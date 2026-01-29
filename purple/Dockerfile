
FROM docker.1ms.run/python:3-slim

RUN apt-get update && apt-get install -y curl netcat-openbsd && rm -rf /var/lib/apt/lists/*


ENV PYTHONDONTWRITEBYTECODE=1


ENV PYTHONUNBUFFERED=1


RUN python -m pip install --upgrade pip \
    && pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/


COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0"]
EXPOSE 9010