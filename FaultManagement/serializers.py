from rest_framework import serializers
from FaultManagement.models import *


class AttributeNameValuePairSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeNameValuePair
        fields = '__all__'


class HeaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionResource
        fields = '__all__'


class CommentResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentResource
        fields = '__all__'


class SubscriptionResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionResource
        fields = '__all__'


class ThresholdInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ThresholdInfo
        fields = '__all__'


class AttributeValueChangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeValueChange
        fields = '__all__'


class CorrelatedNotificationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorrelatedNotifications
        fields = '__all__'


class AlarmResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlarmResource
        fields = '__all__'


class AlarmsCountSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlarmsCount
        fields = '__all__'


