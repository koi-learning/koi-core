FROM python:3.8-alpine
COPY . /src
RUN pip install ./src