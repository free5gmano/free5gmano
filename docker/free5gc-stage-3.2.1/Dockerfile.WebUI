FROM ubuntu:20.04

RUN apt -y update && \
    DEBIAN_FRONTEND=noninteractive \
    apt remove cmdtest yarn && \
    apt install -y curl git gnupg2 make wget

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN apt -y update && \
    DEBIAN_FRONTEND=noninteractive \
    apt install -y nodejs yarn git

WORKDIR /
RUN wget https://dl.google.com/go/go1.14.4.linux-amd64.tar.gz
RUN tar -zxvf go1.14.4.linux-amd64.tar.gz
RUN rm /go1.14.4.linux-amd64.tar.gz

ENV GOPATH /go
ENV PATH $PATH:$GOPATH/bin:$GOROOT/bin

WORKDIR /
RUN git clone --recursive -b v3.2.1 -j `nproc` https://github.com/free5gc/free5gc.git

WORKDIR /free5gc/webconsole
RUN git checkout v1.0.1

WORKDIR /free5gc
RUN make webconsole

FROM ubuntu:20.04
RUN apt update -y

WORKDIR /free5gc
COPY --from=0 /free5gc /free5gc

# ENV GIN_MODE=release
