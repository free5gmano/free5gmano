import ast

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet

from moi.models import *
from moi.serializers import *
from moi.enums import Modification, Scope


class ObjectManagement(ModelViewSet):
    queryset = NetworkSliceSubnet.objects.all()
    serializer_class = NetworkSliceSubnetSerializer

    @csrf_exempt
    @action(detail=True, methods='PUT', name='createMOI')
    def create_moi(self, request, **kwargs):
        global moi_object_serializer

        data = JSONParser().parse(request)
        response_data = {'status': 'OperationFailed'}

        moi_serializer_class = globals()[kwargs['className'] + "Serializer"]
        moi_object_serializer = moi_serializer_class(data=data['attributeListIn'])
        if moi_object_serializer.is_valid():
            moi_object_serializer.save()
            response_data = {'status': 'OperationSucceeded',
                             'attributeListOut': moi_object_serializer.data}
            return JsonResponse(response_data, status=201)

        return JsonResponse(response_data, status=400)

    @csrf_exempt
    @action(detail=True, methods='GET', name='getMOIAttributes')
    def get_moi_attributes(self, request, **kwargs):
        global moi_object
        global moi_object_serializer
        response_data = {'status': 'OperationFailed'}
        scope_seq = ast.literal_eval(request.query_params.get('scope'))
        moi_model_class = globals()[kwargs['className']]
        moi_serializer_class = globals()[kwargs['className'] + "Serializer"]

        if not Scope.has_value(scope_seq[0]):
            return JsonResponse(response_data, status=400)

        moi_serializer_class.Meta.depth = get_scope_level(scope_seq[0], scope_seq[1])

        try:
            if kwargs['id'] == "*" and request.query_params.get('filter') is None:
                moi_object = moi_model_class.objects.all()
            elif request.query_params.get('filter') is None or \
                    request.query_params.get('filter') == "":
                _id = kwargs['id'].replace('-', '')
                moi_object = moi_model_class.objects.extra(
                    where=[moi_model_class._meta.pk.verbose_name + "='" + _id + "'"])
            else:
                moi_object = moi_model_class.objects.extra(
                    where=[request.query_params.get('filter')])

            moi_object_serializer = moi_serializer_class(moi_object, many=True)
        except moi_model_class.DoesNotExist:
            return JsonResponse(response_data, status=400)

        response_data = {'status': 'OperationSucceeded',
                         'attributeListOut': moi_object_serializer.data}

        return JsonResponse(response_data, status=200)

    @csrf_exempt
    @action(detail=True, methods='PATCH', name='modifyMOIAttributes')
    def modify_moi_attributes(self, request, **kwargs):
        global moi_object
        global moi_object_serializer
        response_data = {'status': 'OperationFailed'}
        scope_seq = ast.literal_eval(request.query_params.get('scope'))
        moi_model_class = globals()[kwargs['className']]
        moi_serializer_class = globals()[kwargs['className'] + "Serializer"]

        if not Scope.has_value(scope_seq[0]):
            return JsonResponse(response_data, status=400)

        moi_serializer_class.Meta.depth = get_scope_level(scope_seq[0], scope_seq[1])

        if len(request.data['modificationList']) == 2 and not Modification.has_value(
                request.data['modificationList'][1]):
            return JsonResponse(response_data, status=400)
        elif len(request.data['modificationList']) == 3 and not Modification.has_value(
                request.data['modificationList'][2]):
            return JsonResponse(response_data, status=400)

        try:
            if kwargs['id'] == "*" and request.query_params.get('filter') is None:
                moi_object = moi_model_class.objects.all()
            elif request.query_params.get('filter') is None or \
                    request.query_params.get('filter') == "":
                _id = kwargs['id'].replace('-', '')
                moi_object = moi_model_class.objects.extra(
                    where=[moi_model_class._meta.pk.verbose_name + "='" + _id + "'"])
            else:
                moi_object = moi_model_class.objects.extra(
                    where=[request.query_params.get('filter')])

            moi_object_serializer = moi_serializer_class(moi_object, many=True)

            operator_index = len(request.data['modificationList']) - 1

            moi_object_serializer = moi_serializer_class(moi_object, many=True)
            response_data = {'status': 'OperationSucceeded',
                             'attributeListOut': moi_object_serializer.data}
            update(moi_object, request.data, request.data['modificationList'][operator_index])
        except moi_model_class.DoesNotExist:
            return JsonResponse(response_data, status=400)
        except Exception as ex:
            print(ex)
            return JsonResponse(response_data, status=400)
        return JsonResponse(response_data, status=200)

    @csrf_exempt
    @action(detail=True, methods='DELETE', name='deleteMOI')
    def delete_moi(self, request, **kwargs):
        global moi_object
        global moi_object_serializer
        response_data = {'status': 'OperationFailed'}
        scope_seq = ast.literal_eval(request.query_params.get('scope'))
        moi_model_class = globals()[kwargs['className']]
        moi_serializer_class = globals()[kwargs['className'] + "Serializer"]

        if not Scope.has_value(scope_seq[0]):
            return JsonResponse(response_data, status=400)

        moi_serializer_class.Meta.depth = get_scope_level(scope_seq[0], scope_seq[1])

        try:
            if kwargs['id'] == "*" and request.query_params.get('filter') is None:
                moi_object = moi_model_class.objects.all()
            elif request.query_params.get('filter') is None or \
                    request.query_params.get('filter') == "":
                _id = kwargs['id'].replace('-', '')
                moi_object = moi_model_class.objects.extra(
                    where=[moi_model_class._meta.pk.verbose_name + "='" + _id + "'"])
            else:
                moi_object = moi_model_class.objects.extra(
                    where=[request.query_params.get('filter')])

            moi_object_serializer = moi_serializer_class(moi_object, many=True)
        except moi_model_class.DoesNotExist:
            return JsonResponse(response_data, status=400)

        response_data = {'status': 'OperationSucceeded', 'deletionList': moi_object_serializer.data}
        moi_object.delete()
        return JsonResponse(response_data, status=200)

    def subscribe_moi(self):
        pass

    def unsubscribe_moi(self):
        pass


def get_scope_level(level_selection, level):
    if level_selection == 'BASE_ONLY':
        return 0
    elif level_selection == 'BASE_NTH_LEVEL':
        return level
    elif level_selection == 'BASE_SUBTREE':
        return level + 1
    elif level_selection == 'BASE_ALL':
        return 10


def update(moi_object_data, data, operator):
    global modification_list
    global moi_object_list

    if operator != 'SET_TO_DEFAULT':
        modification_list = dict()
        for i in range(data['modificationList'][0].__len__()):
            modification_list[data['modificationList'][0][i]] = data['modificationList'][1][i]

    if operator == 'REPLACE':
        moi_object_data.update(**modification_list)
    elif operator == 'ADD_VALUES':
        moi_object_list = [nssi for nssi in moi_object_data]
        for i in range(moi_object_list.__len__()):
            for j in range(data['modificationList'][0].__len__()):
                str_list = list(data['modificationList'][0][j])
                str_list[0] = str_list[0].upper()
                model_class_name = "".join(str_list)
                moi_object_list[i].__getattribute__(data['modificationList'][0][j]).add(
                    globals()[model_class_name].objects.get(pk=data['modificationList'][1][j]))
    elif operator == 'REMOVE_VALUES':
        moi_object_list = [moi for moi in moi_object_data]
        for i in range(moi_object_list.__len__()):
            for j in range(data['modificationList'][0].__len__()):
                str_list = list(data['modificationList'][0][j])
                str_list[0] = str_list[0].upper()
                model_class_name = "".join(str_list)
                moi_object_list[i].__getattribute__(data['modificationList'][0][j]).remove(
                    globals()[model_class_name].objects.get(pk=data['modificationList'][1][j]))
    elif operator == 'SET_TO_DEFAULT':
        moi_object_list = [nssi for nssi in moi_object_data]
        for i in range(moi_object_list.__len__()):
            default_value = moi_object_data.model._meta.get_field(
                data['modificationList'][0][i]).default
            modification_list = {
                data['modificationList'][0][i]:
                    default_value
            }
        moi_object_data.update(**modification_list)
