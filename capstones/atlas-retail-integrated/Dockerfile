FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY logic.py storage.py app.py ./
COPY data/events.json ./data/events.json
RUN useradd -r -u 11001 atlas
USER atlas
ENTRYPOINT ["python", "/app/app.py"]
