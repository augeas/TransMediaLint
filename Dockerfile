FROM python:3.9-slim


COPY transmedialint/requirements.txt transmedialint/requirements.txt

RUN pip install -r transmedialint/requirements.txt
RUN python -m spacy download en_core_web_sm
RUN apt update -y && apt install -y curl dnsutils zip
    
ADD transmedialint /transmedialint

WORKDIR /transmedialint

RUN python setup.py sdist && python setup.py install

#ENTRYPOINT ["/transmedialint/run.sh"]
