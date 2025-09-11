FROM python:3.10-slim

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
