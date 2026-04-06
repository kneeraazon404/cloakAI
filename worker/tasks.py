import logging
import os
import time
import traceback

from celery import Celery
from fawkes.protection import Fawkes
import config as celery_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery("cloak_worker")
app.config_from_object(celery_config)

_engine: Fawkes | None = None
_engine_mode: str | None = None


def get_engine(mode: str) -> Fawkes:
    global _engine, _engine_mode
    if _engine is None or _engine_mode != mode:
        gpu_id = os.getenv("GPU_ID", None)
        logger.info(f"Initialising Fawkes engine — mode={mode}, gpu={gpu_id}")
        _engine = Fawkes("extractor_2", gpu_id, batch_size=1, mode=mode)
        _engine_mode = mode
    return _engine


@app.task(bind=True)
def protect_images_task(self, image_paths: list, mode: str = "low", fmt: str = "png"):
    logger.info(f"Task started — {len(image_paths)} image(s), mode={mode}, fmt={fmt}")

    # Fawkes accepts 'jpeg' not 'jpg'
    output_fmt = "jpeg" if fmt == "jpg" else fmt

    engine = get_engine(mode)
    start = time.time()

    try:
        status = engine.run_protection(image_paths, debug=True, format=output_fmt)
    except Exception as exc:
        logger.error(f"Protection failed: {exc}")
        traceback.print_exc()
        return {
            "status": "FAILURE",
            "error": str(exc),
            "result_paths": [],
            "elapsed_time": round(time.time() - start, 2),
        }

    elapsed = round(time.time() - start, 2)
    result_paths = []

    if status == 1:
        for path in image_paths:
            base = ".".join(path.split(".")[:-1])
            cloaked = f"{base}_cloaked.{output_fmt}"
            if os.path.exists(cloaked):
                result_paths.append(cloaked)

    return {
        "status": status,
        "result_paths": result_paths,
        "elapsed_time": elapsed,
    }
