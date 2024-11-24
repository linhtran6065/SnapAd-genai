from model.model import Model
from model.helpers import b64_to_pil
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from helpers import handle_gen_image_request, upload_image_to_firebase, delete_file_in_folder
import os
import uuid
from typing import Dict
import logging
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load ComfyUI
try:
    IM_MODEL = Model(port=8188)
    IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load the model: {e}")
    raise

# Initialize FastAPI app
app = FastAPI()

# Thread-safe job storage to track job statuses
job_status_store: Dict[str, Dict] = {}
store_lock = Lock()

def process_image_job(job_id: str, gen_image_request: dict):
    try:
        logging.debug(f"Processing job: {job_id} with request: {gen_image_request}")

        # Call the model and generate the image
        gen_image_values = handle_gen_image_request(gen_image_request)
        image_b64 = IM_MODEL.predict(gen_image_values)['result'][-1]['data']

        # Save the image locally
        file_path = f"{gen_image_request['save_id']}.jpg"
        b64_to_pil(image_b64).save(file_path)

        # Upload the image to Firebase
        result_link = upload_image_to_firebase(file_path, f"output/{file_path}")

        # Update job status
        with store_lock:
            job_status_store[job_id]["status"] = "completed"
            job_status_store[job_id]["result"] = result_link

        # Cleanup temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("data/ComfyUI/output/"):
            delete_file_in_folder("data/ComfyUI/output/")
    except Exception as e:
        logging.error(f"Error processing job {job_id}: {e}")
        with store_lock:
            job_status_store[job_id]["status"] = "failed"
            job_status_store[job_id]["error"] = str(e)

@app.post("/gen-image/jobs", status_code=201)
async def create_image_job(
    background_tasks: BackgroundTasks,
    product_image: UploadFile = File(...),
    prompt: str = Form(...),
    light_type: str = Form(...),
    object_keyword: str = Form(...),
    save_id: str = Form(...)
):
    # Validate inputs
    if not all([prompt, light_type, object_keyword, save_id]):
        logging.warning("Missing required form fields.")
        raise HTTPException(status_code=400, detail="Missing required form fields")

    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        logging.info(f"Generated job_id: {job_id}")

        # Save initial job status in a thread-safe manner
        with store_lock:
            job_status_store[job_id] = {
                "status": "processing",
                "result": None,
                "error": None
            }

        # Read the uploaded image
        image_data = await product_image.read()
        gen_image_request = {
            "product_image_data": image_data,
            "prompt": prompt,
            "light_type": light_type,
            "object_keyword": object_keyword,
            "save_id": save_id,
        }

        # Add the job to the background tasks
        background_tasks.add_task(process_image_job, job_id, gen_image_request)

        # Return the job ID immediately
        return {"job_id": job_id, "status": "processing"}
    except Exception as e:
        logging.error(f"Failed to create image job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job")

@app.get("/gen-image/jobs/{job_id}/status", status_code=200)
async def get_image_job_status(job_id: str):
    # Check if job exists in a thread-safe manner
    with store_lock:
        if job_id not in job_status_store:
            logging.warning(f"Job {job_id} not found.")
            raise HTTPException(status_code=404, detail="Job not found")

        # Return the current status of the job
        logging.debug(f"Status of job {job_id}: {job_status_store[job_id]}")
        return job_status_store[job_id]

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1403)
