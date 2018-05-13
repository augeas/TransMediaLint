FROM python:latest

RUN apt-get clean && apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y --fix-missing install \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

RUN pip install virtualenv \
    && virtualenv tml

COPY transmedialint/requirements.txt transmedialint/requirements.txt
    
RUN /bin/bash -c "source tml/bin/activate && pip3 install -r transmedialint/requirements.txt && deactivate"

ADD transmedialint /transmedialint

WORKDIR /transmedialint