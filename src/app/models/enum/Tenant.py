from enum import Enum


# TODO: This should be fetched from some database

class Tenant(Enum):
    PERFECT_ACCOUNTING_AND_SHARED_SERVICES = "perfect-accounting-and-shared-services"
    EXPEDIA = "expedia"
