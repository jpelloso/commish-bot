FROM python:3.7.4-slim

WORKDIR /app/commish_bot

ADD . /app/commish_bot

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc libc-dev make git libffi-dev python3-dev libxml2-dev libxslt-dev 

RUN pip install -U pip

RUN pip install -r requirements.txt

CMD ["make", "run"]
