FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && \
    apt-get install curl python3-pip -y && \
    pip3 install -r requirements.txt --no-cache-dir
COPY . ./
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
