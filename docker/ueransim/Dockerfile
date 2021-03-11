FROM ubuntu:20.04

RUN apt update && apt-get install -y make g++ libsctp-dev lksctp-tools iproute2 libssl-dev nano wget tcpdump

WORKDIR /
RUN wget https://github.com/Kitware/CMake/releases/download/v3.19.4/cmake-3.19.4.tar.gz
RUN tar -zxvf cmake-3.19.4.tar.gz

WORKDIR /cmake-3.19.4
RUN ./bootstrap
RUN make
RUN make install

WORKDIR /
RUN wget https://github.com/aligungr/UERANSIM/archive/v3.1.0.tar.gz
RUN tar -zxvf v3.1.0.tar.gz
RUN mv UERANSIM-3.1.0 UERANSIM

WORKDIR /UERANSIM
RUN make
