from django.conf.urls import url
from django.urls import include

from moi.views import ObjectManagement, TopologyView, SubscriptionView, NotificationView
from moi.routers import CustomReadOnlyRouter

moi_view = ObjectManagement.as_view({
            'put': 'create_moi',
            'get': 'get_moi_attributes',
            'patch': 'modify_moi_attributes',
            'delete': 'delete_moi'
            })
router = CustomReadOnlyRouter()
router.register(r'ObjectManagement/subscriptions', SubscriptionView,
                basename='Subscription')
router.register(r'ObjectManagement/provisioningNotifications', NotificationView,
                basename='Notification')
router.register(r'ObjectManagement/NSS/topology', TopologyView,
                basename='Topology')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^ObjectManagement/(?P<className>[\w+]+)/(?P<id>[\w\\*-]+)/$', moi_view),
]
