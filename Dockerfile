FROM python:3.15.2-alpine3.24

LABEL maintainer="hello@mazzotta.me"

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY src /app/src

CMD ["python", "src/carstatus.py"]
