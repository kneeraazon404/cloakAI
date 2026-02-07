# CloakAI

CloakAI is an enterprise-grade privacy protection system that applies imperceptible perturbations to face images, rendering them resistant to unauthorized facial recognition systems while preserving visual quality. It is built as a scalable, containerized web application suitable for security-conscious deployments.

---

## Features

- **Privacy-first**: Leverages the Fawkes algorithm to cloak faces against recognition models (e.g., ArcFace-style extractors).
- **Configurable protection**: Modes `low`, `mid`, and `high` trade off visibility of changes vs. strength of protection.
- **Async processing**: FastAPI + Celery + Redis for non-blocking, queue-based workloads.
- **GPU or CPU**: Optional GPU acceleration; falls back to CPU with tunable threading.
- **REST API & docs**: OpenAPI documentation at `/docs`.

---

## System Architecture

| Component    | Technology | Role                                                        |
| ------------ | ---------- | ----------------------------------------------------------- |
| **Frontend** | React      | SPA for upload, mode/format selection, status, and download |
| **API**      | FastAPI    | Upload handling, task enqueue, status, and zip download     |
| **Worker**   | Celery     | Runs the Fawkes protection pipeline (TensorFlow)            |
| **Broker**   | Redis      | Task queue and result backend                               |

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React    │────▶│   FastAPI   │────▶│   Redis    │
│  ( :3000 ) │     │   ( :8000 ) │     │   ( :6379 ) │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐     ┌─────────────┐
                   │   Celery    │◀────│   Worker    │
                   │   Worker    │     │  (Fawkes)   │
                   └─────────────┘     └─────────────┘
```

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) NVIDIA GPU and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU acceleration

### Run

```bash
docker-compose up --build -d
```

- **Web app**: [http://localhost:3000](http://localhost:3000)
- **API docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

```bash
docker-compose logs -f
```

---

## Configuration

### Environment Variables

| Variable                 | Service     | Description                              | Default                    |
| ------------------------ | ----------- | ---------------------------------------- | -------------------------- |
| `REDIS_URL`              | web, worker | Redis connection URL                     | `redis://localhost:6379/0` |
| `REACT_APP_API_URL`      | frontend    | Public API base URL (used at build time) | `http://localhost:8000`    |
| `GPU_ID`                 | worker      | GPU device ID; unset or empty for CPU    | —                          |
| `CLOAK_MODE`             | web         | Default protection mode                  | `low`                      |
| `OMP_NUM_THREADS`        | worker      | OpenMP threads (CPU mode)                | `6`                        |
| `TF_NUM_INTRAOP_THREADS` | worker      | TensorFlow intra-op threads              | `6`                        |
| `TF_NUM_INTEROP_THREADS` | worker      | TensorFlow inter-op threads              | `1`                        |

### Secrets and Credentials

- **Do not commit secrets** (API keys, tokens, passwords, or production URLs) to the repository.
- Use a `.env` file for local overrides; it is in `.gitignore` and must remain untracked.
- Optionally, keep a `.env.example` with placeholder variable names (no real values) and copy it to `.env` for local use.
- In production, use your platform’s secret manager (e.g., Docker secrets, Kubernetes secrets, or a vault) and inject variables at runtime.  
  Example: `REACT_APP_API_URL=https://api.your-domain.com` — replace with your own URL and manage it via secrets, not the repo.

---

## Performance

CloakAI is compute-intensive. Approximate times per image (high protection mode):

| Hardware                       | Time per image | Notes                                        |
| ------------------------------ | -------------- | -------------------------------------------- |
| NVIDIA RTX 3060 / Tesla T4     | ~5–10 s        | NVIDIA Container Toolkit required            |
| Data center GPU (e.g. A100)    | &lt; 2 s       | Best for production                          |
| High-end CPU (e.g. Ryzen 5600) | ~250 s         | Set `OMP_NUM_THREADS` to physical core count |
| Small cloud CPU (2 vCPU)       | &gt; 600 s     | Not recommended for production               |

**AMD GPUs**: Use a `rocm/tensorflow` image and map `/dev/kfd` and `/dev/dri`; otherwise the stack uses CPU.

---

## Production Deployment

### 1. Hardware

- **GPU**: e.g. AWS `g4dn.xlarge`, Azure `Standard_NC4as_T4_v3`, or similar.
- **CPU-only**: e.g. AWS `c5.2xlarge`; tune `OMP_NUM_THREADS` and `TF_*` threads.
- **Storage**: At least 50 GB SSD.

### 2. Host setup

Install Docker, Docker Compose, and (for GPU) NVIDIA drivers and the Container Toolkit. Example (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
# Install NVIDIA drivers and Container Toolkit per NVIDIA docs
```

### 3. Configure and run

1. Clone the repository.
2. Set `REACT_APP_API_URL` to your public API URL (e.g. `https://api.your-domain.com`). Prefer build-time injection or a runtime config; keep the value out of the repo.
3. Run with the production stack:

   ```bash
   docker-compose -f deployment/docker-compose.prod.yml up --build -d
   ```

### 4. Reverse proxy and TLS

Do not expose `3000` or `8000` directly. Put Nginx (or another reverse proxy) in front and use TLS (e.g. Let’s Encrypt/Certbot).

Example Nginx site (replace `your-domain.com` and paths as needed):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://web:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Security

- **Data**: Images are stored under `/tmp/cloak_uploads` by default. For stricter compliance, use a dedicated, encrypted volume or object storage (e.g. S3) and define retention and deletion policies.
- **Access control**: The default API is open. For production, add authentication (e.g. OAuth2, API keys) in `backend/api/main.py` or at the reverse proxy.
- **Secrets**: Keep all credentials and production URLs in `.env` (local, gitignored) or in a secret manager; never commit them.

---

## Project layout

```
├── backend/
│   ├── api/           # FastAPI app
│   ├── worker/         # Celery tasks
│   ├── core/          # Fawkes algorithm (fawkes)
│   └── config.py      # Celery/Redis config
├── frontend/          # React SPA
├── deployment/        # Prod compose, Nginx, checklist
└── docker-compose.yml
```

---

## License

BSD-3-Clause (derived from the Fawkes project; see [LICENSE](LICENSE)).
