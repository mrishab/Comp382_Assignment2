from enum import Enum


class Status(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ACCEPTED = "accepted"
    REJECTED = "rejected"