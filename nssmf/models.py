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
