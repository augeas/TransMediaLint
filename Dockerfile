FROM python:3.12-slim-bookworm

COPY transmedialint/requirements.txt transmedialint/requirements.txt

RUN apt update -y && apt install -y curl dnsutils zip
RUN pip install uv 
RUN uv pip install --system -r transmedialint/requirements.txt
RUN python -m spacy download en_core_web_sm
RUN playwright install-deps && playwright install firefox && playwright install chromium
    
ADD transmedialint /transmedialint

WORKDIR /transmedialint

RUN python setup.py sdist && python setup.py install

#ENTRYPOINT ["/transmedialint/run.sh"]
