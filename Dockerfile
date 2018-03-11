FROM pypy:3-5.9.0

RUN apt-get clean && apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y --fix-missing install \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

RUN pip install virtualenv \
    && virtualenv tml_pypy

COPY transmedialint/pypy_requirements.txt transmedialint/pypy_requirements.txt
    
RUN /bin/bash -c "source tml_pypy/bin/activate && pip3 install -r transmedialint/pypy_requirements.txt && deactivate"

ADD transmedialint /transmedialint

WORKDIR /transmedialint