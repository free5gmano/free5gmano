from plugin_framework.allocate_nssi_abc import AllocateNSSIabc
import requests
import zipfile
import json
import os


class NFVOPlugin(AllocateNSSIabc):
    def __init__(self, nm_host, nfvo_host, subscription_host, parameter):
        super().__init__(nm_host, nfvo_host, subscription_host, parameter)
        self.vnf_pkg_id = str()
        self.vnf_subscription_list = dict()
        self.nsd_object_id = str()
        self.nsd_subscription_id = str()
        self.ns_descriptor_id = str()
        self.ns_instance_id = str()
        self.vnf_instance_data = list()
        self.nsi_subscription_id = str()
        self.nsinfo = dict()
        self.headers = {'Content-type': 'application/json'}

    def coordinate_tn_manager(self):
        pass

    def create_vnf_package(self, moi_config):
        url = self.NFVO_URL + "vnfpkgm/v1/vnf_packages/"
        data = {
            "userDefinedData": {
                "data": str(moi_config)
            }
        }
        create_vnfp = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_vnfp.status_code == 201:
            self.vnf_pkg_id = create_vnfp.json()['id']
            print("Vnf package ID: {}".format(create_vnfp.json()['id']))
        else:
            response = {
                "attributeListOut": {
                    'create_vnf_package': create_vnfp.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def create_vnf_package_subscriptions(self, vnf):
        print("Create vnf package subscribe: {}".format(self.vnf_pkg_id))
        url = self.NFVO_URL + "vnfpkgm/v1/subscriptions/"
        data = {
            "filter": {
                "vnfPkgId": [self.vnf_pkg_id]
            },
            "callbackUri": self.SUBSCRIPTION_HOST + "topics/vnf_pkg/"
        }
        create_vnf_subscribe = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_vnf_subscribe.status_code == 201:
            self.vnf_subscription_list[vnf] = create_vnf_subscribe.json()['id']
        else:
            response = {
                "attributeListOut": {
                    'create_vnf_subscribe': create_vnf_subscribe.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def read_vnf_package(self, vnf_pkg_id):
        url = self.NFVO_URL + "vnfpkgm/v1/vnf_packages/{}/".format(vnf_pkg_id)
        create_vnfp = requests.get(url, headers=self.headers)
        print("Vnf package ID: {}".format(create_vnfp.json()['id']))
        return create_vnfp

    def upload_vnf_package(self, vnf_pkg_path):
        src_path = os.getcwd()
        vnf = vnf_pkg_path.split('/')[-1]

        # VNF Package compression
        os.chdir(os.path.join(vnf_pkg_path))
        with zipfile.ZipFile(vnf_pkg_path + '.zip', mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            for pkg_root, folders, files in os.walk('.'):
                for s_file in files:
                    a_file = os.path.join(pkg_root, s_file)
                    zf.write(a_file, arcname=os.path.join(vnf, a_file))
        os.chdir(src_path)
        print("Upload '{}' package...".format(vnf))
        url = self.NFVO_URL + "vnfpkgm/v1/vnf_packages/{}/package_content/".format(self.vnf_pkg_id)
        files = {'file': (vnf + '.zip', open(vnf_pkg_path + '.zip', 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        headers = {
            'Accept': "application/json,application/zip",
            'accept-encoding': "gzip, deflate"
        }
        upload_vnfp = requests.put(url, files=files, headers=headers)
        print(upload_vnfp.status_code)

    def listen_on_vnf_package_subscriptions(self):
        # TODO gitlab feature/deallocateNSSI API in 250 row
        pass

    def create_ns_descriptor(self):
        print("Create Network service descriptor...")
        url = self.NFVO_URL + "nsd/v1/ns_descriptors/"
        data = {
            "userDefinedData": {}
        }
        create_nsd = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_nsd.status_code == 201:
            self.nsd_object_id = create_nsd.json()['id']
        else:
            response = {
                "attributeListOut": {
                    'create_vnf_subscribe': create_nsd.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def create_ns_descriptor_subscriptions(self, ns_des):
        print("Network service descriptor object Id: {}".format(self.nsd_object_id))
        url = self.NFVO_URL + "nsd/v1/subscriptions/"
        data = {
            "filter": {
                "nsdInfoId": [self.nsd_object_id]
            },
            "callbackUri": self.SUBSCRIPTION_HOST + "topics/ns_descriptor/"
        }
        create_nsd_subscribe = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_nsd_subscribe.status_code == 201:
            self.nsd_subscription_id = create_nsd_subscribe.json()['id']
        else:
            response = {
                "attributeListOut": {
                    'create_nsd_subscribe': create_nsd_subscribe.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def upload_ns_descriptor(self, ns_descriptor_path):
        src_path = os.getcwd()
        ns_des = ns_descriptor_path.split('/')[-1]

        # NS Description compression
        os.chdir(ns_descriptor_path)
        with zipfile.ZipFile(ns_descriptor_path + '.zip', mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            for pkg_root, folders, files in os.walk('.'):
                for s_file in files:
                    a_file = os.path.join(pkg_root, s_file)
                    zf.write(a_file, arcname=os.path.join(ns_des, a_file))
        os.chdir(src_path)
        print('Upload Network Service descriptor file...')
        url = self.NFVO_URL + "nsd/v1/ns_descriptors/{}/nsd_content/".format(self.nsd_object_id)
        files = {'file': (ns_des + '.zip', open(ns_descriptor_path + '.zip', 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        headers = {
            'Accept': "application/json,application/zip",
            'accept-encoding': "gzip, deflate"
        }
        upload_nsd = requests.put(url, files=files, headers=headers)
        print("Upload operated status {}".format(upload_nsd.status_code))
        self.read_ns_descriptor(self.nsd_object_id)

    def read_ns_descriptor(self, nsd_object_id):
        # None plugin inherit
        url = self.NFVO_URL + "nsd/v1/ns_descriptors/{}/".format(nsd_object_id)
        get_nsd = requests.get(url, headers=self.headers)
        self.ns_descriptor_id = get_nsd.json()['nsdId']
        print("Network service descriptor ID: {}".format(self.ns_descriptor_id))
        return get_nsd

    def listen_on_ns_descriptor_subscriptions(self):
        pass

    def create_ns_instance(self):
        print("Create Network service Instance ...")
        url = self.NFVO_URL + "nslcm/v1/ns_instances/"
        data = {
            "nsdId": self.ns_descriptor_id,
            "nsName": "string",
            "nsDescription": "string"
        }
        create_nsi = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_nsi.status_code == 201:
            self.ns_instance_id = create_nsi.json()['id']
            vnf_instance_list = create_nsi.json()['vnfInstance']
            for vnf_instance in vnf_instance_list:
                self.vnf_instance_data.append({
                    "vnfInstanceId": vnf_instance['id'],
                    "vnfProfileId": "string"
                })

        else:
            response = {
                "attributeListOut": {
                    'create_nsi': create_nsi.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def create_ns_instance_subscriptions(self):
        url = self.NFVO_URL + "nslcm/v1/subscriptions/"
        data = {
            "filter": {
                "nsInstanceSubscriptionFilter": {
                    "nsInstanceIds": [self.ns_instance_id]
                }
            },
            "callbackUri": self.SUBSCRIPTION_HOST + "topics/ns_instances/"
        }
        create_nsi_subscribe = requests.post(url, data=json.dumps(data), headers=self.headers)
        if create_nsi_subscribe.status_code == 201:
            self.nsi_subscription_id = create_nsi_subscribe.json()['id']
        else:
            response = {
                "attributeListOut": {
                    'create_nsi_subscribe': create_nsi_subscribe.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def ns_instantiation(self, ns_descriptor_path):
        print("Network service instance ID: {}".format(self.ns_instance_id))
        print("Instantiation Network service Instance ...")
        print("Vnf instance data {}".format(self.vnf_instance_data))
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/instantiate/".format(self.ns_instance_id)
        data = {"vnfInstanceData": self.vnf_instance_data}
        instance_nsi = requests.post(url, data=json.dumps(data), headers=self.headers)
        print("Instantiation operated status {}".format(instance_nsi.status_code))
        self.read_ns_instantiation(self.ns_instance_id)

    def read_ns_instantiation(self, ns_instance_id):
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/".format(ns_instance_id)
        read_instance_nsi = requests.get(url, headers=self.headers)
        nsinfo = read_instance_nsi.json()
        vnf_pkg_id_list = []
        # subscription_list = {
        #     'vnfp_subscription': self.vnf_subscription_list,
        #     'nsd_subscription': self.nsd_subscription_id,
        #     'nsi_subscription': self.nsi_subscription_id
        # }
        for _ in nsinfo['vnfInstance']:
            vnf_pkg_id_list.append(_['vnfPkgId'])
        print('Nsinfo ID: {}'.format(nsinfo['id']))
        self.nsinfo = {
            "id": nsinfo['id'],
            "nsInstanceName": nsinfo['nsInstanceName'],
            "nsInstanceDescription": nsinfo['nsInstanceDescription'],
            "nsdId": nsinfo['nsdId'],
            "nsdInfoId": nsinfo['nsdInfoId'],
            "flavourId": nsinfo['flavourId'],
            "vnfInstance": str(nsinfo['vnfInstance']),
            "vnffgInfo": str(nsinfo['vnffgInfo']),
            "nestedNsInstanceId": str(nsinfo['nestedNsInstanceId']),
            "nsState": nsinfo['nsState'],
            "_links": str(nsinfo['_links']),
        }
        return read_instance_nsi

    def update_ns_instantiation(self, ns_instance_id, update_info):
        print("Update Network service instance ID: {}".format(ns_instance_id))
        print("Update Network service Info: {}".format(update_info))
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/update/".format(ns_instance_id)
        data = dict()
        if 'ADD' in update_info['type']:
            data = {
                "updateType": update_info['type'],
                "addVnfInstance": [
                    {
                        "vnfInstanceId": update_info['vnf_instance_id'],
                        "vnfProfiledId": "string"
                    }
                ]
            }
        elif 'REMOVE' in update_info['type']:
            data = {
                "updateType": update_info['type'],
                "removeVnfInstanceId": update_info['vnf_instance_id']
            }
        update_nsi = requests.post(url, data=json.dumps(data), headers=self.headers)
        if update_nsi.status_code == 202:
            print("Update operated status {}".format(update_nsi.status_code))
        else:
            response = {
                "attributeListOut": {
                    'update_nsi': update_nsi.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def scale_ns_instantiation(self, ns_instance_id, scale_info):
        print("Scale Network service instance ID: {}".format(ns_instance_id))
        print("Scale Network service instance Info".format(scale_info))
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/scale/".format(ns_instance_id)
        data = {
            "scaleType": "SCALE_VNF",
            "scaleVnfData": [
                {
                    "vnfInstanceId": scale_info['vnf_instance_id'],
                    "scaleVnfType": scale_info['type'],
                    "scaleByStepData": {
                        "additionalParams": {
                            "replicas": scale_info['replicas']
                        }
                    }
                }
            ]
        }

        scale_nsi = requests.post(url, data=json.dumps(data), headers=self.headers)
        if scale_nsi.status_code == 202:
            print("Scale operated status {}".format(scale_nsi.status_code))
        else:
            response = {
                "attributeListOut": {
                    'scale_nsi': scale_nsi.status_code
                },
                "status": "OperationFailed"
            }
            raise Exception(response)

    def listen_on_ns_instance_subscriptions(self):
        pass
