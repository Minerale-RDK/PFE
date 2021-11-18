FROM python:alpine

RUN apk update
RUN apk add build-base libffi-dev libc-dev
RUN pip install --no-cache-dir asyncua

COPY client-minimal.py client-minimal.py
CMD python3 client-minimal.py

