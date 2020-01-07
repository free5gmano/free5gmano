from django.db import models
import uuid


class SliceTemplate(models.Model):
    templateId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(null=True, blank=True)
    nfvo = models.TextField(null=True, blank=True)
    reference = models.TextField(null=True, blank=True)


class GenericTemplate(models.Model):
    templateId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.TextField(null=True, blank=True)
    nfvo = models.TextField(null=True, blank=True)
    download_link = models.TextField(null=True, blank=True)
    status = models.TextField(default='create')


class ServiceMappingPluginModel(models.Model):
    name = models.CharField(primary_key=True, max_length=20)
    allocate_nssi = models.TextField(null=False)
    deallocate_nssi = models.TextField(null=False)
