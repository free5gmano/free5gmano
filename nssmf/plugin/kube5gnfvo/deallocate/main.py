from plugin_framework.deallocate_nssi_abc import DeallocateNSSIabc
import requests
import json


class NFVOPlugin(DeallocateNSSIabc):
    def __init__(self, nm_host, nfvo_host, subscription_host, parameter):
        super().__init__(nm_host, nfvo_host, subscription_host, parameter)
        self.headers = {'Content-type': 'application/json'}

    def coordinate_tn_manager(self):
        pass

    def terminate_network_service_instance(self):
        print('Terminate Network service instance...')
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/terminate/".format(self.ns_instance)
        response = requests.post(url, headers=self.headers)
        print(response.status_code)

    def delete_network_service_instance(self):
        print('Delete Network service instance...')
        url = self.NFVO_URL + "nslcm/v1/ns_instances/{}/".format(self.ns_instance)
        response = requests.delete(url, headers=self.headers)
        print(response.status_code)

    def delete_network_service_instance_subscriptions(self):
        print('Delete Network service instance subscriptions...')
        url = self.NFVO_URL + "nslcm/v1/subscriptions/{}/".format(self.nsi_subscription)
        response = requests.delete(url, headers=self.headers)
        print(response.status_code)

    def update_network_service_descriptor(self):
        print('Update Network service descriptor...')
        url = self.NFVO_URL + "nsd/v1/ns_descriptors/{}/".format(self.ns_descriptor)
        data = {
            "nsdOperationalState": "DISABLED",
            "userDefinedData": [
                {}
            ]
        }
        response = requests.patch(url, data=json.dumps(data), headers=self.headers)
        print(response.status_code)

    def delete_network_service_descriptor(self):
        print('Delete Network service descriptor...')
        url = self.NFVO_URL + "nsd/v1/ns_descriptors/{}/".format(self.ns_descriptor)
        response = requests.delete(url, headers=self.headers)
        print(response.status_code)

    def delete_network_service_descriptor_subscriptions(self):
        print('Delete Network service descriptor subscriptions...')
        url = self.NFVO_URL + "nsd/v1/subscriptions/{}/".format(self.nsd_subscription)
        response = requests.delete(url, headers=self.headers)
        print(response.status_code)

    def update_vnf_package(self):
        for vnf in self.vnf_package:
            print('Update {} Vnf Package...'.format(vnf))
            url = self.NFVO_URL + "vnfpkgm/v1/vnf_packages/{}/".format(vnf)
            data = {
                "operationalState": "DISABLED",
                "userDefinedData": {}
            }
            response = requests.patch(url, data=json.dumps(data), headers=self.headers)
            print(response.status_code)

    def delete_vnf_package(self):
        for vnf in self.vnf_package:
            print('Delete {} Vnf Package...'.format(vnf))
            url = self.NFVO_URL + "vnfpkgm/v1/vnf_packages/{}/".format(vnf)
            response = requests.delete(url, headers=self.headers)
            print(response.status_code)

    def delete_vnf_package_subscriptions(self):
        for vnf in self.vnfp_subscription:
            print('Delete {} Vnf Package subscriptions...'.format(vnf))
            url = "http://10.0.0.217:8000/vnfpkgm/v1/subscriptions/{}/".format(
                self.vnfp_subscription[vnf])
            response = requests.delete(url, headers=self.headers)
            print(response.status_code)
