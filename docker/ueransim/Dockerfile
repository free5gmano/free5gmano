FROM ubuntu:20.04 AS build

ARG CMAKE_VERSION=3.31.4
ARG UERANSIM_VERSION=3.2.6

RUN apt-get update && \
    apt-get install -y make gcc g++ libsctp-dev lksctp-tools iproute2 openssl libssl-dev wget tar && \
    wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz && \
    tar -zxf cmake-${CMAKE_VERSION}.tar.gz && \
    rm cmake-${CMAKE_VERSION}.tar.gz && \
    mv cmake-${CMAKE_VERSION} cmake && \
    cd cmake && \
    ./bootstrap && \
    make && \
    make install && \
    cd .. && \
    wget https://github.com/aligungr/UERANSIM/archive/v${UERANSIM_VERSION}.tar.gz && \
    tar -zxf v${UERANSIM_VERSION}.tar.gz && \
    rm v${UERANSIM_VERSION}.tar.gz && \
    mv UERANSIM-${UERANSIM_VERSION} UERANSIM && \
    cd UERANSIM && \
    make -j

FROM ubuntu:22.04

COPY --from=build  /UERANSIM /UERANSIM

WORKDIR /UERANSIM

RUN apt-get update && \
    apt-get install -y iproute2 libsctp-dev && \
    apt-get clean
