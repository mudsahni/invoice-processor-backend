from enum import Enum


class ValidationType(Enum):
    PRESENCE = 'presence'
    TYPE = 'type'
    LENGTH = 'length'
    RANGE = 'range'
    PATTERN = 'pattern'
    BUSINESS = 'business'
