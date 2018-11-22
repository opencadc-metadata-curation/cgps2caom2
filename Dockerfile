FROM python:3.6-jessie

WORKDIR /usr/src/app

RUN pip install caom2
RUN git clone https://github.com/opencadc-metadata-curation/caom2tools.git && \
  cd caom2tools && git pull origin master && \
  pip install ./caom2utils && pip install ./caom2pipe
RUN pip install git+https://github.com/opencadc-metadata-curation/cgps2caom2.git

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
