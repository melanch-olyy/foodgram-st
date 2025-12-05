FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
