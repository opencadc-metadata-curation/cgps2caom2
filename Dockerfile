FROM python:3.6-jessie

WORKDIR /usr/src/app

RUN pip install caom2 && \
    pip install caom2utils

RUN git clone https://github.com/opencadc-metadata-curation/caom2pipe.git && \
  git pull origin master && pip install ./caom2pipe
  
RUN pip install git+https://github.com/opencadc-metadata-curation/cgps2caom2.git

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
