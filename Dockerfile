# Base image
FROM python:3.9-slim

# Skift til mappen /app (svarer til CD kommandoen)
WORKDIR /app

# Copy alle filer i den mappe hvor min Dockerfile er til /app mappen i mit image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py","gunicorn", "--bind", "0.0.0.0:80", "app:app"]