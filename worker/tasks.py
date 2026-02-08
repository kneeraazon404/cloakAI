# cloud_app/worker.py
import os
import logging
from celery import Celery
from fawkes.protection import Fawkes
import backend.config as celery_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery('cloak_worker')
app.config_from_object(celery_config)

# Global Engine instance (lazy loading)
privacy_engine = None

def get_engine_instance(mode="low"):
    global privacy_engine
    
    # Check if we need to (re)initialize
    should_init = False
    if privacy_engine is None:
        should_init = True
    elif privacy_engine.mode != mode:
        logger.info(f"Switching mode from {privacy_engine.mode} to {mode}")
        should_init = True
        
    if should_init:
        # Check for GPU
        gpu_id = os.getenv("GPU_ID", None)
        
        logger.info(f"Initializing CloakAI Engine with GPU={gpu_id}, Mode={mode}")
        # Using the core Fawkes library for protection
        privacy_engine = Fawkes("extractor_2", gpu_id, batch_size=1, mode=mode)
        
    return privacy_engine

@app.task(bind=True)
def protect_images_task(self, image_paths, mode="low"):
    """
    Celery task to run CloakAI protection on a list of images.
    """
    logger.info(f"Starting protection task for {len(image_paths)} images. Mode: {mode}")
    
    protector = get_engine_instance(mode)
    
    # Run protection
    # Note: run_protection returns status codes: 1=Success, 2=No Face, 3=No Images
    # We might need to adapt this depending on how run_protection handles file outputs
    # Currently it saves "_cloaked" files in the same directory.
    
    import time
    import traceback
    start_time = time.time()
    
    try:
        status = protector.run_protection(
            image_paths, 
            debug=True,
            format='png'
        )
    except Exception as e:
        logger.error(f"Protection failed: {e}")
        traceback.print_exc()
        return {
            "status": "FAILURE",
            "error": str(e),
            "result_paths": [],
            "elapsed_time": round(time.time() - start_time, 2)
        }
    
    elapsed_time = time.time() - start_time
    
    result_paths = []
    if status == 1:
        for path in image_paths:
            base, ext = os.path.splitext(path)
            # Fawkes default naming convention:
            cloaked_path = f"{base}_cloaked.png"
            if os.path.exists(cloaked_path):
                result_paths.append(cloaked_path)
    
    return {
        "status": status,
        "result_paths": result_paths,
        "elapsed_time": round(elapsed_time, 2)
    }
