FROM python:3.11-slim
WORKDIR /app
COPY requirements.lock requirements.in ./
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
CMD ["python", "-m", "src.ui"]