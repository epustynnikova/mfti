FROM ubuntu:20.04
MAINTAINER Elena Pustynnikova <elena.pustynnikova.work@gmail.com>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update

RUN apt-get install -y \
    python3-dev \
    python3-numpy \
    python3-pip \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U setuptools==65.6.3 more_itertools==9.0.0 singleton_decorator aenum markdown pytest pre-commit pandas kaleido==0.2.1 plotly

## USER CONFIGURATION, containers should not run as root
RUN adduser --disabled-password --gecos '' docker_user && chsh -s /bin/bash && mkdir -p /home/docker_user
USER    docker_user
WORKDIR /home/docker_user

COPY create_ganta_char.py ./
RUN mkdir data
COPY data/* data/

RUN cd ../
CMD ["bash"]
