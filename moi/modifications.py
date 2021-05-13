from enum import Enum


class Modification(Enum):
    REPLACE = 'REPLACE'
    ADD_VALUES = 'ADD_VALUES'
    REMOVE_VALUES = 'REMOVE_VALUES'
    SET_TO_DEFAULT = 'SET_TO_DEFAULT'

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
