# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY main.py config.py ./
COPY utils/ utils/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/static/ static/

# Create directories for runtime data (used in local mode only)
RUN mkdir -p data uploads

# Default port for Cloud Run
ENV PORT=8080
# Production mode: Firestore + GCS + Firebase Auth
ENV ENV_MODE=production

EXPOSE 8080

CMD ["python", "main.py"]
