# Base image
FROM python:3.9-slim

# Copy alle filer i den mappe hvor min Dockerfile er til /app mappen i mit image
COPY . /app

# Skift til mappen /app (svarer til CD kommandoen)
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]