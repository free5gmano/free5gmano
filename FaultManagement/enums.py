from enum import Enum, EnumMeta


class ChoiceEnumMeta(EnumMeta):

    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, Enum):
            return value.value
        return value

    def __iter__(self):
        return ((tag.name, tag.value) for tag in super().__iter__())


class AlarmAckState(Enum, metaclass=ChoiceEnumMeta):
    allAlarms = 'allAlarms'
    allActiveAlarms = 'allActiveAlarms'
    allActiveAndAcknowledgedAlarms = 'allActiveAndAcknowledgedAlarms'
    allActiveAndUnacknowledgedAlarms = 'allActiveAndUnacknowledgedAlarms'
    allClearedAndUnacknowledgedAlarms = 'allClearedAndUnacknowledgedAlarms'
    allUnacknowledgedAlarms = 'allUnacknowledgedAlarms'


class PerceivedSeverity(Enum, metaclass=ChoiceEnumMeta):
    Critical = 'Critical'
    Major = 'Major'
    Minor = 'Minor'
    Warning = 'Warning'
    Indeterminate = 'Indeterminate'
    Cleared = 'Cleared'


class Notification(Enum, metaclass=ChoiceEnumMeta):
    notifyNewAlarm = 'notifyNewAlarm'
    notifyAckStateChanged = 'notifyAckStateChanged'
    notifyClearedAlarm = 'notifyClearedAlarm'
    notifyAlarmListRebuiltAlarm = 'notifyAlarmListRebuiltAlarm'
    notifyChangedAlarm = 'notifyChangedAlarm'
    notifyComments = 'notifyComments'
    notifyPotentialFaultyAlarmList = 'notifyPotentialFaultyAlarmList'
    notifyCorrelatedNotificationChanged = 'notifyCorrelatedNotificationChanged'
    notifyChangedAlarmGeneral = 'notifyChangedAlarmGeneral'


class AlarmType(Enum, metaclass=ChoiceEnumMeta):
    CommunicationsAlarm = 'CommunicationsAlarm'
    ProcessingErrorAlarm = 'ProcessingErrorAlarm'
    EnvironmentalAlarm = 'EnvironmentalAlarm'
    QualityOfServiceAlarm = 'QualityOfServiceAlarm'
    EquipmentAlarm = 'EquipmentAlarm'
    IntegrityViolation = 'IntegrityViolation'
    OperationalViolation = 'OperationalViolation'
    PhysicalViolation = 'PhysicalViolation'
    SecurityService = 'SecurityService'
    MechanismViolation = 'MechanismViolation'
    TimeDomainViolation = 'TimeDomainViolation'


class TrendIndication(Enum, metaclass=ChoiceEnumMeta):
    MoreSevere = 'MoreSevere'
    NoChange = 'NoChange'
    LessSevere = 'LessSevere'


class Indication(Enum, metaclass=ChoiceEnumMeta):
    Up = 'Up'
    Down = 'Down'


class AlarmListAlignmentRequirement(Enum, metaclass=ChoiceEnumMeta):
    AlignmentRequired = 'AlignmentRequired'
    AlignmentNotRequired = 'AlignmentNotRequired'










