from rest_framework.routers import SimpleRouter
# from fault_supervision.routers import CustomReadOnlyRouter
from django.urls import path, include


from FaultManagement.views import FaultSupervisionView, FaultSupervisionSubscriptionsView

router = SimpleRouter()


router.register(r'alarms', FaultSupervisionView,
                basename='FaultSupervision')
router.register(r'subscriptions', FaultSupervisionSubscriptionsView,
                basename='FaultSupervisionSubscriptions')

urlpatterns = [
    path('', include(router.urls)),
]
