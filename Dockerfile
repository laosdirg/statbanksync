FROM python:3.5

MAINTAINER Zacharias

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        locales

RUN locale-gen en_DK.UTF-8 && dpkg-reconfigure locales
ENV LANG en_DK.UTF-8
ENV LC_NUMERIC en_DK.UTF-8

RUN mkdir -p /usr/src/app/statbanksync
WORKDIR /usr/src/app

COPY setup.py /usr/src/app/
COPY setup.py /usr/src/app/statbanksync/__init__.py
RUN python setup.py install

COPY . /usr/src/app

CMD [ "python", "-m", "statbanksync", "--reset", "folk1" ]
