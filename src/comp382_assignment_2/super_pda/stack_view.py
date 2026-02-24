from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.super_pda_view_status import SuperPDAViewStatus
from comp382_assignment_2.gui.node_style_map import NodeStyleMap


class StackView:
    def __init__(self):
        self._items: list[str] = []
        self._nodes: list[dict] = []
        self._edges: list[dict] = []

    def reset(self, items: list[str] | None = None) -> None:
        self._items = list(items or [])
        self.rebuild_graph()

    def push(self, value: str) -> None:
        self._items.append(value)
        self.rebuild_graph()

    def pop(self) -> str | None:
        if self.is_empty():
            return None
        value = self._items.pop()
        self.rebuild_graph()
        return value

    def peek(self) -> str | None:
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def to_list(self) -> list[str]:
        return list(self._items)

    def nodes(self) -> list[dict]:
        return list(self._nodes)

    def edges(self) -> list[dict]:
        return list(self._edges)

    def rebuild_graph(self, start_x: int = 0, start_y: int = -450, gap: int = 110) -> None:
        style = NodeStyleMap.super_pda(SuperPDAViewStatus.STACK)

        self._nodes = [
            {
                "id": "__stack_empty__",
                "label": "Stack\n∅",
                "color": style,
                "shape": "box",
                "size": 30,
                "font": {"size": 13, "color": Color.SUPER_STACK_TEXT.value},
                "x": start_x,
                "y": start_y,
                "fixed": {"x": True, "y": True},
            }
        ]
        self._edges = []

        for index, value in enumerate(self._items):
            node_id = f"__stack_{index}__"
            self._nodes.append(
                {
                    "id": node_id,
                    "label": value,
                    "color": style,
                    "shape": "box",
                    "size": 30,
                    "font": {"size": 13, "color": Color.SUPER_STACK_TEXT.value},
                    "x": start_x + ((index + 1) * gap),
                    "y": start_y,
                    "fixed": {"x": True, "y": True},
                }
            )

            self._edges.append(
                {
                    "from": "__stack_empty__" if index == 0 else f"__stack_{index - 1}__",
                    "to": node_id,
                    "label": "",
                }
            )

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __getitem__(self, index: int) -> str:
        return self._items[index]
