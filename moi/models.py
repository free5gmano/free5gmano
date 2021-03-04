import uuid

from django.db import models
from django.db.models import CharField
from django_mysql.models import ListTextField
from moi.enums import NotificationType, MOIType

# Create your models here.


class SST(models.Model):
    value = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=16)
    characteristics = models.TextField()


class SNSSAIList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    sST = models.ManyToManyField(SST, related_name='sST')
    sD = models.CharField(max_length=6)


class PLMNIdList(models.Model):
    pLMNId = models.CharField(primary_key=True, max_length=5)
    mcc = models.CharField(max_length=3)
    mnc = models.CharField(max_length=2)
    MobileNetworkOperator = models.TextField()


class PerfRequirements(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    scenario = models.TextField()
    experiencedDataRateDL = models.TextField()
    experiencedDataRateUL = models.TextField()
    areaTrafficCapacityDL = models.TextField()
    areaTrafficCapacityUL = models.TextField()
    overallUserDensity = models.TextField()
    activityFactor = models.TextField()
    ueSpeed = models.TextField()
    coverage = models.TextField()


class SliceProfileList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    sNSSAIListId = models.ManyToManyField(SNSSAIList, related_name='sNSSAIList')
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdList_sliceProfileList')
    perfReqId = models.ManyToManyField(PerfRequirements, related_name='perfReq')


class NsInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nsInstanceName = models.TextField(null=True, blank=True)
    nsInstanceDescription = models.TextField(null=True, blank=True)
    nsdId = models.UUIDField(null=True, blank=True)
    nsdInfoId = models.UUIDField(null=True, blank=True)
    flavourId = models.UUIDField(null=True, blank=True)
    vnfInstance = models.TextField(null=True, blank=True)
    vnffgInfo = models.TextField(null=True, blank=True)
    nestedNsInstanceId = models.TextField(null=True, blank=True)
    nsState = models.TextField(null=True, blank=True)
    monitoringParameter = models.TextField(null=True, blank=True)
    _links = models.TextField(null=True, blank=True)


class NetworkSliceSubnet(models.Model):
    nssiId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    mFIdList = ListTextField(base_field=CharField(max_length=30))
    constituentNSSIIdList = models.ManyToManyField('self', blank=True,
                                                   related_name='constituentNSSIIdList')
    administrativeState = models.TextField(default='LOCKED')
    operationalState = models.TextField(default='ENABLED')
    nsInfo = models.ForeignKey(NsInfo, null=True, on_delete=models.CASCADE, related_name='nsInfo')
    sliceProfileList = models.ManyToManyField(SliceProfileList, related_name='sliceProfileList')


class AMFSet(models.Model):
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_AMFSet')
    nRTACList = models.IntegerField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_AMFSet')


class AMFRegion(models.Model):
    aMFSetId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    nRTACList = models.IntegerField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_AMFRegion')


class AMFRegionRelated(models.Model):
    aMFRegionId = models.OneToOneField(AMFRegion, primary_key=True, on_delete=models.CASCADE,
                                       related_name='aMFRegionId')
    aMFSet = models.ManyToManyField(AMFSet, related_name='aMFSet')


class AMFSetRelated(models.Model):
    aMFSetId = models.OneToOneField(AMFSet, primary_key=True, on_delete=models.CASCADE,
                                    related_name='aMFSetId')
    aMFRegion = models.ManyToManyField(AMFRegion, related_name='aMFRegion')
    aMFSetMemberList = models.ManyToManyField(AMFSet, related_name='aMFSetMemberList')


class AMFFunction(models.Model):
    aMFIdentifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_AMFFunction')
    sBIFQDN = models.TextField()
    sBIServiceList = models.TextField()
    weightFactor = models.IntegerField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_AMFFunction')


class SMFFunction(models.Model):
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_SMFFunction')
    nRTACList = models.IntegerField()
    sBIFQDN = models.TextField()
    sBIServiceList = models.TextField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_SMFFunction')


class UPFFunction(models.Model):
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_UPFFunction')
    nRTACList = models.IntegerField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_UPFFunction')


class PCFunction(models.Model):
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_PCFFunction')
    sBIFQDN = models.TextField()
    sBIServiceList = models.TextField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_PCFFunction')


class OtherFunction(models.Model):
    pLMNIdList = models.ManyToManyField(PLMNIdList, related_name='pLMNIdListId_OtherFunction')
    sBIFQDN = models.TextField()
    sBIServiceList = models.TextField()
    sNSSAIList = models.ManyToManyField(SNSSAIList, related_name='sNSSAIListId_OtherFunction')


class CommonNotification(models.Model):
    notificationId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    notificationType = models.CharField(max_length=255, choices=NotificationType)
    eventTime = models.DateTimeField(auto_now=True)
    systemDN = models.CharField(max_length=255, null=True, blank=True)
    objectClass = models.CharField(max_length=255, choices=MOIType)
    objectInstanceInfos = models.TextField()
    additionalText = models.TextField()


class Subscription(models.Model):
    subscriptionId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    timeTick = models.IntegerField()
    filter = models.ManyToManyField(CommonNotification,
                                    related_name='Subscription_CommonNotification')
    callbackUri = models.TextField()