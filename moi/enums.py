from enum import Enum, EnumMeta


class ChoiceEnumMeta(EnumMeta):

    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, Enum):
            return value.value
        return value

    def __iter__(self):
        return ((tag.name, tag.value) for tag in super().__iter__())


class NotificationType(Enum, metaclass=ChoiceEnumMeta):
    notifyMOIAttributeValueChanges = 'notifyMOIAttributeValueChanges'
    notifyMOICreation = 'notifyMOICreation'
    notifyMOIDeletion = 'notifyMOIDeletion'


class OperationStatus(Enum, metaclass=ChoiceEnumMeta):
    OperationSucceeded = 'OperationSucceeded'
    OperationFailedExistingSubscription = 'OperationFailedExistingSubscription'
    OperationFailed = 'OperationFailed'


class MOIType(Enum, metaclass=ChoiceEnumMeta):
    SST = 'SST'
    SNSSAIList = 'SNSSAIList'
    PLMNIdList = 'PLMNIdList'
    PerfRequirements = 'PerfRequirements'
    SliceProfileList = 'SliceProfileList'
    NsInfo = 'NsInfo'
    NetworkSliceSubnet = 'NetworkSliceSubnet'


class Modification(Enum):
    REPLACE = 'REPLACE'
    ADD_VALUES = 'ADD_VALUES'
    REMOVE_VALUES = 'REMOVE_VALUES'
    SET_TO_DEFAULT = 'SET_TO_DEFAULT'

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class Scope(Enum):
    BASE_ONLY = 'BASE_ONLY'
    BASE_NTH_LEVEL = 'BASE_NTH_LEVEL'
    BASE_SUBTREE = 'BASE_SUBTREE'
    BASE_ALL = 'BASE_ALL'

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)