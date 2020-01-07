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
