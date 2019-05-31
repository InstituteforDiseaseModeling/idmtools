FROM python:3.7.2
WORKDIR /app
ENV PYTHONPATH=/app:${PYTHONPATH}

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt