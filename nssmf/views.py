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
import re
import shutil
import subprocess
import threading
import zipfile

import yaml
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet

from free5gmano import settings
from nssmf.models import ServiceMappingPluginModel, GenericTemplate, SliceTemplate
from nssmf.serializers import ServiceMappingPluginSerializer, GenericTemplateSerializer, \
    SliceTemplateSerializer
from nssmf.utils import self_zipfile

from nssmf.utils.command_ouput_socket import CommandOutputSocket


class Provisioning(ModelViewSet):

    @csrf_exempt
    @action(detail=True, methods='POST', name='allocate_nssi')
    def allocate_nssi(self, request, **kwargs):
        global ret
        response_data = {'status': 'OperationFailed'}
        request_data = JSONParser().parse(request)

        try:
            _id = request_data['attributeListIn']['template_id'].replace('-', '')
            slice_template_model = SliceTemplate.objects.extra(
                where=[SliceTemplate._meta.pk.verbose_name + "='" + _id + "'"])
            slice_template_serializer = SliceTemplateSerializer(slice_template_model, many=True)
            if slice_template_serializer.data.__len__() == 0:
                raise ValueError

            service_mapping_plugin_model = ServiceMappingPluginModel.objects.extra(
                where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                       slice_template_serializer.data[0]['nfvo'] + "'"])
            service_mapping_plugin_serializer = \
                ServiceMappingPluginSerializer(service_mapping_plugin_model, many=True)
            if service_mapping_plugin_serializer.data.__len__() == 0:
                raise ValueError

            ret_code, ret = subprocess.getstatusoutput(
                'python3 ' + os.path.join(settings.BASE_DIR, 'nssmf', 'plugin',
                                          service_mapping_plugin_serializer.data['name'],
                                          service_mapping_plugin_serializer.data['allocate_nssi']) +
                ' -v ' +
                str(os.path.join(settings.DATA_DIR, "VNF",
                                 eval(slice_template_serializer.data[0]['reference'])['VNF'][0])) +
                ' -n ' +
                str(os.path.join(settings.DATA_DIR, "NSD",
                                 eval(slice_template_serializer.data[0]['reference'])['NSD'][0])))
            print(ret)
        except IOError as e:
            print(e)
            return JsonResponse(response_data, status=400)
        except ValueError:
            print('This template/Plug-in is not existed.')

        return JsonResponse({'status': 'OperationSucceeded'}, status=200)

    @csrf_exempt
    @action(detail=True, methods='POST', name='allocate_nssi_for_command')
    def allocate_nssi_for_command(self, request, **kwargs):
        response_data = {'status': 'OperationFailed'}
        request_data = JSONParser().parse(request)

        try:
            _id = request_data['attributeListIn']['template_id'].replace('-', '')
            slice_template_model = SliceTemplate.objects.extra(
                where=[SliceTemplate._meta.pk.verbose_name + "='" + _id + "'"])
            slice_template_serializer = SliceTemplateSerializer(slice_template_model, many=True)
            if slice_template_serializer.data.__len__() == 0:
                raise ValueError

            service_mapping_plugin_model = ServiceMappingPluginModel.objects.extra(
                where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                       slice_template_serializer.data[0]['nfvo'] + "'"])
            service_mapping_plugin_serializer = \
                ServiceMappingPluginSerializer(service_mapping_plugin_model, many=True)
            if service_mapping_plugin_serializer.data.__len__() == 0:
                raise ValueError

            plugin_thread = threading.Thread(target=allocate_threading,
                                             args=(
                                                 service_mapping_plugin_serializer.data,
                                                 slice_template_serializer.data[0]['reference']))
            plugin_thread.start()
        except ValueError:
            print('This template/Plug-in is not existed.')
            return JsonResponse(response_data, status=400)
        except IOError:
            return JsonResponse(response_data, status=400)

        return JsonResponse({'status': 'OperationSucceeded'}, status=200)


class Template(ModelViewSet):

    @csrf_exempt
    @action(detail=True, methods='POST')
    def create(self, request, **kwargs):
        # The POST method is used to create a new Generic Template resource.
        if kwargs['id']:
            response = {
                "attributeListOut": {
                    "templateId": "Shouldn't be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)
        # Check and Save data
        if request.data:
            # Check type setting
            if request.data['type'] not in \
                    ('VNF', 'NSD', 'all'):
                response = {
                    "attributeListOut": {
                        "type": "Invalid type"
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)

            # Check nfvo setting
            if not request.data['nfvo']:
                response = {
                    "attributeListOut": {
                        "nfvo": "Should be provide nfvo"
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response)

            if request.data['type'] == 'all':
                response_all_list = list()
                for _ in ('VNF', 'NSD'):
                    generic_template = GenericTemplate()
                    request.data[
                        'download_link'] = request.build_absolute_uri() + 'download/' + str(
                        generic_template.templateId)
                    request.data['type'] = _
                    serializer = GenericTemplateSerializer(generic_template, data=request.data,
                                                           partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        response = serializer.data
                        response_all_list.append(response)
                    else:
                        response = {
                            "status": "OperationFailed"
                        }
                        return JsonResponse(response, status=400)
                return JsonResponse(response_all_list, safe=False)
            else:
                generic_template = GenericTemplate()
                request.data['download_link'] = request.build_absolute_uri() + 'download/' + str(
                    generic_template.templateId)
                serializer = GenericTemplateSerializer(generic_template, data=request.data,
                                                       partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response = serializer.data
                    return JsonResponse(response)
                else:
                    response = {
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response, status=400)
        else:
            response = {
                "attributeListOut": {
                    "nfvo": "xos_nfvo | tacker_nfvo | <other_nfvo>",
                    "type": "VNF | NSD | all"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='GET')
    def read(self, request, **kwargs):
        # The GET method reads information about an Generic Template resource.
        if kwargs['id']:
            try:
                generic_template = GenericTemplate.objects.get(templateId=kwargs['id'])
                serializer = GenericTemplateSerializer(generic_template)
                response = serializer.data
            except GenericTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            return JsonResponse([response], safe=False)
        else:
            try:
                generic_template = GenericTemplate.objects.all()
                response = []
                for i in generic_template.values():
                    i['templateId'] = str(i['templateId'])
                    response.append(i)
            except GenericTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            return JsonResponse(response, safe=False)

    @csrf_exempt
    @action(detail=True, methods='PATCH')
    def update(self, request, **kwargs):
        if kwargs['id']:
            # Check template is exist
            try:
                generic_template = GenericTemplate.objects.get(templateId=kwargs['id'])
            except GenericTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            # Check and Save data
            if request.data:
                # Check type setting
                if request.data['type'] not in \
                        ('VNF', 'NSD'):
                    response = {
                        "attributeListOut": {
                            "type": "Invalid type"
                        },
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response, status=400)

                # Check nfvo setting
                if not request.data['nfvo']:
                    response = {
                        "attributeListOut": {
                            "nfvo": "Should be provide nfvo"
                        },
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response)

                request.data['download_link'] = request.build_absolute_uri() + 'download/' + str(
                    generic_template.templateId)
                serializer = GenericTemplateSerializer(generic_template, data=request.data,
                                                       partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response = serializer.data
                    return JsonResponse(response)
                else:
                    response = {
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response, status=400)
            else:
                response = {
                    "attributeListOut": {
                        "nfvo": "xos_nfvo | tacker_nfvo | <other_nfvo>",
                        "type": "VNF | NSD"
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
        else:
            response = {
                "attributeListOut": {
                    "templateId": "Should be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='DELETE')
    def delete(self, request, **kwargs):
        # The DELETE method deletes an Generic Template resource.
        if kwargs['id']:
            try:
                generic_template = GenericTemplate.objects.get(templateId=kwargs['id'])
                # TODO: NRM
                if generic_template.status == 'onboard':
                    # Delete onboard directory
                    try:
                        print('Delete directory...')
                        os.removedirs(os.path.join(settings.DATA_DIR, generic_template.type,
                                                   str(kwargs['id'])))
                        generic_template.delete()
                    except OSError as e:
                        print(e)
                        response = {
                            "status": "OperationFailed"
                        }
                        return JsonResponse(response, status=400)
                    else:
                        response = {
                            "status": "OperationSucceeded"
                        }
                        return JsonResponse(response)
                else:
                    generic_template.delete()
                    response = {
                        "status": "OperationSucceeded"
                    }
                    return JsonResponse(response)
            except GenericTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
        else:
            response = {
                "attributeListOut": {
                    "templateId": "Should be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='PUT')
    def onboard(self, request, **kwargs):
        try:
            generic_template = GenericTemplate.objects.get(templateId=kwargs['id'])
        except GenericTemplate.DoesNotExist:
            response = {
                "templateId": "Template does not exist",
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)
        if generic_template.status == 'onboard':
            response = {
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)
        generic_template.status = 'onboard'
        data = request.FILES['file']
        buffer = data.read()
        self_zipfile.decompression(buffer, kwargs['id'], generic_template.type)
        serializer = GenericTemplateSerializer(generic_template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Delete download zip file
            try:
                os.remove(os.path.join(os.getcwd(), "nssmf", 'template_example',
                                       generic_template.type + '.zip'))
            except OSError:
                pass
            response = {
                "status": "OperationSucceeded"
            }
            return JsonResponse(response)
        else:
            response = {
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='GET')
    def download(self, request, **kwargs):
        # The GET method download information about an Generic Template resource.
        if kwargs['id']:
            generic_template = GenericTemplate.objects.get(templateId=kwargs['id'])
            generic_template.status = 'download'
            generic_template.save()
            # TODO: NRM
            path = self_zipfile.compression('template_example', '', '', generic_template.type)
            with open(path, "rb") as zip_file:
                return HttpResponse(zip_file.read(), content_type="application/zip")
        else:
            response = {
                "attributeListOut": {
                    "templateId": "Should be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)


class NetworkSliceTemplate(ModelViewSet):

    @csrf_exempt
    @action(detail=True, methods='POST')
    def create(self, request, **kwargs):
        # The POST method is used to create a new Network Slice Template resource.
        if kwargs['id']:
            response = {
                "attributeListOut": {
                    "templateId": "Shouldn't be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)
        # Check and Save data
        if request.data:
            refer_response = list()
            # Check nfvo setting
            if not request.data['nfvo']:
                response = {
                    "attributeListOut": {
                        "nfvo": "Should be provide nfvo"
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response)
            # Check reference setting
            if request.data['reference']:
                vnf_id_list = list()
                nsd_id_list = list()
                for refer_id in request.data['reference']:
                    if re.search(r'(\w{8}(-\w{4}){3}-\w{12})$', refer_id):
                        try:
                            reference_template = GenericTemplate.objects.get(templateId=refer_id)
                        except GenericTemplate.DoesNotExist:
                            response = {
                                "attributeListOut": {
                                    "reference": "Invalid reference"
                                },
                                "status": "OperationFailed"
                            }
                            return JsonResponse(response, status=400)
                        if reference_template.type == 'VNF':
                            vnf_id_list.append(str(reference_template.templateId))
                        elif reference_template.type == 'NSD':
                            nsd_id_list.append(str(reference_template.templateId))

                        refer_response = {
                            'VNF': vnf_id_list,
                            'NSD': nsd_id_list
                        }
                    else:
                        response = {
                            "attributeListOut": {
                                "reference": "Reference should be uuid"
                            },
                            "status": "OperationFailed"
                        }
                        return JsonResponse(response, status=400)
            else:
                response = {
                    "attributeListOut": {
                        "reference": "Should be provide reference"
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            # Save data
            if refer_response:
                request.data['reference'] = str(refer_response)
            slice_template = SliceTemplate()
            serializer = SliceTemplateSerializer(slice_template, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response = serializer.data
                response['reference'] = eval(response['reference'])
                return JsonResponse(response)
            else:
                response = {
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
        else:
            response = {
                "attributeListOut": {
                    "description": "<Some slice description>",
                    "nfvo": "xos_nfvo | tacker_nfvo | <other_nfvo>",
                    "reference": ["<refer_uuid>"]
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='GET')
    def read(self, request, **kwargs):
        # The GET method reads information about an Network Slice Template resource.
        if kwargs['id']:
            try:
                slice_template = SliceTemplate.objects.get(templateId=kwargs['id'])
                serializer = SliceTemplateSerializer(slice_template)
                response = serializer.data
                response['reference'] = eval(response['reference'])
            except SliceTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            return JsonResponse([], safe=False)
        else:
            try:
                slice_template = SliceTemplate.objects.all()
                response = []
                for i in slice_template.values():
                    i['templateId'] = str(i['templateId'])
                    i['reference'] = eval(i['reference'])
                    response.append(i)
            except SliceTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            return JsonResponse(response, safe=False)

    @csrf_exempt
    @action(detail=True, methods='PATCH')
    def update(self, request, **kwargs):
        # Modify the user defined data of an Network Slice Template resource
        if kwargs['id']:
            # Check template is exist
            try:
                slice_template = SliceTemplate.objects.get(templateId=kwargs['id'])
            except SliceTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            # Check and Save data
            if request.data:
                refer_response = list()
                # Check nfvo setting
                if not request.data['nfvo']:
                    response = {
                        "attributeListOut": {
                            "nfvo": "Should be provide nfvo"
                        },
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response)
                # Check and Reorganization reference setting
                if request.data['reference']:
                    vnf_id_list = list()
                    nsd_id_list = list()
                    for refer_id in request.data['reference']:
                        if re.search(r'(\w{8}(-\w{4}){3}-\w{12})$', refer_id):
                            try:
                                reference_template = GenericTemplate.objects.get(
                                    templateId=refer_id)
                            except GenericTemplate.DoesNotExist:
                                response = {
                                    "attributeListOut": {
                                        "reference": "Invalid reference"
                                    },
                                    "status": "OperationFailed"
                                }
                                return JsonResponse(response, status=400)
                            if reference_template.type == 'VNF':
                                vnf_id_list.append(str(reference_template.templateId))
                            elif reference_template.type == 'NSD':
                                nsd_id_list.append(str(reference_template.templateId))

                            refer_response = {
                                'VNF': vnf_id_list,
                                'NSD': nsd_id_list
                            }
                        else:
                            response = {
                                "attributeListOut": {
                                    "reference": "Reference should be uuid"
                                },
                                "status": "OperationFailed"
                            }
                            return JsonResponse(response, status=400)
                # Save data
                if refer_response:
                    request.data['reference'] = str(refer_response)
                serializer = SliceTemplateSerializer(slice_template, data=request.data,
                                                     partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response = serializer.data
                    return JsonResponse(response)
                else:
                    response = {
                        "status": "OperationFailed"
                    }
                    return JsonResponse(response, status=400)
            else:
                response = {
                    "attributeListOut": {
                        "description": "<Some slice description>",
                        "nfvo": "xos_nfvo | tacker_nfvo | <other_nfvo>",
                        "reference": ["<refer_uuid>"]
                    },
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
        else:
            response = {
                "attributeListOut": {
                    "templateId": "Should be provide templateId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='DELETE')
    def delete(self, request, **kwargs):
        # The DELETE method deletes an Network Slice Template resource.
        if kwargs['id']:
            try:
                slice_template = SliceTemplate.objects.get(templateId=kwargs['id'])
            except GenericTemplate.DoesNotExist:
                response = {
                    "templateId": "Template does not exist",
                    "status": "OperationFailed"
                }
                return JsonResponse(response, status=400)
            slice_template.delete()
            response = {
                "status": "OperationSucceeded"
            }
            return JsonResponse(response)
        else:
            response = {
                "attributeListOut": {
                    "templateId": "Should be provide tId"
                },
                "status": "OperationFailed"
            }
            return JsonResponse(response, status=400)


class ServiceMappingPlugin(ModelViewSet):

    @csrf_exempt
    @action(detail=True, methods='POST', name='registerPlugin')
    def register_plugin(self, request, **kwargs):
        try:
            model = ServiceMappingPluginModel.objects.extra(
                where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                       request.data['name'] + "'"])
            serializer = ServiceMappingPluginSerializer(model, many=True)
            if serializer.data.__len__() != 0:
                raise ValueError

            plugin_path = os.path.join(settings.BASE_DIR, 'nssmf', 'plugin')
            extract_path = os.path.join(plugin_path, request.data['name'])

            with zipfile.ZipFile(request.data['file'].file) as zip_file:
                zip_file.extractall(path=extract_path)

            with open(os.path.join(extract_path, 'config.yaml'), 'r') as stream:
                config = yaml.safe_load(stream)
                plugin = {
                    'name': request.data['name'],
                    'allocate_nssi': config['allocate_file'],
                    'deallocate_nssi': config['deallocate_file']
                }

                service_mapping_plugin_serializer = ServiceMappingPluginSerializer(data=plugin)
                if service_mapping_plugin_serializer.is_valid():
                    service_mapping_plugin_serializer.save()
                    response = {'status': 'Register Success'}
                    return JsonResponse(response, status=200)

            response = {'status': 'Register Failed.'}
            return JsonResponse(response, status=400)
        except yaml.YAMLError:
            response = {'status': 'Register Failed. config.yaml not found'}
            return JsonResponse(response, status=400)
        except ValueError:
            response = {'status': 'Register Failed. Name is duplicate'}
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='GET', name='getPluginList')
    def get_plugin_list(self, request, **kwargs):
        try:
            if not kwargs['plugin_name']:
                model = ServiceMappingPluginModel.objects.all()
            else:
                model = ServiceMappingPluginModel.objects.extra(
                    where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                           kwargs['plugin_name'] + "'"])
            serializer = ServiceMappingPluginSerializer(model, many=True)

            response = {'status': 'Succeed', 'plugin_list': serializer.data}
            return JsonResponse(response, status=200)
        except KeyError:
            response = {'status': 'No result'}
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='PATCH', name='modifyPlugin')
    def update_plugin(self, request, **kwargs):
        try:
            model = ServiceMappingPluginModel.objects.extra(
                where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                       kwargs['plugin_name'] + "'"])
            serializer = ServiceMappingPluginSerializer(model, many=True)
            if serializer.data.__len__() == 0:
                raise KeyError

            shutil.rmtree(os.path.join(settings.BASE_DIR, 'nssmf', 'plugin', kwargs['plugin_name']))
            plugin_path = os.path.join(settings.BASE_DIR, 'nssmf', 'plugin')
            extract_path = os.path.join(plugin_path, kwargs['plugin_name'])

            with zipfile.ZipFile(request.data['file'].file) as zip_file:
                zip_file.extractall(path=extract_path)

            with open(os.path.join(extract_path, 'config.yaml'), 'r') as stream:
                config = yaml.safe_load(stream)
                plugin = {
                    'allocate_nssi': config['allocate_file'],
                    'deallocate_nssi': config['deallocate_file']
                }

                model.update(**plugin)
                response = {'status': 'Update Succeed'}
                return JsonResponse(response, status=200)
        except yaml.YAMLError:
            response = {'status': 'Update Failed. config.yaml not found'}
            return JsonResponse(response, status=400)
        except KeyError:
            response = {'status': 'No such Plug-in'}
            return JsonResponse(response, status=400)

    @csrf_exempt
    @action(detail=True, methods='DELETE', name='deletePlugin')
    def delete_plugin(self, request, **kwargs):
        try:
            model = ServiceMappingPluginModel.objects.extra(
                where=[ServiceMappingPluginModel._meta.pk.verbose_name + "='" +
                       kwargs['plugin_name'] + "'"])
            serializer = ServiceMappingPluginSerializer(model, many=True)
            if serializer.data.__len__() == 0:
                raise KeyError

            response = {'status': 'Delete Succeed', 'plugin_list': serializer.data}
            model.delete()
            shutil.rmtree(os.path.join(settings.BASE_DIR, 'nssmf', 'plugin', kwargs['plugin_name']))
            return JsonResponse(response, status=200)
        except KeyError:
            response = {'status': 'No such Plug-in'}
            return JsonResponse(response, status=400)


def allocate_threading(plugin_data, template_object):
    command_output_socket = CommandOutputSocket()
    try:
        client, addr = command_output_socket.accept()
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

        command = 'python3 ' + os.path.join(settings.BASE_DIR, 'nssmf', 'plugin',
                                            plugin_data[0]['name'],
                                            plugin_data[0]['allocate_nssi']) + \
                  ' -v ' + \
                  str(os.path.join(settings.DATA_DIR, "VNF", eval(template_object)['VNF'][0])) + \
                  ' -n ' + \
                  str(os.path.join(settings.DATA_DIR, "NSD", eval(template_object)['NSD'][0]))

        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
        for line in iter(p.stdout.readline, b''):
            print(line)
            client.send(line)
        command_output_socket.close()
        client.close()
    except TimeoutError:
        print("Socket Timeout")
