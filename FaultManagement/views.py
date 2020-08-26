from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from FaultManagement.enums import *
from FaultManagement.models import *
from moi.models import NsInfo, NetworkSliceSubnet
from nssmf.models import SliceTemplate
from nssmf.models import ServiceMappingPluginModel
from FaultManagement.serializers import *
import requests
import json


class FaultSupervisionView(GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin):
    queryset = AlarmResource.objects.all()
    serializer_class = AlarmResourceSerializer

    def create(self, request, *args, **kwargs):
        """
            Add a comment to multiple alarms

            Add a comment to multiple alarms
        """
        pass
        # return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
            Retrieve alarms

            Retrieve the alarms identified by alarmAckState, href and filter.
        """
        service_mapping_list = ServiceMappingPluginModel.objects.values()
        if service_mapping_list:
            for _ in service_mapping_list:
                NFVO_HOST = _['nfvo_host']
                url = "http://{}/nsfm/v1/alarms".format(NFVO_HOST)
                response = requests.get(url).json()
                for alarm_data in response:
                    alarm_data['eventType'] = AlarmType.ProcessingErrorAlarm \
                        if alarm_data['eventType'] == 'PROCESSING_ERROR_ALARM' else ''
                    alarm_data['ackState'] = AlarmAckState.allUnacknowledgedAlarms \
                        if alarm_data['ackState'] == 'UNACKNOWLEDGED' else ''
                    alarm_data['perceivedSeverity'] = PerceivedSeverity.Critical \
                        if alarm_data['perceivedSeverity'] == 'CRITICAL' else ''
                    store_data = {
                        "alarmId": alarm_data['id'],
                        "alarmRaisedTime": alarm_data['alarmRaisedTime'],
                        "alarmChangedTime": alarm_data['alarmChangedTime'],
                        "alarmClearedTime": alarm_data['alarmClearedTime'],
                        "ackstate": alarm_data['ackState'],
                        "perceivedSeverity": alarm_data['perceivedSeverity'],
                        "alarmType": alarm_data['eventType'],
                        "probableCause": alarm_data['probableCause'],
                        "additionalText": alarm_data['faultDetails'],
                        "ackTime": alarm_data['eventTime'],
                        "serviceProvider": _['name']
                    }
                    alarm_obj = AlarmResource.objects.filter(alarmId=alarm_data['id'])
                    if alarm_obj:
                        serializer = AlarmResourceSerializer(alarm_obj[0],
                                                             data=store_data,
                                                             partial=True)
                    else:
                        serializer = AlarmResourceSerializer(data=store_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
            return super().list(request, *args, **kwargs)
        else:
            return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
            Get the alarm count per perceived severity


            tba
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Clear, acknowledge or unacknowledge multiple alarms

            tba
        """
        return super().update(request, *args, **kwargs)


class FaultSupervisionSubscriptionsView(GenericViewSet,
                                        mixins.ListModelMixin,
                                        mixins.DestroyModelMixin,
                                        mixins.CreateModelMixin):
    queryset = SubscriptionResource.objects.all()
    serializer_class = SubscriptionResourceSerializer

    def list(self, request, *args, **kwargs):
        """
            List a all subscription

            The GET method queries the information of the subscription the filter.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
            Create a single subscription

            To create a subscription the representation of the subscription is POSTed\
             on the /subscriptions collection resource.
        """

        for nssi_id in request.data['filter']['nsInstanceSubscriptionFilter']['nSSIId']:
            nssi_obj = NetworkSliceSubnet.objects.get(nssiId=nssi_id)
            print(nssi_obj.nsInfo.id)
            if nssi_obj:
                nsst_obj = SliceTemplate.objects.get(instanceId=nssi_id)
                NFVO_HOST = nsst_obj.nfvoType.values()[0]['nfvo_host']
                url = "http://{}/nsfm/v1/subscriptions/".format(NFVO_HOST)
                headers = {'Content-type': 'application/json'}
                data = {
                  "filter": {
                    "nsInstanceSubscriptionFilter": {
                        "nsInstanceIds": [str(nssi_obj.nsInfo.id)]
                    }
                  },
                  "callbackUri": request.data['callbackUri']
                }
                response = requests.post(url, data=json.dumps(data), headers=headers)
                print(response.json())
                header_obj = Header(notificationId=response.json()['id'],
                                    notificationType=response.json()['filter']['notificationTypes'],
                                    uri=request.data['callbackUri'])
                print(header_obj)
                header_obj.save()
                sub_obj = SubscriptionResource(header_obj.notificationId,
                                               filter=response.json()['filter'],
                                               timeTick=request.data['timeTick'],
                                               consumerReference=str(response.json())
                                               )
                sub_obj.save()
                res = {
                    "data": {
                        "notificationId": response.json()['id'],
                        "consumerReference": str(sub_obj.consumerReference),
                        "timeTick": sub_obj.timeTick,
                        "filter": sub_obj.filter
                    }
                }
                print(res)
                return JsonResponse(res, status=201)
            else:
                return Response("Not nsInstanceIds")

    def destroy(self, request, *args, **kwargs):
        """
            Delete a single subscription

            The subscription is deleted by deleting the corresponding subscription resource. \
            The resource to be deleted is identified with the path component of the URI.
        """
        nsi_id = eval(self.get_object().filter)['nsInstanceSubscriptionFilter']['nsInstanceIds'][0]
        nssi_obj = NetworkSliceSubnet.objects.get(nsInfo=nsi_id)
        nsst_obj = SliceTemplate.objects.get(instanceId=nssi_obj.nssiId)
        NFVO_HOST = nsst_obj.nfvoType.values()[0]['nfvo_host']
        url = "http://{}/nsfm/v1/subscriptions/{}/".format(NFVO_HOST, kwargs['pk'])
        response = requests.delete(url)
        if response.status_code == 204:
            return super().destroy(request, *args, **kwargs)
        else:
            response = {
                'status': 'OperationFailed'
            }
            return Response(response)

