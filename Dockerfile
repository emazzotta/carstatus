FROM python:3.7-alpine3.8

LABEL maintainer="hello@mazzotta.me"

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY src /app/src

CMD ["python", "src/carstatus.py"]
