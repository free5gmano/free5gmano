from django.contrib import admin
from .models import ServiceMappingPluginModel, GenericTemplate, SliceTemplate


admin.site.register(ServiceMappingPluginModel)
admin.site.register(GenericTemplate)
admin.site.register(SliceTemplate)