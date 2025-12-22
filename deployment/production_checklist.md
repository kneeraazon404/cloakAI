# CloakAI Production Checklist

## 1. System Cleanup
Remove legacy development artifacts to ensure a clean deployment environment.
```bash
# Remove artifacts created by previous Docker runs (requires sudo)
sudo rm -rf cloud_app
sudo rm -rf imgs tmp_data
sudo find . -type d -name "__pycache__" -exec rm -rf {} +
```

## 2. Environment Configuration
Verify your `docker-compose.prod.yml` and environment variables.
*   [ ] **API URL**: Ensure `REACT_APP_API_URL` points to your public domain/IP.
*   [ ] **Security**: Change default passwords for Redis (if exposed) or secure via firewall.
*   [ ] **SSL**: Configure Nginx with SSL certificates (Certbot).

## 3. Performance Tuning (CPU Mode)
If running on CPU (e.g. Ryzen 5600), ensure optimization flags are set in `docker-compose.yml`:
```yaml
environment:
  - OMP_NUM_THREADS=6  # Set to physical core count
  - TF_NUM_INTRAOP_THREADS=6
```

## 4. Final Build & Deploy
Execute the final build to apply all dependencies and optimizations.
```bash
# Development
sudo docker-compose up --build -d

# Production
sudo docker-compose -f deployment/docker-compose.prod.yml up --build -d
```

## 5. Verification
*   **Access**: http://localhost:3000 (or your domain)
*   **Test**: Upload an image in "Low" or "Mid" mode.
*   **Validate**: Download result and ensure "Cloaked" artifacts are generated.
