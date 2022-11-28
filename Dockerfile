FROM python:3.9.13
RUN pip3 install -U pipenv
RUN curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm
RUN curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer
COPY . /app
WORKDIR /app
RUN pipenv install --system --deploy --ignore-pipfile
ENTRYPOINT ["/bin/sh", "run.sh"]
