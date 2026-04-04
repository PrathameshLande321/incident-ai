FROM python:3.10-slim

WORKDIR /app

COPY . .


RUN pip install --upgrade pip


RUN pip install --no-cache-dir -r requirements.txt

# Optional but safer (some libs need it)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 7860


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]