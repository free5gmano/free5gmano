FROM ubuntu:20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y curl wget python3-pip \
        python3-setuptools python3-wheel ninja-build build-essential flex bison git libsctp-dev \
        libgnutls28-dev libgcrypt-dev libssl-dev libidn11-dev libmongoc-dev libbson-dev libyaml-dev \ 
	libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev libnghttp2-dev meson
 
WORKDIR /
RUN wget https://github.com/open5gs/open5gs/archive/v2.1.7.tar.gz
RUN tar -zxvf v2.1.7.tar.gz 
RUN mv open5gs-2.1.7 open5gs

WORKDIR /open5gs
RUN meson build --prefix=`pwd`/install
RUN ninja -C build

WORKDIR /open5gs/build
RUN ninja install

WORKDIR /open5gs/install

FROM ubuntu:20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libsctp-dev libgnutls28-dev \
        libgcrypt-dev libssl-dev libidn11-dev libmongoc-dev libbson-dev libyaml-dev libnghttp2-dev \
	libmicrohttpd-dev libcurl4-gnutls-dev libnghttp2-dev

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install iputils-ping tcpdump nano git iproute2 iptables

WORKDIR /open5gs/install
COPY --from=0 /open5gs/install /open5gs/install
COPY setup-uptun.sh ./
RUN chmod +x ./setup-uptun.sh
