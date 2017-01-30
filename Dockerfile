FROM python:3
MAINTAINER Rufus Cable <rufus@threebytesfull.com>

WORKDIR /pcbmode

ADD . /pcbmode-inst

RUN apt-get update && \
    apt-get install -y inkscape && \
    cd /pcbmode-inst && \
    python setup.py install

ENTRYPOINT ["/usr/local/bin/python", "/usr/local/bin/pcbmode"]
CMD ["--help"]
