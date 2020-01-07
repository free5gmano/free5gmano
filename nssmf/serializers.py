from rest_framework import serializers
from nssmf.models import SliceTemplate, GenericTemplate, ServiceMappingPluginModel


class SliceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliceTemplate
        fields = '__all__'


class GenericTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericTemplate
        fields = '__all__'


class ServiceMappingPluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMappingPluginModel
        fields = '__all__'
