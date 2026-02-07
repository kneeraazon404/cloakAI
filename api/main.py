# cloud_app/api.py
import os
import shutil
import uuid
import zipfile
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.worker.tasks import protect_images_task
from celery.result import AsyncResult

app = FastAPI(title="CloakAI API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/cloak_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/protect")
async def protect_images(files: List[UploadFile] = File(...), mode: str = "low"):
    """
    Upload images and start protection task.
    """
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(UPLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    saved_paths = []
    
    for file in files:
        file_path = os.path.join(task_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)
    
    # Trigger Celery task
    task = protect_images_task.delay(saved_paths, mode=mode)
    
    return {"task_id": task.id, "upload_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Check the status of a protection task.
    """
    task_result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return response

@app.get("/download/{task_id}")
async def download_results(task_id: str):
    """
    Download the protected images as a ZIP file.
    """
    task_result = AsyncResult(task_id)
    
    if not task_result.ready():
        raise HTTPException(status_code=400, detail="Task not finished yet")
    
    result = task_result.result
    if not result or result.get("status") != 1:
         raise HTTPException(status_code=400, detail="Protection failed or no result")
         
    result_paths = result.get("result_paths", [])
    if not result_paths:
        raise HTTPException(status_code=404, detail="No protected images found")

    # Create a zip file
    # We assume all files are in the same directory (the upload_id directory, 
    # but we only have task_id here. 
    # Wait, in this simple design task_id == celery_task_id. 
    # But the files are stored in a dir keyed by our generated UUID?
    # Actually, let's look at `protect_images`: 
    # `task = protect_images_task.delay(...)`. Celery generates its own ID.
    # The return value uses `task.id`. 
    # The files are stored in `UPLOAD_DIR/task_id` (where task_id was our UUID).
    
    # Correction: The celery task ID is different from the upload folder ID (which I called task_id in the upload logic).
    # I should pass the upload_id (folder name) to the task result or structure to find it back easily.
    # OR, simplified: simple use celery task ID as the reference, but storing files *before* we have IT is hard.
    # Current code returns: `{"task_id": task.id, "upload_id": task_id}`
    # The client needs to request download using... `task_id`.
    # But files are at `UPLOAD_DIR/upload_id`.
     
    # Let's fix this in the `protect_images` endpoint logic or Client logic.
    # Better: The Worker knows the paths. The Paths are absolute.
    # So `result_paths` contains absolute paths.
    
    # We can just zip those specific paths.
    
    base_dir = os.path.dirname(result_paths[0])
    zip_filename = f"{base_dir}/protected.zip"
    
    # Always create/overwrite zip to ensure freshness
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in result_paths:
            if os.path.exists(file_path):
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
            else:
                print(f"Warning: File not found {file_path}")
                
    return FileResponse(zip_filename, media_type='application/zip', filename="protected_images.zip")
