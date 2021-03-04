from django.db import models
import uuid
from .enums import PerceivedSeverity, Notification, AlarmAckState,\
    AlarmType, TrendIndication, Indication


# Create your models here.


class AttributeNameValuePair(models.Model):
    attributeName = models.CharField(max_length=255)
    attributeValue = models.CharField(max_length=255)


class Header(models.Model):
    notificationId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notificationType = models.CharField(max_length=255, choices=Notification, null=True)
    uri = models.CharField(max_length=255)
    eventTime = models.DateTimeField(auto_now=True)
    systemDN = models.CharField(max_length=255, null=True, blank=True)


class CommentResource(models.Model):
    commentTime = models.DateTimeField()
    commentText = models.CharField(max_length=255, null=True, blank=True)
    commentUserId = models.UUIDField()
    commentSystemId = models.UUIDField()


# class AlarmIdAndPerceivedSeverityList(models.Model):
#     alarmId = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)


# class CommentRequest(models.Model):
#     data = models.ForeignKey(CommentResource)


# class PatchAcknowledgeAlarmsRequest(models.Model):
#     ackUserId = models.CharField(max_length=255)
#     ackSystemId = models.CharField(max_length=255)
#     ackState = models.CharField(max_length=255, choices=AckState)
#
#
# class PatchUnacknowledgeAlarmsRequest(models.Model):
#     ackUserId = models.CharField(max_length=255)
#     ackSystemId = models.CharField(max_length=255)
#     ackState = models.CharField(max_length=255, choices=AckState)
#
#
# class PatchClearAlarmsRequest(models.Model):
#     clearUserId = models.CharField(max_length=255)
#     clearSystemId = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)


class SubscriptionResource(models.Model):
    notificationId = models.OneToOneField(Header, on_delete=models.CASCADE, primary_key=True)
    consumerReference = models.CharField(max_length=255, null=True, blank=True)
    timeTick = models.IntegerField()
    filter = models.TextField()


# class SubscriptionRequest(models.Model):
#     data = models.ForeignKey(SubscriptionResource)


class ThresholdInfo(models.Model):
    attributeName = models.CharField(max_length=255)
    observedValue = models.CharField(max_length=255)
    thresholdLevel = models.CharField(max_length=255, choices=Indication)
    armTime = models.DateTimeField()


class AttributeValueChange(models.Model):
    attributeName = models.CharField(max_length=255)
    oldAttributeValue = models.CharField(max_length=255)
    newAttributeValue = models.CharField(max_length=255)


class CorrelatedNotifications(models.Model):
    source = models.CharField(max_length=255)
    notificationIds = models.UUIDField()


class AlarmResource(models.Model):
    header = models.ForeignKey(Header, on_delete=models.CASCADE, related_name='header', null=True)
    alarmType = models.CharField(max_length=255, choices=AlarmType, null=True)
    alarmId = models.CharField(primary_key=True, max_length=255)
    alarmRaisedTime = models.CharField(max_length=255, null=True, blank=True)
    alarmChangedTime = models.CharField(max_length=255, null=True, blank=True)
    alarmClearedTime = models.CharField(max_length=255, null=True, blank=True)
    probableCause = models.CharField(max_length=255, null=True, blank=True)
    perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity, blank=True)
    rootCauseIndicator = models.CharField(max_length=255, null=True, blank=True)
    specificProblem = models.TextField(null=True, blank=True)
    backedUpStatus = models.CharField(max_length=255, null=True, blank=True)
    trendIndication = models.CharField(max_length=255, choices=TrendIndication,
                                       null=True, blank=True)
    thresholdinfo = models.ForeignKey(ThresholdInfo, on_delete=models.CASCADE,
                                      related_name='thresholdinfo', null=True)
    stateChangeDefinition = models.ForeignKey(AttributeValueChange, on_delete=models.CASCADE,
                                              related_name='stateChangeDefinition', null=True)
    monitoredAttributes = models.ForeignKey(AttributeNameValuePair, on_delete=models.CASCADE,
                                            related_name='monitoredAttributes', null=True)
    proposedRepairActions = models.CharField(max_length=255, null=True, blank=True)
    additionalText = models.TextField(null=True, blank=True)
    additionalInformation = models.ForeignKey(AttributeNameValuePair, on_delete=models.CASCADE,
                                              related_name='additionalInformation', null=True)
    ackTime = models.CharField(max_length=255, null=True, blank=True)
    ackUserId = models.UUIDField(null=True, blank=True)
    ackSystemId = models.UUIDField(null=True, blank=True)
    ackstate = models.CharField(max_length=255, choices=AlarmAckState, null=True)
    clearUserId = models.UUIDField(null=True, blank=True)
    clearSystemId = models.UUIDField(null=True, blank=True)
    backUpObject = models.CharField(max_length=255, null=True, blank=True)
    correlatedNotifications = models.ForeignKey(CorrelatedNotifications, on_delete=models.CASCADE,
                                                related_name='correlatedNotifications', null=True)
    comments = models.ForeignKey(CommentResource, on_delete=models.CASCADE,
                                 related_name='comments', null=True)
    serviceUser = models.CharField(max_length=255, null=True, blank=True)
    serviceProvider = models.CharField(max_length=255, null=True, blank=True)
    securityAlarmDetector = models.CharField(max_length=255, null=True, blank=True)


# class AlarmsResponse(models.Model):
#     data = models.ForeignKey(AlarmResource)


class AlarmsCount(models.Model):
    criticalCount = models.IntegerField()
    majorCount = models.IntegerField()
    minorCount = models.IntegerField()
    warningCount = models.IntegerField()
    indeterminateCount = models.IntegerField()
    clearedCount = models.IntegerField()


# class AlarmsCountResponse(models.Model):
#     data = models.ForeignKey(AlarmsCount)


# class CommentResponse(models.Model):
#     data = models.ForeignKey(CommentResource)


# class ErrorResponse(models.Model):
#     errorInfo = models.CharField(max_length=255)


# class FailedAlarmsResponse(models.Model):
#     # error [{
#     # alarmId alarmId-Typestring
#     # errorReason string
#     #
#     # }]
#
# class SubscriptionResponse(models.Model):
#     data = models.ForeignKey(SubscriptionResource)


# class NotifyNewAlarm(models.Model):
#     header = models.ForeignKey(Header)
#     alarmId = models.CharField(max_length=255)
#     alarmType = models.ForeignKey(AlarmType)
#     probableCause = models.CharField(max_length=255)
#     specificProblem = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)
#     backedUpStatus = models.CharField(max_length=255)
#     backUpObject = models.CharField(max_length=255)
#     trendIndication = models.CharField(max_length=255, choices=TrendIndication)
#     thresholdInfo = models.ForeignKey(ThresholdInfo)
#     correlatedNotifications = models.ForeignKey(CorrelatedNotifications)
#     stateChangeDefinition = models.ForeignKey(AttributeValueChange)
#     monitoredAttributes = models.ForeignKey(AttributeNameValuePair)
#     proposedRepairActions = models.CharField(max_length=255)
#     additionalText = models.CharField(max_length=255)
#     additionalInformation = models.ForeignKey(AttributeNameValuePair)
#     rootCauseIndicator = models.CharField(max_length=255)


# class NotifyNewSecurityAlarm(models.Model):
#     header = models.ForeignKey(Header)
#     alarmId = models.CharField(max_length=255)
#     alarmType = models.ForeignKey(AlarmType)
#     probableCause = models.CharField(max_length=255)
#     specificProblem = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)
#     correlatedNotifications = models.ForeignKey(CorrelatedNotifications)
#     additionalText = models.CharField(max_length=255)
#     additionalInformation = models.ForeignKey(AttributeNameValuePair)
#     rootCauseIndicator = models.CharField(max_length=255)
#     serviceUser = models.CharField(max_length=255)
#     serviceProvider = models.CharField(max_length=255)
#     securityAlarmDetector = models.CharField(max_length=255)
#
# class NotifyAckStateChanged(models.Model):
#     header = models.ForeignKey(Header)
#     alarmId = models.CharField(max_length=255)
#     alarmType = models.ForeignKey(AlarmType)
#     probableCause = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)
#     ackUserId = models.CharField(max_length=255)
#     ackSystemId = models.CharField(max_length=255)
#     ackstate = models.ForeignKey(AckState)
#
# class NotifyClearedAlarm(models.Model):
#     header = models.ForeignKey(Header)
#     alarmId = models.CharField(max_length=255)
#     alarmType = models.ForeignKey(AlarmType)
#     probableCause = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)
#     correlatedNotifications = models.ForeignKey(CorrelatedNotifications)
#     clearUserId = models.CharField(max_length=255)
#     clearSystemId = models.CharField(max_length=255)
#
# class NotifyAlarmListRebuilt(models.Model):
#     header = models.ForeignKey(Header)
#     reason = models.CharField(max_length=255)
#     alarmListAlignmentRequirement = models.ForeignKey(AlarmListAlignmentRequirement)
#
#
# class NotifyChangedAlarm(models.Model):
#     header = models.ForeignKey(Header)
#     alarmId = models.CharField(max_length=255)
#     alarmType = models.ForeignKey(AlarmType)
#     probableCause = models.CharField(max_length=255)
#     perceivedSeverity = models.CharField(max_length=255, choices=PerceivedSeverity)
