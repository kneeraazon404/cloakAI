# CloakAI

**CloakAI** is an enterprise-grade privacy protection system designed to cloak images against unauthorized facial recognition models. It is built as a scalable, containerized web application suitable for high-security environments.

---

## 🏗 System Architecture

The system follows a microservices architecture:

*   **Frontend**: React SPA (Single Page Application) with a premium dark-mode interface.
*   **API Gateway**: FastAPI (Python) handling secure uploads, validated requests.
*   **Worker Nodes**: Celery workers performing the GPU-accelerated *CloakAI* algorithm.
*   **Message Broker**: Redis for task queuing.

---
## ⚡ Performance & Hardware Optimization

The CloakAI algorithm is computationally intensive. Performance varies significantly between CPU and GPU execution.

### Benchmarks (High Protection Mode)
| Hardware | Avg. Time per Image | Optimization Note |
|:---|:---:|:---|
| **NVIDIA RTX 3060 / Tesla T4** | **~5-10s** | Requires NVIDIA Drivers + Container Toolkit |
| **Data Center GPU (A100)** | **< 2s** | Enterprise grade performance |
| **High-End CPU (e.g. Ryzen 5600)** | **~250s** | Set `OMP_NUM_THREADS` to physical core count |
| **Standard Cloud CPU (2 vCPU)** | **> 600s** | Not recommended for production |

> **Note for AMD GPU Users**: To utilize AMD GPUs (e.g., RX 6700 XT), the backend Docker image must be swapped for `rocm/tensorflow` and configured with device mapping (`/dev/kfd`, `/dev/dri`). By default, the system falls back to CPU on non-NVIDIA hardware.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
*   Docker & Docker Compose
*   (Optional) NVIDIA GPU + Container Toolkit

### Running the App
1.  **Start Services**:
    ```bash
    docker-compose up --build -d
    ```
    *Builds may take a few minutes initially.*

2.  **Access Interfaces**:
    *   **Web App**: [http://localhost:3000](http://localhost:3000)
    *   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

3.  **Logs**:
    ```bash
    docker-compose logs -f
    ```

---

## ☁️ Production Deployment Guide

This section outlines deploying Fawkes Cloud to a production environment like AWS EC2, Azure VM, or Google Compute Engine.

### 1. Hardware Requirements
*   **Instance Type**:
    *   **AWS**: `g4dn.xlarge` (Recommended for GPU) or `c5.2xlarge` (CPU only).
    *   **Azure**: `Standard_NC4as_T4_v3`.
*   **Storage**: At least 50GB SSD.

### 2. Setup Host Machine
Install Docker and NVIDIA Drivers (if using GPU).
```bash
# Example for Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
# Follow NVIDIA docs for Container Toolkit
```

### 3. Deploy Application
1.  Clone this repository to the server.
2.  Configuration:
    *   Set `REACT_APP_API_URL` in `docker-compose.yml` to your server's public IP or Domain (e.g., `http://api.yourdomain.com`).
    *   Ideally, serve the frontend via Nginx mostly statically, but the Docker composition handles dev-server for simplicity. Use `npm run build` for true production assets.

3.  Run in production mode:
    ```bash
    sudo docker-compose up --build -d
    ```

### 4. Reverse Proxy & SSL (Recommended)
Do not expose ports 3000/8000 directly. Use Nginx with Let's Encrypt / Certbot.

**Sample Nginx Config:**
```nginx
server {
    listen 80;
    server_name fawkes.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api/ {
        proxy_pass http://localhost:8000/; # Trailing slash strips /api
        proxy_set_header Host $host;
    }
}
```

---

## 🔒 Security Notes
*   **Data Privacy**: Images are stored in `/tmp` by default. For compliance, configure a secure S3 bucket or ensure the temporary volume is encrypted and auto-cleaned.
*   **Authentication**: This version is open access. Implement OAuth2 middleware in `backend/api/main.py` for user access control.

## 🛠 Directory Structure
```text
/
├── backend/            # Python Services
│   ├── api/            # FastAPI Endpoints
│   ├── worker/         # Protection Logic (Celery)
│   ├── core/           # Fawkes Algorithm Library
│   └── config.py       # Configuration
├── frontend/           # React Web Application
├── deployment/         # Deployment Assets
└── docker-compose.yml  # Orchestration
```

---

**License**: MIT / BSD-3 (Inherited from Fawkes Project)
