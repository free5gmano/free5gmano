# free5gmano NM manager
![](https://i.imgur.com/siaTpV7.png)
## Table of Contents
- [free5gmano](#What-is-free5gmano?)
- [Features](#Features)
- [Dependencies](#Dependencies)
- [Getting started](#Getting-started)
  - [Install NFV-MANO](#Install-NFV-MANO)
  - [Install NM](#Install-NM)
  - [Install Kafka](#Install-Kafka)
- [Apply a NSSI (Network Slice Subnet Instance)](#Apply-a-NSSI-(Network-Slice-Subnet-Instance))
  - [Install the nmctl client](#Install-the-nmctl-client)
- [Release Note](#Release-Note)

## What is free5gmano?
This is a 5G MANO (Management and Network Orchestration) project developed that refer to 3GPP TS 28.531, TS 28.532 Release 15 (R15). The purpose is to achieve the management and scheduling of 5G network slices. Please refer to [Features](#Features) for the functions of release.
This project is collaborating with [free5GC.org](https://free5gc.org). Hence, it can provide as a MANO platform for deploying network slice subnet instances (NSSIs) of free5GC VNFs. 

Currently, the major contributors of this project are Department of Computer Science and Information Engineering (Dept. of CSIE) and Center of Infomormation Technology Innovation Services (CITIS), National Taichung University of Science and Technology (NTCUST)

Note:
Thank you very much for your interest in free5gmano. The license of Stage 2 free5gmano follows [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0). That is, anyone can use free5gmano for commercial purposes for free. We will not charge any license fee.

This project is initiated by:
[![](https://i.imgur.com/7HU6PZu.png)](https://www.moea.gov.tw/)[![](https://i.imgur.com/kNImVoF.png)](https://www.edu.tw/)
## Architecture
![](https://imgur.com/ImpCFyt.png)
It's refer to [ETSI GS NFV-MAN 001 V1.1.1](https://www.etsi.org/deliver/etsi_gs/NFV-MAN/001_099/001/01.01.01_60/gs_NFV-MAN001v010101p.pdf)

## Features
* AllocationNssi API is implemented in Network Slice Subnet Management Function that refer to 3GPP TS 28.531 (R15). It can create a Network Slice Subnet Instance (NSSI) by calling os-ma-nfvo interface, which is the basis of network slicing.
* A Service Mapping Plugin framework is designed to deploy the Network Slice Subnet Instance (NSSI) via os-ma-nfvo APIs and provide the selection of the open source NFV Orchestrators, e.g. Kubernetes-based [Kube5gnfvo](https://github.com/free5gmano/kube5gnfvo) (default), [OpenStack-based Tacker](https://wiki.openstack.org/wiki/Tacker) etc.
* Network Slice Subnet Template can assist users to provide ETSI MANO NFVO required information, e.g. VNF Package, Network Service Descriptor

## Dependencies
The following packages are required:
* git
* python3
* pip3
* mysql
* NFV-MANO
* Kafka

## Getting started
### Install NFV-MANO
#### Option1 - install kube5gnfvo
Please refer to [kube5gnfvo](https://github.com/free5gmano/kube5gnfvo) Installation Guide to install kube5gnfvo.

#### Option2 - install OpenStack Tacker
Please refer to [OpenStack Tacker](https://github.com/free5gmano/tacker-example-plugin) Installation Guide to install OpenStack Tacker.

### Deploy free5gmano by Kubernetes
```
git clone https://github.com/free5gmano/free5gmano.git
cd free5gmano/deploy
kubectl apply -f .
```
### Install Kafka
Please refer to [Kafka](https://docs.confluent.io/current/getting-started.html) Installation Guide to install Kafka.
### Manual install free5gmano
If you have deployed free5gmano by Kubernetes before, you can jump to [Apply a NSSI (Network Slice Subnet Instance)](#apply-a-nssi-network-slice-subnet-instance).
1. Install the required packages
```
sudo apt -y update
sudo apt install -y python3 python3-pip git libmysqlclient-dev mysql-server
sudo service mysql start
```

2. Alias python3 to python
```
sudo alias python=python3
sudo alias pip=pip3
```

3. Clone nm_manager project
```
git clone https://github.com/free5gmano/free5gmano.git
cd free5gmano
```

4. Install python dependencies
```
pip install -r requirements.txt
```

5. Apply environment variable
```
echo 'export FREE5GMANO_MYSQL_USER=<your mysql user>' >> ~/.bashrc
echo 'export FREE5GMANO_MYSQL_PASSWORD=<your mysql password>' >> ~/.bashrc
echo 'export FREE5GMANO_MYSQL_HOST=<your mysql host ip>' >> ~/.bashrc
echo 'export FREE5GMANO_MYSQL_PORT=<your mysql port>' >> ~/.bashrc
echo 'export FREE5GMANO_NM=127.0.0.1:8000' >> ~/.bashrc
echo 'export FREE5GMANO_NFVO=<your nfvo ip>:<your nfvo port>' >> ~/.bashrc
source ~/.bashrc
```

6. Create a database
```
mysql -u $FREE5GMANO_MYSQL_USER -p$FREE5GMANO_MYSQL_PASSWORD
CREATE DATABASE free5gmano;
```
7. Database migrate
```
python manage.py makemigrations nssmf moi FaultManagement
python manage.py migrate
```
8. Run the Django server
```
python manage.py runserver 0.0.0.0:8000
```
## Apply a NSSI (Network Slice Subnet Instance)
### Install the **nmctl** client
Please refer to [free5gmano-cli](https://github.com/free5gmano/free5gmano-cli) Installation Guide to install free5gmano-cli.

1. Clone simpleexampleplugin project
```
git clone https://github.com/free5gmano/simpleexampleplugin.git
```
2. Register a service mapping plugin
```
nmctl register plugin kube5gnfvo -f simpleexampleplugin/
```
3. Check service mapping plugin is registered
```
nmctl get plugin
        name     allocate_nssi     deallocate_nssi
  kube5gnfvo  allocate/main.py  deallocate/main.py
```
4. Create a VNF Template
```
nmctl create template -t VNF -n kube5gnfvo
Do you want to download example? [y/N]: y
OperationSucceeded
Template Id: 00936c28-ba30-4604-a134-4f4302acaea7
```
5. Onboard the VNF Template
```
nmctl onboard template 00936c28-ba30-4604-a134-4f4302acaea7 -f VNF/
```
6. Create a NSD Template
```
nmctl create template -t NSD -n kube5gnfvo
Do you want to download example? [y/N]: y
OperationSucceeded
Template Id: 31e7f5ad-9259-4b9b-97b6-d3ff78996aec
```
7. Onboard the NSD Template
```
nmctl onboard template 31e7f5ad-9259-4b9b-97b6-d3ff78996aec -f NSD/
```
8. Create a NRM Template
```
nmctl create template -t NRM -n kube5gnfvo
Do you want to download example? [y/N]: y
OperationSucceeded
Template Id: 68e7411e-cf0d-4113-a15f-493ae5cad54f
```
9. Onboard the NRM Template
```
nmctl onboard template 68e7411e-cf0d-4113-a15f-493ae5cad54f -f NRM/
```
10. Combined the VNF, NSD, NRM Template to Network Slice Subnet Template (NSST)
```
nmctl create nsst -n kube5gnfvo 00936c28-ba30-4604-a134-4f4302acaea7 31e7f5ad-9259-4b9b-97b6-d3ff78996aec 68e7411e-cf0d-4113-a15f-493ae5cad54f
OperationSucceeded, NSST is combined.
NSST Id:: 66ff6b6f-6c54-4498-bc1e-411382c80bc5
```
11. Commissioning a NSSI(via NSST)
```
nmctl allocate nssi 66ff6b6f-6c54-4498-bc1e-411382c80bc5
Do you want to Using exist Nssi? [y/N]: N
Create Nssi...
Nssi ID: b4483341-1021-44c0-b30f-bacfbb82eeaa
```
12. Modification a NSSI(via New NSST)
`You should choice 'y' and provide Nssi ID`
```
nmctl allocate nssi 6d116653-6785-4d00-91fd-4d3a4603a286
Do you want to Using exist Nssi? [y/N]: y
Nssi ID: : b4483341-1021-44c0-b30f-bacfbb82eeaa
Modify Nssi b4483341-1021-44c0-b30f-bacfbb82eeaa...
```
13. Decommissioning a NSSI
```
nmctl deallocate nssi b4483341-1021-44c0-b30f-bacfbb82eeaa
Delete Nssi...
```
14. Create Management Object Instance Subscription
```
nmctl create subscriptions -t moi <<Nssi_ID>>
notification Id: 3ae036cf-b4ea-46e3-b4da-3ef122c96e1e
```
15. Create Fault Management Subscription
```
nmctl create subscriptions -t fm <<Nssi_ID>>
notification Id: 3ae036cf-b4ea-46e3-b4da-3ef122c96e1e
```
16. Delete Fault Management Subscription
```
nmctl delete subscriptions <<notification_Id>>
OperationSucceeded
```

## Docker Repository
[free5gmano](https://hub.docker.com/repository/docker/free5gmano/free5gmano)
[free5gc-stage-1](https://hub.docker.com/repository/docker/free5gmano/free5gc-base)
[free5gc-stage-2(control plane)](https://hub.docker.com/repository/docker/free5gmano/free5gc-control-plane)
[free5gc-stage-2(user plane)](https://hub.docker.com/repository/docker/free5gmano/free5gc-user-plane)

## Contributors
**National Taichung University of Science and Technology:** Cheng-En Wu, Sheng-Tang Hsu, Yi-Chieh Hsu, Wen-Sheng Li, Meng-Ze Li, Yi-Xin Lin, Hung-Ming Chen, Yung-Feng Lu

## Release Note
* Allocate a Network Slice Subnet Instance(NSSI) and deploy [free5GC](https://www.free5gc.org/)


&copy;Copyright January 2020
All rights reserved.

Contact:
free5gmano@gmail.com
