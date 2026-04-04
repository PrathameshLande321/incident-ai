FROM python:3.10-slim

WORKDIR /app

# Prevent python buffering (IMPORTANT for logs)
ENV PYTHONUNBUFFERED=1

COPY . .

# Install system deps (only if really needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Debug: show files (helps confirm correct structure)
RUN ls -la

EXPOSE 7860

# Use explicit python -m (more reliable than direct uvicorn)
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]