# free5gmano
## Dependencies
The following packages are required:

* git
* python3
* pip3
* mysql
* NFV-MANO

## Installation Guide
### Install NFV-MANO
#### Option1 - install kube5gnfvo
Please refer to [kube5gnfvo](https://github.com/free5gmano/kube5gnfvo) Installation Guide to install kube5gnfvo.

#### Option2 - install OpenStack Tacker
Please refer to [OpenStack Tacker](https://github.com/free5gmano/tacker-example-plugin) Installation Guide to install OpenStack Tacker.

### Install NM
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
git clone https://github.com/free5gmano/nm_manager.git
cd nm_manager
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
mysql -h $FREE5GMANO_MYSQL_HOST -u $FREE5GMANO_MYSQL_USER -p$FREE5GMANO_MYSQL_PASSWORD
CREATE DATABASE free5gmano
```
7. Database migrate
```
python manage.py makemigrations
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
8. Combined the VNF and NSD Template to Network Slice Subnet Template (NSST)
```
nmctl create nsst -n kube5gnfvo 00936c28-ba30-4604-a134-4f4302acaea7 31e7f5ad-9259-4b9b-97b6-d3ff78996aec
OperationSucceeded, NSST is combined.
NSST Id:: 66ff6b6f-6c54-4498-bc1e-411382c80bc5
```
9. Apply a NSSI
```
nmctl allocate nssi 66ff6b6f-6c54-4498-bc1e-411382c80bc5
```

## Release Note
Allocate a Network Slice Subnet Instance(NSSI) and deploy [free5GC v1.0.0](https://bitbucket.org/nctu_5g/free5gc-stage-1/src/master/)