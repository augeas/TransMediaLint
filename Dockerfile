FROM python:3.6-alpine

COPY transmedialint/requirements.txt transmedialint/requirements.txt

RUN apk update \
    && apk add --virtual build-deps python3-dev gcc g++ gfortran musl-dev lapack-dev libffi-dev libxml2-dev postgresql-dev libxslt-dev jpeg-dev zlib-dev freetype-dev pkgconfig \
    && apk add bash lapack libstdc++ libxml2 libxslt libffi \
    && pip3 install -r transmedialint/requirements.txt \
    && apk del build-deps
    
ADD transmedialint /transmedialint

WORKDIR /transmedialint

