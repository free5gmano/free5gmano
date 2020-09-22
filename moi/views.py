import ast
import threading
import datetime
import base64
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.apps import apps

from moi.models import *
from moi.serializers import *
from moi.enums import Modification, Scope, OperationStatus
from free5gmano.settings import THREAD_POOL
from nssmf.models import SliceTemplate
from nssmf.serializers import SliceTemplateRelationSerializer
from rest_framework.response import Response

class TaskThread(threading.Thread):
    def __init__(self, time_tick, callback_uri, notify_data):
        super().__init__()
        self.time_tick = time_tick
        self.callback_uri = callback_uri
        self.notify_data = notify_data
        self.stop = False

    def run(self):
        import time
        # Get MOI values list
        model = apps.get_model('moi', self.notify_data['objectClass'])
        pre_value_list = list()
        object_queryset = model.objects.values()
        for query in object_queryset:
            if str(query[model._meta.pk.name]) in self.notify_data['objectInstanceInfos']:
                pre_value_list.append(query)

        if self.notify_data['notificationType'] == 'notifyMOIDeletion':
            while 1:
                time.sleep(self.time_tick)
                object_queryset = model.objects.values()
                condition = list()
                for query in object_queryset:
                    condition.append(str(query[model._meta.pk.name]) in
                                     self.notify_data['objectInstanceInfos'])
                if not any(condition):
                    # Notify calluri
                    print('Delete Notify')
                    header = {"Content-Type": "application/vnd.kafka.v1+json"}
                    data = {
                        "notificationId": self.notify_data['notificationId'],
                        "notificationType": self.notify_data['notificationType']
                    }
                    b64_data = base64.b64encode(str(data).encode())
                    _data = {"records": [{"value": b64_data.decode()}]}
                    requests.post(url=self.callback_uri, json=_data, headers=header)
                    break
        elif self.notify_data['notificationType'] == 'notifyMOIAttributeValueChanges':
            while not self.stop:
                time.sleep(self.time_tick)
                value_list = list()
                object_queryset = model.objects.values()
                for query in object_queryset:
                    if str(query[model._meta.pk.name]) in self.notify_data['objectInstanceInfos']:
                        value_list.append(query)

                for i in range(len(value_list)):
                    if value_list[i] == pre_value_list[i]:
                        pass
                    else:
                        print('Change MOI')
                        # Notify callbackuri
                        header = {"Content-Type": "application/vnd.kafka.v1+json"}
                        data = {
                            "notificationId": self.notify_data['notificationId'],
                            "notificationType": self.notify_data['notificationType']
                        }
                        b64_data = base64.b64encode(str(data).encode())
                        _data = {"records": [{"value": b64_data.decode()}]}
                        requests.post(url=self.callback_uri, json=_data, headers=header)
                pre_value_list = value_list
        elif self.notify_data['notificationType'] == 'notifyMOICreation':
            record_count = model.objects.count()
            while 1:
                time.sleep(self.time_tick)
                if record_count >= model.objects.count():
                    pass
                else:
                    print('Create MOI')
                    # Notify callbackuri
                    header = {"Content-Type": "application/vnd.kafka.v1+json"}
                    data = {
                        "notificationId": self.notify_data['notificationId'],
                        "notificationType": self.notify_data['notificationType']
                    }
                    b64_data = base64.b64encode(str(data).encode())
                    _data = {"records": [{"value": b64_data.decode()}]}
                    requests.post(url=self.callback_uri, json=_data, headers=header)
                    break


class MultipleSerializerViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return SubscriptionRetrieveSerializer
        return SubscriptionSerializer

    
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


class SubscriptionView(MultipleSerializerViewSet):
    """ Subscription Information
    """
    queryset = Subscription.objects.all()
    serializer_class = MultipleSerializerViewSet.get_serializer_class

    def list(self, request, *args, **kwargs):
        """
            Query Subscription information.

            The GET method queries the information of the Subscription matching the filter.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
            Create a new individual Subscription resource.

            The POST method creates a new individual Subscription resource.
        """
        response = super().create(request, *args, **kwargs)
        for notification in request.data['filter']:
            notify_obj = CommonNotification.objects.get(notificationId=notification)
            notify_data = {
                "notificationId": notify_obj.notificationId,
                "notificationType": notify_obj.notificationType,
                "objectInstanceInfos": eval(notify_obj.objectInstanceInfos),
                "objectClass": notify_obj.objectClass,
                "additionalText": eval(notify_obj.additionalText)
            }
            THREAD_POOL[notification] = TaskThread(request.data['timeTick'],
                                                   request.data['callbackUri'],
                                                   notify_data)
            THREAD_POOL[notification].start()
        return response

    def retrieve(self, request, *args, **kwargs):
        """
            Read information about an individual Subscription resource.

            The GET method reads the information of a Subscription.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update information about an individual Subscription resource.

            The PATCH method updates the information of a Subscription.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
            Delete an individual Subscription.

            The DELETE method deletes an individual Subscription resource.
        """
        for notification in self.get_object().filter.all():
            if str(notification.notificationId) in THREAD_POOL:
                task = THREAD_POOL[str(notification.notificationId)]
                task.stop = True
        return super().destroy(request, *args, **kwargs)


class NotificationView(ModelViewSet):
    """ Notification Information
    """
    queryset = CommonNotification.objects.all()
    serializer_class = CommonNotificationSerializer

    def check(self, request):
        # Check objectInstanceInfos (type: list) is exist in other CommonNotification
        notify_queryset = \
            self.queryset.filter(notificationType=request.data['notificationType'])
        for query in request.data['objectInstanceInfos']:
            notify_queryset = notify_queryset.filter(
                objectInstanceInfos__contains=query)
        # Check additionalText (type: dict) is exist in other CommonNotification
        for query in notify_queryset:
            if eval(query.additionalText) == request.data['additionalText']:
                return notify_queryset
        notify_queryset = list()
        return notify_queryset

    def list(self, request, *args, **kwargs):
        """
            Query Notification information.

            The GET method queries the information of the Notification matching the filter.
        """
        response = list()
        queryset = self.filter_queryset(self.get_queryset())
        for query in queryset.values():
            query['objectInstanceInfos'] = eval(query['objectInstanceInfos'])
            query['additionalText'] = eval(query['additionalText'])
            response.append(query)
        return Response(response)

    def create(self, request, *args, **kwargs):
        """
            Create a new individual Notification resource.

            The POST method creates a new individual Notification resource.
        """
        response = {'status': OperationStatus.OperationFailedExistingSubscription}
        notify_queryset = self.check(request)
        if notify_queryset:
            return Response(response, status=500)
        request.data['objectInstanceInfos'] = str(request.data['objectInstanceInfos'])
        request.data['additionalText'] = str(request.data['additionalText'])
        super().create(request, *args, **kwargs)
        return Response(status=201)

    def retrieve(self, request, *args, **kwargs):
        """
            Read information about an individual Notification resource.

            The GET method reads the information of a Notification.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
            Update information about an individual Notification resource.

            The PATCH method updates the information of a Notification.
        """
        response = {'status': OperationStatus.OperationFailedExistingSubscription}
        notify_queryset = self.check(request)
        if notify_queryset:
            return Response(response, status=500)
        request.data['objectInstanceInfos'] = str(request.data['objectInstanceInfos'])
        request.data['additionalText'] = str(request.data['additionalText'])
        super().update(request, *args, **kwargs)
        return Response(status=200)

    def destroy(self, request, *args, **kwargs):
        """
            Delete an individual Notification.

            The DELETE method deletes an individual Notification resource.
        """
        return super().destroy(request, *args, **kwargs)
