FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 COPY EVERYTHING (not src)
COPY . .

# 👇 Render listens on 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
