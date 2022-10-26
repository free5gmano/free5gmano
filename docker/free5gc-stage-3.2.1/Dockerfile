FROM golang:1.14.4

RUN apt update -y
RUN apt -y install git wget gcc cmake autoconf libtool pkg-config libmnl-dev libyaml-dev

WORKDIR /
RUN git clone --recursive -b v3.2.1 -j `nproc` https://github.com/free5gc/free5gc.git

WORKDIR /free5gc
#RUN go get -u github.com/sirupsen/logrus

RUN make upf

FROM ubuntu:20.04
RUN apt update -y && \
    DEBIAN_FRONTEND=noninteractive \
    apt -y install wget curl git iputils-ping tcpdump net-tools nano libmnl-dev libyaml-dev iproute2 iptables dnsutils &&\
    apt-get clean

WORKDIR /free5gc
COPY --from=0 /free5gc /free5gc

COPY setup-uptun.sh /
RUN chmod +x /setup-uptun.sh

# ENV GIN_MODE=release
