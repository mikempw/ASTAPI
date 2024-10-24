FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Create directory for config file
RUN mkdir -p /config

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
