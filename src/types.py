from enum import Enum


class OperationEnum(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
