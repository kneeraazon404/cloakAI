# CloakAI Backend

This is the backend repository for the CloakAI privacy protection system. It provides the API, Celery workers, and Fawkes implementation.

---

## Features

- **FastAPI**: High-performance async API.
- **Celery + Redis**: Asynchronous task queue for image processing.
- **Fawkes Algorithm**: Image perturbation for privacy protection.
- **Dockerized**: specific `Dockerfile` for easy deployment.

---

## Tech Stack

- **Python 3.9+**
- **FastAPI**
- **Celery**
- **TensorFlow** (for Fawkes)
- **Redis**

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) NVIDIA GPU for acceleration

### Run with Docker Compose

```bash
docker-compose up --build -d
```

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Deployment

This branch is structured for backend deployment.

- **API**: Deploy `api/` or root `Dockerfile` to a container service (AWS ECS, Google Cloud Run, DigitalOcean App Platform).
- **Worker**: Deploy the worker process using the same image but with a different command (e.g., `celery -A worker.celery_app worker`).
- **Redis**: Use a managed Redis instance.

---

## Environment Variables

See `.env.example` (if available) or the table below:

| Variable    | Default                    | Description                          |
| :---------- | :------------------------- | :----------------------------------- |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string              |
| `GPU_ID`    | (empty)                    | Set to specific GPU ID if using CUDA |

---

## License

BSD-3-Clause
