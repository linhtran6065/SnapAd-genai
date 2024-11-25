from fastapi import FastAPI, Form, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from threading import Lock
import logging
import os
import uuid
from typing import Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadSafeJobStore:
    def __init__(self):
        self._store: Dict[str, Dict] = {}
        self._lock = Lock()

    def add_job(self, job_id: str, status: Dict) -> None:
        if not job_id:
            raise ValueError("Job ID cannot be null")
            
        with self._lock:
            self._store[job_id] = {
                **status,
                "created_at": datetime.utcnow().isoformat()
            }

    def get_job(self, job_id: str) -> Optional[Dict]:
        if not job_id:
            return None
            
        with self._lock:
            return self._store.get(job_id)

    def update_job(self, job_id: str, updates: Dict) -> None:
        if not job_id:
            return
            
        with self._lock:
            if job_id in self._store:
                self._store[job_id].update(updates)

# Initialize FastAPI app and job store
app = FastAPI()
job_store = ThreadSafeJobStore()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"Processing request {request_id}")
    response = await call_next(request)
    return response

def process_image_job(job_id: str, gen_image_request: dict):
    try:
        logger.info(f"Processing job {job_id}")
        gen_image_values = handle_gen_image_request(gen_image_request)
        image_b64 = IM_MODEL.predict(gen_image_values)['result'][-1]['data']

        file_path = f"{gen_image_request['save_id']}.jpg"
        b64_to_pil(image_b64).save(file_path)

        result_link = upload_image_to_firebase(file_path, f"output/{file_path}")

        job_store.update_job(job_id, {
            "status": "completed",
            "result": result_link
        })

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("data/ComfyUI/output/"):
            delete_file_in_folder("data/ComfyUI/output/")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job_store.update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })

@app.post("/gen-image/jobs", status_code=201)
async def create_image_job(
    request: Request,
    background_tasks: BackgroundTasks,
    product_image: UploadFile = File(...),
    prompt: str = Form(...),
    light_type: str = Form(...),
    object_keyword: str = Form(...),
    save_id: str = Form(...)
):
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job {job_id} for request {request.state.request_id}")

        job_store.add_job(job_id, {
            "status": "processing",
            "result": None,
            "error": None
        })

        image_data = await product_image.read()
        gen_image_request = {
            "product_image_data": image_data,
            "prompt": prompt,
            "light_type": light_type,
            "object_keyword": object_keyword,
            "save_id": save_id,
        }

        background_tasks.add_task(process_image_job, job_id, gen_image_request)
        return {"job_id": job_id, "status": "processing"}
    except Exception as e:
        logger.error(f"Failed to create job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job")

@app.get("/gen-image/jobs/{job_id}/status", status_code=200)
async def get_image_job_status(job_id: str, request: Request):
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required")

    job_status = job_store.get_job(job_id)
    if not job_status:
        logger.warning(f"Job {job_id} not found for request {request.state.request_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    return job_status