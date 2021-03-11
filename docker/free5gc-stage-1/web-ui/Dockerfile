FROM node:10

# Clone free5gc-stage-1 project
RUN git clone https://bitbucket.org/nctu_5g/free5gc-stage-1.git /root/free5gc-stage-1

WORKDIR /root/free5gc-stage-1/webui
RUN npm install .
ENV DB_URI mongodb://mongodb-svc/free5gc

CMD npm run dev