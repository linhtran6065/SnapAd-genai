from model.model import Model
from model.helpers import b64_to_pil
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from helpers import handle_gen_video_request, upload_image_to_firebase, delete_file_in_folder, b64_to_video, check_file_exists_firebase, get_firebase_blob_url
import os
import uuid
from typing import Dict
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CACHE_DIR = "cache"
FIREBASE_OUTPUT_DIR = "output"

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Load ComfyUI
VI_MODEL = Model(port=8189)
VI_MODEL.load(ui_workflow="video_gen_workflow_api.json")

# Initialize FastAPI app
app = FastAPI()

# Job storage to track job statuses
job_status_store: Dict[str, Dict] = {}

def get_file_path(job_id: str) -> str:
    return os.path.join(CACHE_DIR, f"{job_id}.mp4")

def process_video_job(job_id: str, gen_video_request: dict):
    try:
        gen_video_values = handle_gen_video_request(gen_video_request)
        video_b64 = VI_MODEL.predict(gen_video_values)['result'][-1]['data']

        # Save the video in cache directory using job_id as filename
        file_path = get_file_path(job_id)
        b64_to_video(video_b64, file_path)

        # Upload to Firebase using job_id as filename
        firebase_path = f"{FIREBASE_OUTPUT_DIR}/{job_id}.mp4"
        result_link = upload_image_to_firebase(file_path, firebase_path)

        job_status_store[job_id].update({
            "status": "completed",
            "result": result_link
        })

        # Clean up cache directory
        if os.path.exists("data/ComfyUI/output/"):
            delete_file_in_folder("data/ComfyUI/output/")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job_status_store[job_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.post("/gen-video/jobs", status_code=201)
async def create_video_job(
    background_tasks: BackgroundTasks,
    product_image: UploadFile = File(...),
    prompt: str = Form(...),
):
    job_id = str(uuid.uuid4())
    logger.info(f"Creating new video job {job_id}")

    job_status_store[job_id] = {
        "status": "processing",
        "result": None,
        "error": None
    }

    image_data = await product_image.read()
    gen_video_request = {
        "product_image_data": image_data,
        "prompt": prompt,
    }

    background_tasks.add_task(process_video_job, job_id, gen_video_request)
    return {"job_id": job_id, "status": "processing"}

@app.get("/gen-video/jobs/{job_id}/status", status_code=200)
async def get_video_job_status(job_id: str):
    # Check if job exists in memory
    if job_id not in job_status_store:
        firebase_path = f"{FIREBASE_OUTPUT_DIR}/{job_id}.mp4"
        if check_file_exists_firebase(firebase_path):
            result_link = get_firebase_blob_url(firebase_path)
            
            job_status_store[job_id] = {
                "status": "completed",
                "result": result_link,
                "error": None
            }
        else:
            raise HTTPException(status_code=404, detail="Job not found")

    job_status = job_status_store[job_id]
    if job_status["status"] in ["failed", "processing"]:
        file_path = get_file_path(job_id)
        if os.path.exists(file_path):
            firebase_path = f"{FIREBASE_OUTPUT_DIR}/{job_id}.mp4"
            try:
                result_link = upload_image_to_firebase(file_path, firebase_path)
                job_status.update({
                    "status": "completed",
                    "result": result_link,
                    "error": None
                })
            except Exception as e:
                logger.error(f"Failed to reprocess job {job_id}: {str(e)}")

    return job_status

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Cleanup handler
def cleanup_cache():
    if os.path.exists(CACHE_DIR):
        for file in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, file)
            if os.path.isfile(file_path):
                # Keep files newer than 24 hours
                if time.time() - os.path.getmtime(file_path) > 86400:
                    os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    # Run cleanup on startup
    cleanup_cache()
    uvicorn.run(app, host="0.0.0.0", port=1403)
