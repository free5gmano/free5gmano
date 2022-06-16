from django.db import models
import uuid
from nssmf.enums import TemplateType, OperationStatus
from django.core.files.storage import FileSystemStorage
from free5gmano import settings
from moi.models import NetworkSliceSubnet


filesystem = FileSystemStorage(location=settings.PLUGIN_ROOT)


def generate_filename_template(instance, filename):
    url = "%s/%s" % (instance.templateType, filename)
    return url


def generate_filename_plugin(instance, filename):
    url = "%s/%s" % (instance.name, filename)
    return url


class ServiceMappingPluginModel(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=255)
    share = models.BooleanField(default=False)
    name = models.CharField(primary_key=True, max_length=20)
    allocate_nssi = models.CharField(max_length=255)
    deallocate_nssi = models.CharField(max_length=255)
    pluginFile = models.FileField(upload_to=generate_filename_plugin, storage=filesystem)
    nm_host = models.CharField(max_length=255)
    nfvo_host = models.CharField(max_length=255)
    subscription_host = models.CharField(max_length=255)


class GenericTemplate(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=255)
    share = models.BooleanField(default=False)
    templateId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, blank=True)
    templateType = models.CharField(max_length=255,
                                    choices=TemplateType)
    nfvoType = models.CharField(max_length=255)
    templateFile = models.FileField(upload_to=generate_filename_template, blank=True, null=True)
    operationStatus = models.CharField(max_length=255,
                                       choices=OperationStatus,
                                       default=OperationStatus.CREATED)
    description = models.TextField(null=True, blank=True)
    operationTime = models.DateTimeField(auto_now=True)


class Content(models.Model):
    contentId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    templateId = models.ForeignKey(GenericTemplate, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=255, choices=TemplateType)
    tosca_definitions_version = models.CharField(max_length=255)
    topology_template = models.TextField()


class SliceTemplate(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=255)
    share = models.BooleanField(default=False)
    templateId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True, blank=True)
    nfvoType = models.ManyToManyField(ServiceMappingPluginModel)
    genericTemplates = models.ManyToManyField(GenericTemplate, related_name="templates")
    instanceId = models.ManyToManyField(NetworkSliceSubnet, blank=True,
                                        related_name="instsances")