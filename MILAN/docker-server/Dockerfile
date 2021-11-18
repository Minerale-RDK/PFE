FROM python:alpine

RUN apk update
RUN apk add build-base libffi-dev libc-dev
RUN pip install --no-cache-dir asyncua

COPY server-minimal.py server-minimal.py
CMD python3 server-minimal.py
