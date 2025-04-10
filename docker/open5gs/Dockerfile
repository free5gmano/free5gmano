FROM ubuntu:22.04 AS build

ARG OPEN5GS_VERSION=2.7.2

RUN apt-get update && \
    apt-get install -y python3-pip python3-setuptools python3-wheel ninja-build build-essential flex bison git cmake meson wget tar \
        libsctp-dev libgnutls28-dev libgcrypt-dev libssl-dev libmongoc-dev libbson-dev libyaml-dev libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev libtins-dev libtalloc-dev libidn-dev && \
    wget https://github.com/open5gs/open5gs/archive/v${OPEN5GS_VERSION}.tar.gz && \
    tar -zxf v${OPEN5GS_VERSION}.tar.gz && \
    mv open5gs-${OPEN5GS_VERSION} open5gs && \
    rm v${OPEN5GS_VERSION}.tar.gz && \
    cd open5gs && \
    meson build --prefix=`pwd`/install && \
    ninja -C build && \
    cd build && \
    ninja install

FROM ubuntu:22.04

COPY --from=build /open5gs/install /open5gs/install

COPY open5gs-entrypoint.sh /

WORKDIR /open5gs

RUN chmod +x /open5gs-entrypoint.sh && \
    apt-get update && \
    apt-get install -y iproute2 iptables libsctp-dev libmongoc-dev libyaml-dev libnghttp2-dev libmicrohttpd-dev libcurl4-gnutls-dev libtins-dev libtalloc2 libidn-dev && \
    apt-get clean
