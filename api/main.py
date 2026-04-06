import os
import shutil
import uuid
import zipfile
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from worker.tasks import protect_images_task
from celery.result import AsyncResult

app = FastAPI(title="CloakAI API", version="0.1.0")

# CORS — restrict origins via env in production
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/cloak_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/protect")
async def protect_images(
    files: List[UploadFile] = File(...),
    mode: str = "low",
    fmt: str = "png",
):
    if mode not in ("low", "mid", "high"):
        raise HTTPException(status_code=400, detail="mode must be low, mid, or high")
    if fmt not in ("png", "jpg"):
        raise HTTPException(status_code=400, detail="format must be png or jpg")

    upload_id = str(uuid.uuid4())
    task_dir = os.path.join(UPLOAD_DIR, upload_id)
    os.makedirs(task_dir, exist_ok=True)

    saved_paths = []
    for file in files:
        safe_name = os.path.basename(file.filename or "upload")
        file_path = os.path.join(task_dir, safe_name)
        with open(file_path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)
        saved_paths.append(file_path)

    task = protect_images_task.delay(saved_paths, mode=mode, fmt=fmt)
    return {"task_id": task.id, "upload_id": upload_id}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }


@app.get("/download/{task_id}")
async def download_results(task_id: str):
    task_result = AsyncResult(task_id)

    if not task_result.ready():
        raise HTTPException(status_code=400, detail="Task not finished yet")

    result = task_result.result
    if not result or result.get("status") != 1:
        raise HTTPException(status_code=400, detail="Protection failed or no result")

    result_paths = result.get("result_paths", [])
    if not result_paths:
        raise HTTPException(status_code=404, detail="No protected images found")

    base_dir = os.path.dirname(result_paths[0])
    zip_path = os.path.join(base_dir, "protected.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in result_paths:
            if os.path.exists(fp):
                zf.write(fp, os.path.basename(fp))

    return FileResponse(zip_path, media_type="application/zip", filename="protected_images.zip")
