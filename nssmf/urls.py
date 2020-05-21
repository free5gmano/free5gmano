from django.urls import include, path
from .views import ProvisioningView, SliceTemplateView, GenericTemplateView,\
    ServiceMappingPluginView
from .routers import CustomReadOnlyRouter

router = CustomReadOnlyRouter()

router.register(r'plugin/management', ServiceMappingPluginView,
                basename='ServiceMappingPlugin')
router.register(r'ObjectManagement/GenericTemplate', GenericTemplateView,
                basename='GenericTemplate')
router.register(r'ObjectManagement/SliceTemplate', SliceTemplateView,
                basename='SliceTemplate')
router.register(r'ObjectManagement/NSS/SliceProfiles', ProvisioningView,
                basename='Provisioning')


urlpatterns = [
    path('', include(router.urls))
]
