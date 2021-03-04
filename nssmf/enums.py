from enum import Enum, EnumMeta


class ChoiceEnumMeta(EnumMeta):

    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, Enum):
            return value.value
        return value

    def __iter__(self):
        return ((tag.name, tag.value) for tag in super().__iter__())


class TemplateType(Enum, metaclass=ChoiceEnumMeta):
    VNF = 'Virtual Network Function Package'
    NSD = 'Network Service Descriptor'
    NRM = 'Network Resource Model'
    # VNF = 0
    # NSD = 1
    # NRM = 2


class NfvoType(Enum, metaclass=ChoiceEnumMeta):
    XOS_NFVO = 'XOS_NFVO'
    TACKER_NFVO = 'TACKER_NFVO'


class OperationStatus(Enum, metaclass=ChoiceEnumMeta):
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    UPLOAD = 'UPLOAD'
    OPERATION_SUCCEEDED = 'OperationSucceeded'
    OPERATION_FAILED = 'OperationFailed'


class LifeCycleStatus(Enum, metaclass=ChoiceEnumMeta):
    CREATION = 'CREATION'
    ACTIVATION = 'ACTIVATION'
    MODIFICATION = 'MODIFICATION'
    DEACTIVATION = 'DEACTIVATION'
    TERMINATION = 'TERMINATION'


class PluginOperationStatus(Enum, metaclass=ChoiceEnumMeta):
    REGISTER = 'Register Success'
    UPDATE = 'Update Success'
    DELETE = 'Delete Success'
    ERROR = 'No such Plug-in config.yaml'

