# CloakAI — AI Image Security Platform

Protect your images from unauthorized AI training and facial recognition using adversarial cloaking.

---

## Architecture

```
Frontend (Next.js) ──→ Backend API (FastAPI)
                              │
                         Celery Worker
                              │
                        Redis (broker)
                              │
                       Fawkes Core (TF)
```

- **Frontend**: Next.js 16, React 19 — deployed independently on Vercel
- **API**: FastAPI + Uvicorn — stateless HTTP server
- **Worker**: Celery — async image processing queue
- **Broker/Cache**: Redis
- **Engine**: Fawkes (adversarial perturbation via TensorFlow)

---

## Frontend (Vercel)

The frontend is a fully standalone Next.js app. It communicates with the backend only via `NEXT_PUBLIC_API_URL`. If the variable is unset it falls back to `http://localhost:8000`.

### Deploy to Vercel

1. Connect this repository to a Vercel project.
2. Set root directory to `/` (repo root).
3. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url
   NEXT_PUBLIC_SITE_URL=https://your-vercel-url
   ```
4. Deploy — Vercel auto-detects Next.js.

### Local development

```bash
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev                         # http://localhost:3000
```

---

## Backend (Docker)

The backend requires Redis and a machine capable of running TensorFlow (GPU recommended for `mid`/`high` modes).

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |
| `GPU_ID` | `None` | GPU device ID (leave unset for CPU) |

### Run with Docker Compose

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      REDIS_URL: redis://redis:6379/0
      ALLOWED_ORIGINS: https://your-vercel-url
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A worker.tasks worker --loglevel=info
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis
```

```bash
docker compose up
```

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/protect?mode=low&fmt=png` | Upload images, start task |
| `GET` | `/status/{task_id}` | Poll task status |
| `GET` | `/download/{task_id}` | Download protected ZIP |

**Protection modes**: `low` (fast), `mid` (balanced), `high` (strongest)
**Output formats**: `png`, `jpg`

---

## Protection Modes

| Mode | Steps | Strength | Speed |
|---|---|---|---|
| `low` | 40 | Standard | ~20s/img |
| `mid` | 75 | Enhanced | ~45s/img |
| `high` | 150 | Maximum | ~90s/img |

---

## License

BSD-3-Clause
