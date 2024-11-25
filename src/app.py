from model.model import Model
from model.helpers import b64_to_pil
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from helpers import handle_gen_image_request, upload_image_to_firebase, delete_file_in_folder
import os
import uuid
from typing import Dict
import time

# Load ComfyUI
IM_MODEL = Model(port=8188)
IM_MODEL.load(ui_workflow="image_gen_workflow_api.json")

# Initialize FastAPI app
app = FastAPI()

# Job storage to track job statuses
job_status_store: Dict[str, Dict] = {}

def process_image_job(job_id: str, gen_image_request: dict):
    try:
        # Call the model and generate the image
        gen_image_values = handle_gen_image_request(gen_image_request)
        image_b64 = IM_MODEL.predict(gen_image_values)['result'][-1]['data']

        # Save the image locally
        file_path = f"{gen_image_request['save_id']}.jpg"
        b64_to_pil(image_b64).save(file_path)

        # Upload the image to Firebase
        result_link = upload_image_to_firebase(file_path, f"output/{file_path}")

        # Update job status
        job_status_store[job_id]["status"] = "completed"
        job_status_store[job_id]["result"] = result_link

        # Cleanup temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("data/ComfyUI/output/"):
            delete_file_in_folder("data/ComfyUI/output/")
    except Exception as e:
        # Handle errors and update job status
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
    startTime = time.time()
    print(f"Received request for prompt: {prompt}, light_type: {light_type}, object_keyword: {object_keyword}, save_id: {save_id}")
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save initial job status
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

    print(f"Time taken: {time.time() - startTime} for job_id: {job_id}")
    # Return the job ID immediately
    return {"job_id": job_id, "status": "processing"}

@app.get("/gen-image/jobs/{job_id}/status", status_code=200)
async def get_image_job_status(job_id: str):
    startTime = time.time()
    # Check if job exists
    if job_id not in job_status_store:
        print(f"Time taken: {time.time() - startTime}")
        raise HTTPException(status_code=404, detail="Job not found")

    # Return the current status of the job
    data = job_status_store[job_id]
    print(f"Time taken: {time.time() - startTime} for job_id: {job_id} and status: {data['status']}")
    return data

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1403)
