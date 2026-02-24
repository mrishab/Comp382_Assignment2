from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.flow_diagram_status import FlowDiagramStatus


class NodeStyleMap:
    _FLOW_MAP = {
        FlowDiagramStatus.IDLE: {"background": Color.FLOW_IDLE_BG.value, "border": Color.FLOW_IDLE_BORDER.value},
        FlowDiagramStatus.GATE: {"background": Color.FLOW_GATE_BG.value, "border": Color.FLOW_GATE_BORDER.value},
        FlowDiagramStatus.INPUT: {"background": Color.NODE_DEFAULT_BG.value, "border": Color.NODE_DEFAULT_BORDER.value},
        FlowDiagramStatus.RESULT: {"background": Color.FLOW_RESULT_BG.value, "border": Color.FLOW_RESULT_BORDER.value},
        FlowDiagramStatus.LANG: {"background": Color.FLOW_LANG_BG.value, "border": Color.NODE_DEFAULT_BG.value},
        FlowDiagramStatus.START: {"background": Color.FLOW_START_BG.value, "border": Color.FLOW_START_BORDER.value},
    }

    @classmethod
    def flow(cls, key: FlowDiagramStatus) -> dict:
        return cls._FLOW_MAP[key]
