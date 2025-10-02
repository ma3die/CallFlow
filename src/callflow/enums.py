from enum import Enum

class CallStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    READY = "ready"