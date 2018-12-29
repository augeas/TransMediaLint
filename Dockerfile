FROM python:3.6-alpine

RUN apk update \
  && apk add build-base python3-dev jpeg-dev zlib-dev musl-dev openblas-dev freetype-dev pkgconfig gfortran libffi-dev libxml2-dev libxslt-dev postgresql-dev libxml2 libxslt

COPY transmedialint/requirements.txt transmedialint/requirements.txt
    
RUN pip3 install -r transmedialint/requirements.txt

ADD transmedialint /transmedialint

WORKDIR /transmedialint