from django.conf.urls import url
from django.urls import include

from moi.views import ObjectManagement
from moi.routers import CustomReadOnlyRouter

moi_view = ObjectManagement.as_view({
            'put': 'create_moi',
            'get': 'get_moi_attributes',
            'patch': 'modify_moi_attributes',
            'delete': 'delete_moi'
            })
router = CustomReadOnlyRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^ObjectManagement/(?P<className>[\w+]+)/(?P<id>[\w\\*-]+)/$', moi_view),
]
