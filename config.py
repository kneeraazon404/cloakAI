# cloud_app/celery_config.py
import os

# Redis connection URL
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

broker_url = redis_url
result_backend = redis_url

# Serialization settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True
