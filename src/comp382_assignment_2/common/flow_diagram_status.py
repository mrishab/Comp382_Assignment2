from enum import Enum


class FlowDiagramStatus(str, Enum):
    IDLE = "idle"
    GATE = "gate"
    INPUT = "input"
    RESULT = "result"
    LANG = "lang"
    START = "start"
