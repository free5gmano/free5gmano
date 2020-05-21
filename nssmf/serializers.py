from rest_framework import serializers
from nssmf.models import SliceTemplate, GenericTemplate, ServiceMappingPluginModel, Content
from nssmf.enums import OperationStatus, PluginOperationStatus
from free5gmano import settings
import zipfile
import yaml
import os


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['contentId', 'type', 'tosca_definitions_version', 'topology_template']


class GenericTemplateSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=True, read_only=True, source='content_set')

    class Meta:
        model = GenericTemplate
        fields = ['templateId', 'nfvoType', 'templateType', 'templateFile', 'content',
                  'operationStatus', 'operationTime']
        read_only_fields = ['templateFile']

    def create(self, validated_data):
        print(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['operationStatus'] = OperationStatus.UPDATED
        print(validated_data)
        return super().update(instance, validated_data)


class GenericTemplateFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GenericTemplate
        fields = ['templateId', 'templateFile', 'templateType', 'operationStatus', 'operationTime']

    def update(self, instance, validated_data):
        # if not self.instance.templateType:
        #     raise serializers.ValidationError('This templateType field must be value.')
        validated_data['operationStatus'] = OperationStatus.UPLOAD
        return super().update(instance, validated_data)


class GenericTemplateRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = GenericTemplate
        fields = ['templateId', 'templateType', 'nfvoType']


class SliceTemplateRelationSerializer(serializers.ModelSerializer):
    genericTemplates = GenericTemplateRelationSerializer(many=True, read_only=True)

    class Meta:
        model = SliceTemplate
        fields = '__all__'

    @property
    def data(self):
        serialized_data = super().data
        custom_representation = dict()
        for _ in serialized_data['genericTemplates']:
            if _['templateType'] not in custom_representation:
                custom_representation[_['templateType']] = list()
            custom_representation[_['templateType']].append(_['templateId'])
        serialized_data['genericTemplates'] = custom_representation
        return serialized_data


class SliceTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SliceTemplate
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)


class ServiceMappingPluginSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        if 'context' in kwargs.keys():
            view = kwargs['context']['view']
            if view.action in ('retrieve', 'list'):
                self.Meta.fields = ['name', 'allocate_nssi', 'deallocate_nssi']
            elif view.action == 'create':
                self.Meta.fields = ['name', 'pluginFile']
            elif view.action == 'update':
                self.Meta.fields = ['pluginFile']
            else:
                self.Meta.fields = '__all__'
        super().__init__(*args, **kwargs)

    class Meta:
        model = ServiceMappingPluginModel
        fields = '__all__'

    def create(self, validated_data):
        response_data = dict()
        zipfile_check = ['deallocate/main.py', 'deallocate/', 'config.yaml',
                         'allocate/main.py', 'allocate/']
        # Extract Zip file
        with zipfile.ZipFile(validated_data['pluginFile']) as _zipfile:
            for file in _zipfile.filelist:
                if file.filename in zipfile_check:
                    zipfile_check.remove(file.filename)
            if not zipfile_check:
                _zipfile.extractall(path=os.path.join(
                                    settings.PLUGIN_ROOT, validated_data['name']))
        # Assign Plugin config
        if not zipfile_check:
            with open(os.path.join(settings.PLUGIN_ROOT, validated_data['name'],
                                   'config.yaml')) as stream:
                config = yaml.safe_load(stream)
                validated_data = {
                    'name': validated_data['name'],
                    'allocate_nssi': config['allocate_file'],
                    'deallocate_nssi': config['deallocate_file'],
                    'pluginFile': validated_data['pluginFile'],
                    'nm_host': config['nm_host'],
                    'nfvo_host': config['nfvo_host'],
                    'subscription_host': config['subscription_host']
                }
                self.Meta.fields = '__all__'
            return super().create(validated_data)
        response_data['status'] = PluginOperationStatus.ERROR
        raise Exception(response_data)

    def update(self, instance, validated_data):
        response_data = dict()
        zipfile_check = ['requirements.txt', 'deallocate/main.py', 'deallocate/', 'config.yaml',
                         'allocate/main.py', 'allocate/', '.gitignore']
        # Extract Zip file
        with zipfile.ZipFile(validated_data['pluginFile']) as _zipfile:
            for file in _zipfile.filelist:
                if file.filename in zipfile_check:
                    zipfile_check.remove(file.filename)
            if not zipfile_check:
                _zipfile.extractall(path=os.path.join(
                    settings.PLUGIN_ROOT, instance.name))
        # Assign Plugin config
        if not zipfile_check:
            with open(os.path.join(settings.PLUGIN_ROOT, instance.name,
                                   'config.yaml')) as stream:
                config = yaml.safe_load(stream)
                validated_data = {
                    'allocate_nssi': config['allocate_file'],
                    'deallocate_nssi': config['deallocate_file'],
                    'pluginFile': validated_data['pluginFile'],
                    'nm_host': config['nm_host'],
                    'nfvo_host': config['nfvo_host'],
                    'subscription_host': config['subscription_host']
                }
                self.Meta.fields = '__all__'
                instance.pluginFile.delete()
                return super().update(instance, validated_data)
        response_data['status'] = PluginOperationStatus.ERROR
        raise Exception(response_data)


class ServiceMappingPluginRelationSerializer(serializers.ModelSerializer):
    genericTemplates = GenericTemplateRelationSerializer(many=True, read_only=True)
    nfvoType = ServiceMappingPluginSerializer(many=True, read_only=True)

    class Meta:
        model = SliceTemplate
        fields = '__all__'

    @property
    def data(self):
        serialized_data = super().data
        custom_representation = dict()
        for _ in serialized_data['genericTemplates']:
            if _['templateType'] not in custom_representation:
                custom_representation[_['templateType']] = list()
            custom_representation[_['templateType']].append(_['templateId'])
        serialized_data['genericTemplates'] = custom_representation
        return serialized_data
