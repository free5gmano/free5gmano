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

import os
import yaml
import json
import shutil
import zipfile
import importlib

from django.http import JsonResponse, Http404, HttpResponse
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from nssmf.serializers import SliceTemplateSerializer, SliceTemplateRelationSerializer, \
    GenericTemplateSerializer, GenericTemplateFileSerializer, ServiceMappingPluginSerializer, \
    ServiceMappingPluginRelationSerializer
from nssmf.models import SliceTemplate, GenericTemplate, ServiceMappingPluginModel, Content
from nssmf.enums import OperationStatus, PluginOperationStatus
from free5gmano import settings


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class MultipleSerializerViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.basename == 'GenericTemplate':
            if self.action == 'upload':
                return GenericTemplateFileSerializer
            return GenericTemplateSerializer
        elif self.basename == 'SliceTemplate':
            if self.action in ('retrieve', 'list'):
                return SliceTemplateRelationSerializer
            return SliceTemplateSerializer
        elif self.basename == 'Provisioning':
            return SliceTemplateSerializer


class GenericTemplateView(MultipleSerializerViewSet):
    """ Generic Template
    """
    queryset = GenericTemplate.objects.all()
    serializer_class = MultipleSerializerViewSet.get_serializer_class

    @staticmethod
    def check(request, content, filename):
        # Check content isn't exist Content
        for query in Content.objects.all():
            if str(content['topology_template']) in query.topology_template and \
                    request.data['nfvoType'] in query.templateId.nfvoType:
                response = {
                    OperationStatus.OPERATION_FAILED: request.data[
                                                          'templateType'] + ' is exist ' + filename}
                return response

    def list(self, request, *args, **kwargs):
        """
            Query Generic Template information.
            The GET method queries the information of the Generic Template matching the filter.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
            Create a new individual Generic Template resource.
            The POST method creates a new individual Generic Template resource.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
            Read information about an individual Generic Template resource.
            The GET method reads the information of a Generic Template.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update information about an individual Generic Template resource.
            The PATCH method updates the information of a Generic Template.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
            Delete an individual Generic Template.
            The DELETE method deletes an individual Generic Template resource.
        """
        file = self.get_object().templateFile
        if file:
            file_folder = os.path.join(
                settings.MEDIA_ROOT,
                os.path.dirname(str(self.get_object().templateFile)),
                str(self.get_object().templateId)
            )
            shutil.rmtree(file_folder)
            file.delete()
        return super().destroy(request, *args, **kwargs)

    def upload(self, request, *args, **kwargs):
        """
            Upload a Generic Template by providing the content of the Generic Template.
            The PUT method uploads the content of a Generic Template.
        """
        path = os.path.join(
            settings.MEDIA_ROOT,
            request.data['templateType'],
            str(kwargs['pk'])
        )
        generic_template_obj = self.get_object()
        # Delete old Content related
        for relate_obj in self.get_object().content_set.all():
            file = self.get_object().templateFile
            file.delete()
            self.get_object().content_set.remove(relate_obj)
            
        with zipfile.ZipFile(request.data['templateFile']) as _zipfile:
            for element in _zipfile.namelist():
                if '.yaml' in element:
                    with _zipfile.open(element) as file:
                        content = yaml.load(file, Loader=yaml.FullLoader)
                        content_obj = Content(type=self.get_object().templateType,
                                              tosca_definitions_version=content['tosca_definitions_version'],
                                              topology_template=str(content['topology_template']))
                    # check_result = self.check(request, content, filename)

                    # if check_result:
                    #     return Response(check_result, status=400)

                    content_obj.save()
                    generic_template_obj.content_set.add(content_obj)
                elif '.json' in element:
                    with _zipfile.open(element) as file:
                        content = json.loads(file.read().decode('utf-8'))
                    content_obj = Content(type=self.get_object().templateType,
                                          tosca_definitions_version="None",
                                          topology_template=str(content))
                    content_obj.save()
                    generic_template_obj.content_set.add(content_obj)
            _zipfile.extractall(path=path)
        self.partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='example_download/(?P<example>(.)*)/(?P<path>(.)*)')
    def example_download(self, request, *args, **kwargs):
        """
            Download an individual Generic Template.
            The GET method reads the content of the Generic Template.
        """
        source_path = os.getcwd()
        example_file = os.path.join(settings.BASE_DIR, 'nssmf', 'template_example',
                                    kwargs['example'], kwargs['path'].split('/')[0])
        os.chdir(example_file)

        with zipfile.ZipFile(example_file + '.zip', mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            for root, folders, files in os.walk('.'):
                for s_file in files:
                    a_file = os.path.join(root, s_file)
                    zf.write(a_file)
        os.chdir(source_path)
        with open(example_file + '.zip', 'rb') as f:
            return HttpResponse(f.read(), content_type="application/zip")

    @action(detail=False, methods=['get'], url_path='download/(?P<path>(.)*)')
    def download(self, request, *args, **kwargs):
        """
            Download an individual Generic Template for Free5Gmano Dashboard.
            The GET method reads the content of the Generic Template.
        """
        download_query = self.queryset.filter(templateFile=kwargs['path'])
        s = download_query[0].templateFile.name
        filename = s[4:]
        if download_query:
            with download_query[0].templateFile.open() as f:
                # return HttpResponse(f.read(), content_type="application/zip")
                response = HttpResponse(f.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + filename
                return response


class SliceTemplateView(MultipleSerializerViewSet):
    """
        Slice Template
    """
    queryset = SliceTemplate.objects.all()
    serializer_class = MultipleSerializerViewSet.get_serializer_class

    def list(self, request, *args, **kwargs):
        """
            Query Slice Template information.
            The GET method queries the information of the Slice Template matching the filter.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
            Create a new individual Slice Template resource.
            The POST method creates a new individual Slice Template resource.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
            Read information about an individual Slice Template resource.
            The GET method reads the information of a Slice Template.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update information about an individual Slice Template resource.
            The PATCH method updates the information of a Slice Template.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
            Delete an individual Slice Template.
            The DELETE method deletes an individual Slice Template resource.
        """
        return super().destroy(request, *args, **kwargs)


class ProvisioningView(GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """ Provisioning Network Slice Instance
    """
    queryset = SliceTemplate.objects.all()
    serializer_class = ServiceMappingPluginRelationSerializer

    def create(self, request, *args, **kwargs):
        """
            Allocate Network Slice Subnet Instance.
            Allocate a new individual Network Slice Subnet Instance
        """
        data = request.data['attributeListIn']
        response_data = dict()
        try:
            response_data['status'] = OperationStatus.OPERATION_FAILED
            if data['using_existed']:
                check_query = SliceTemplate.objects.filter(instanceId=data['using_existed'])
                for query in check_query:
                    query.instanceId.remove(data['using_existed'])
            unit_query = SliceTemplate.objects.get(templateId=data['nsstid'])
            slice_serializer = ServiceMappingPluginRelationSerializer(unit_query)
            generic_templates = slice_serializer.data['genericTemplates']
            service_plugin = slice_serializer.data['nfvoType'][0]
        except SliceTemplate.DoesNotExist:
            print(SliceTemplate.DoesNotExist)
            return JsonResponse(response_data)
        try:
            parameter = {
                'vnf_template': generic_templates['VNF'][0],
                'ns_template': generic_templates['NSD'][0],
                'slice_template': generic_templates['NRM'][0],
                'use_existed': data['using_existed']
            }
            plugin = importlib.import_module(
                'nssmf.plugin.{}.{}.{}'.format(
                    service_plugin['name'],
                    service_plugin['allocate_nssi'].split('/')[0],
                    service_plugin['allocate_nssi'].split('/')[1].split('.')[0]))
            nfvo_plugin = plugin.NFVOPlugin(
                        service_plugin['nm_host'],
                        service_plugin['nfvo_host'],
                        service_plugin['subscription_host'],
                        parameter)
            nfvo_plugin.allocate_nssi()
            unit_query.instanceId.add(nfvo_plugin.nssiId)
            return JsonResponse(nfvo_plugin.moi_config)
        except IOError as e:
            return JsonResponse(response_data, status=400)

    def destroy(self, request, *args, **kwargs):
        """
            Deallocate Network Slice Subnet Instance.
            Deallocate a new individual Network Slice Subnet Instance
        """
        response_data = dict()
        response_data['status'] = OperationStatus.OPERATION_FAILED
        try:
            slice_id = kwargs['pk']
            if self.get_queryset().filter(instanceId=slice_id):
                response_data['status'] = OperationStatus.OPERATION_SUCCEEDED
                unit_query = self.get_queryset().filter(instanceId=slice_id)[0]
                slice_serializer = self.get_serializer(unit_query)
                service_plugin = slice_serializer.data['nfvoType'][0]
                parameter = {
                    'slice_template': slice_serializer.data['templateId'],
                    'slice_instance': slice_id,
                    'mano_template': False
                }
                plugin = importlib.import_module(
                    'nssmf.plugin.{}.{}.{}'.format(
                        service_plugin['name'],
                        service_plugin['deallocate_nssi'].split('/')[0],
                        service_plugin['deallocate_nssi'].split('/')[1].split('.')[0]))
                nfvo_plugin = plugin.NFVOPlugin(service_plugin['nm_host'],
                                                service_plugin['nfvo_host'],
                                                service_plugin['subscription_host'],
                                                parameter)
                nfvo_plugin.deallocate_nssi()
                unit_query.instanceId.remove(slice_id)
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data, status=400)
        except TypeError:
            return JsonResponse(response_data, status=400)

class ServiceMappingPluginView(ModelViewSet):
    """ Service Mapping Plugin framework
    """
    queryset = ServiceMappingPluginModel.objects.all()
    serializer_class = ServiceMappingPluginSerializer
    response_data = dict()

    def list(self, request, *args, **kwargs):
        """
            Read information about an individual Service Mapping Plugin resource.
            The GET method reads the information of a Service Mapping Plugin.
        """
        return super().list(self, request, args, kwargs)

    def create(self, request, *args, **kwargs):
        """
            Create a new individual Service Mapping Plugin resource.
            The POST method creates a new individual Service Mapping Plugin resource.
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
            Query Service Mapping Plugin information.
            The GET method queries the information of the Service Mapping Plugin \
            matching the filter.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update information about an individual Service Mapping Plugin resource.
            The PATCH method updates the information of a Service Mapping Plugin.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
            Delete an individual Service Mapping Plugin.
            The DELETE method deletes an individual Service Mapping Plugin resource.
        """
        self_object = self.get_object()
        file = self_object.pluginFile
        if file:
            file_folder = os.path.join(
                settings.PLUGIN_ROOT,
                self_object.name
            )
            shutil.rmtree(file_folder)
            file.delete()
        super().destroy(self, request, args, kwargs)
        self.response_data['status'] = PluginOperationStatus.DELETE
        return JsonResponse(self.response_data, status=200)

    @action(detail=False, methods=['get'], url_path='download/(?P<name>(.)*)/(?P<filename>(.)*)')
    def download(self, request, *args, **kwargs):
        """
            Download an individual Service Mapping Plugin.
            The GET method reads the content of the Service Mapping Plugin.
        """
        try:
            plugin_obj = ServiceMappingPluginModel.objects.get(name=kwargs['name'])
            with plugin_obj.pluginFile.open() as f:
                response = HttpResponse(f.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + kwargs['filename']
                return response
        except IOError:
            raise Http404
