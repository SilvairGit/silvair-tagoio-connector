FROM python:3.8-slim

COPY ./.pip-pin/install.txt /
COPY ./.pip-pin/constraints.txt /

RUN pip install -r /install.txt -c constraints.txt

COPY . /src
WORKDIR /src

RUN pip install -e /src
