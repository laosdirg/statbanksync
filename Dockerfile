FROM python:3.5

MAINTAINER Zacharias

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        locales

RUN mkdir -p /usr/src/app/statbanksync
WORKDIR /usr/src/app

COPY setup.py /usr/src/app/
COPY setup.py /usr/src/app/statbanksync/__init__.py
RUN python setup.py install

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
RUN sed -i -e 's/# en_DK.UTF-8 UTF-8/en_DK.UTF-8 UTF-8/' /etc/locale.gen
RUN echo 'LANG="en_DK.UTF-8"' > /etc/default/locale
RUN dpkg-reconfigure --frontend=noninteractive locales
ENV LANGUAGE "C"
ENV LC_ALL "C.UTF-8"

COPY . /usr/src/app

CMD [ "python", "-m", "statbanksync", "--reset", "ft" ]
