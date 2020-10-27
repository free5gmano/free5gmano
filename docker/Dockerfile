FROM ubuntu:16.04

RUN apt update && apt install -y libssl-dev python3 python3-pip git libmysqlclient-dev

WORKDIR /
RUN git clone https://github.com/free5gmano/free5gmano.git && cd free5gmano/ && git checkout v1.0.0
WORKDIR free5gmano/
RUN pip3 install -r requirements.txt

CMD python3 manage.py makemigrations moi nssmf FaultManagement && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000

