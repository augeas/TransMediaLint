FROM python:latest

RUN apt-get clean && apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y --fix-missing install \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

COPY transmedialint/requirements.txt transmedialint/requirements.txt
    
RUN pip3 install -r transmedialint/requirements.txt

ADD transmedialint /transmedialint

WORKDIR /transmedialint