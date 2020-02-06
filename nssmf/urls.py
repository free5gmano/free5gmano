# Copyright 2020 free5gmano
# All Rights Reserved.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.conf.urls import url

from nssmf.views import Provisioning, ServiceMappingPlugin, NetworkSliceTemplate, Template

urlpatterns = [
    url(r'^ObjectManagement/NSS/SliceProfiles$',
        Provisioning.as_view({
            'post': 'allocate_nssi'})),
    url(r'^ObjectManagement/NSS/SliceProfiles/command$',
        Provisioning.as_view({
            'post': 'allocate_nssi_for_command'})),
    url(r'^ObjectManagement/Generic/Template/(?P<id>(\w{8}(-\w{4}){3}-\w{12})?)$',
        Template.as_view({
            'post': 'create',
            'get': 'read',
            'patch': 'update',
            'delete': 'delete',
            'put': 'onboard'
        })),
    url(r'^ObjectManagement/Generic/Template/download/(?P<id>(\w{8}(-\w{4}){3}-\w{12})?)$',
        Template.as_view({
            'get': 'download'
        })),
    url(r'^ObjectManagement/NSS/Template/(?P<id>(\w{8}(-\w{4}){3}-\w{12})?)$',
        NetworkSliceTemplate.as_view({
            'post': 'create',
            'get': 'read',
            'patch': 'update',
            'delete': 'delete',
        })),

    url(r'^plugin/management/(?P<plugin_name>(?:[^/\n]*))$',
        ServiceMappingPlugin.as_view({
            'post': 'register_plugin',
            'get': 'get_plugin_list',
            'patch': 'update_plugin',
            'delete': 'delete_plugin'})),
]
