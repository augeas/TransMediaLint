FROM frolvlad/alpine-python-machinelearning


COPY transmedialint/requirements.txt transmedialint/requirements.txt

RUN apk update \
    && apk add --virtual build-deps python3-dev gcc g++ gfortran musl-dev libffi-dev libxml2-dev postgresql-dev libxslt-dev jpeg-dev zlib-dev freetype-dev pkgconfig \
    && apk add bash curl libstdc++ libxml2 libxslt libffi libpq libjpeg-turbo \
    && pip install -r transmedialint/requirements.txt \
    && python -m spacy download en_core_web_sm \
    && apk del build-deps
    
ADD transmedialint /transmedialint

WORKDIR /transmedialint

RUN python setup.py sdist && python setup.py install

#ENTRYPOINT ["/transmedialint/run.sh"]
