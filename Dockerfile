FROM pypy:latest

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
RUN /bin/bash -c 'source tml_pypy/bin/activate &&  python -c "import nltk; nltk.download('"'punkt'"'); nltk.download('"'stopwords'"')" && deactivate'

ADD transmedialint /transmedialint

WORKDIR /transmedialint