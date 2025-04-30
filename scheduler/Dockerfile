FROM python:3.11-slim

WORKDIR /app

COPY scheduler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scheduler/ .
CMD ["python", "ping_latest_news.py"]
