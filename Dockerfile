
FROM pypy:3-5.9.0

RUN pip install virtualenv

RUN virtualenv tml_pypy

COPY transmedialint/pypy_requirements.txt transmedialint/pypy_requirements.txt

RUN apt-get clean && apt-get -q -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -q -y --fix-missing install \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev
    
RUN /bin/bash -c "source tml_pypy/bin/activate && pip3 install -r transmedialint/pypy_requirements.txt && deactivate"

ADD transmedialint /transmedialint

WORKDIR /transmedialint