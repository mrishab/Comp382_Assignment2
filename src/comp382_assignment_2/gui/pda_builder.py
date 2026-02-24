from __future__ import annotations

import networkx as nx
from pyvis.network import Network

from comp382_assignment_2.common.colors import Color

# ── default visual tokens ─────────────────────────────────────────────────────
_EPS = "\u03b5"   # ε
_ARR = "\u2192"   # →

NODE_COLOURS = {
    "default": {"background": Color.NODE_DEFAULT_BG.value, "border": Color.NODE_DEFAULT_BORDER.value},
    "active":  {"background": Color.NODE_ACTIVE_BG.value, "border": Color.NODE_ACTIVE_BORDER.value},
    "accept":  {"background": Color.NODE_ACCEPTED_BG.value, "border": Color.NODE_ACCEPTED_BORDER.value},
    "initial": {"background": Color.NODE_INITIAL_BG.value, "border": Color.NODE_INITIAL_BORDER.value},
    "stuck":   {"background": Color.NODE_REJECTED_BG.value, "border": Color.NODE_REJECTED_BORDER.value},
}

_NODE_SIZE   = 30
_NODE_FONT   = {"size": 15, "color": Color.TEXT_WHITE.value}
_EDGE_COLOUR = {"color": "#667799"}
_EDGE_FONT   = {"size": 10, "color": "#dddddd", "strokeWidth": 0}


class PDABuilder:
    """
    Builds the full NetworkX / Pyvis graph representation of a PDA from a
    raw config dict (as stored in pda.json).
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self, config: dict):
        self._cfg = config
        self._edge_label_map: dict[tuple[str, str], list[str]] = {}  # lazily built
        self._build_edge_label_map()

    # ── public properties ─────────────────────────────────────────────────────

    @property
    def states(self) -> list[str]:
        return list(self._cfg["states"])

    @property
    def alphabet(self) -> list[str]:
        return list(self._cfg["alphabet"])

    @property
    def stack_alphabet(self) -> list[str]:
        return list(self._cfg["stack_alphabet"])

    @property
    def initial_state(self) -> str:
        return self._cfg["initial_state"]

    @property
    def final_states(self) -> set[str]:
        return set(self._cfg["final_states"])

    @property
    def transitions(self) -> list[dict]:
        return self._cfg["transitions"]

    @property
    def description(self) -> str:
        return self._cfg.get("description", "")

    @property
    def language(self) -> str:
        return self._cfg.get("language", "")

    @property
    def example_strings(self) -> list[str]:
        return self._cfg.get("example_strings", [])

    # ── node / edge colour ────────────────────────────────────────────────────

    def node_color(self, state: str, model=None) -> dict:
        if model is not None:
            if state == model.current_state:
                if model.is_stuck():
                    return NODE_COLOURS["stuck"]
                if model.is_accepted():
                    return NODE_COLOURS["accept"]
                return NODE_COLOURS["active"]
            if state in model.final_states:
                return NODE_COLOURS["accept"]
            if state == model.initial_state:
                return NODE_COLOURS["initial"]
            return NODE_COLOURS["default"]

        # Static (no live model)
        if state in self.final_states:
            return NODE_COLOURS["accept"]
        if state == self.initial_state:
            return NODE_COLOURS["initial"]
        return NODE_COLOURS["default"]

    # ── graph construction ────────────────────────────────────────────────────

    def build_nodes(self, model=None) -> list[dict]:
        """
        Return a list of node attribute dicts ready to pass to pyvis.

        Each dict has: id, label, color, shape, size, font.
        """
        nodes = []
        for state in self.states:
            nodes.append({
                "id":    state,
                "label": state,
                "color": self.node_color(state, model),
                "shape": "doublecircle" if state in self.final_states else "circle",
                "size":  _NODE_SIZE,
                "font":  _NODE_FONT,
            })
        return nodes

    def build_edges(self) -> list[dict]:
        """
        Return a list of edge attribute dicts ready to pass to pyvis.

        Each dict has: source, to, label.
        Multiple transitions between the same pair of states are merged into
        one edge with ' | '-separated labels.
        """
        edges = []
        for (src, dst), labels in self._edge_label_map.items():
            edges.append({
                "source": src,
                "to":     dst,
                "label":  " | ".join(labels),
            })
        return edges

    def build_nx_graph(self) -> nx.MultiDiGraph:
        """Build and return a NetworkX MultiDiGraph for the PDA."""
        G = nx.MultiDiGraph()
        for state in self.states:
            G.add_node(state)
        for (src, dst), labels in self._edge_label_map.items():
            G.add_edge(src, dst, label=" | ".join(labels))
        return G

    def build_pyvis_network(
        self,
        height: str = "100%",
        width: str = "100%",
        bgcolor: str = Color.GRAPH_BACKGROUND_DARK.value,
        options: str | None = None,
        model=None,
    ) -> Network:
        """
        Build and return a fully configured pyvis Network.

        Parameters
        ----------
        height, width : vis.js canvas size strings
        bgcolor       : canvas background colour
        options       : raw vis.js options JSON string (passed to net.set_options)
        model         : optional live PushdownAutomataModel for live-state colours
        """
        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=False,
            bgcolor=bgcolor,
        )
        if options:
            net.set_options(options)

        for node in self.build_nodes(model=model):
            net.add_node(
                node["id"],
                label=node["label"],
                color=node["color"],
                shape=node["shape"],
                size=node["size"],
            )

        for edge in self.build_edges():
            net.add_edge(edge["source"], edge["to"], label=edge["label"])

        return net

    # ── private ───────────────────────────────────────────────────────────────

    def _build_edge_label_map(self) -> None:
        """Pre-compute merged transition labels keyed by (src, dst)."""
        label_map: dict[tuple[str, str], list[str]] = {}
        for t in self.transitions:
            src      = t["from"]
            dst      = t["to"]
            ch       = t.get("input") or _EPS
            top      = t.get("stack_top") or _EPS
            push     = t.get("push", [])
            push_str = "|".join(push) if push else _EPS
            label    = f"{ch},{top} {_ARR} {push_str}"
            label_map.setdefault((src, dst), []).append(label)
        self._edge_label_map = label_map

    def __repr__(self) -> str:
        return (
            f"PDABuilder(states={self.states}, "
            f"initial={self.initial_state!r}, "
            f"final={self.final_states}, "
            f"transitions={len(self.transitions)})"
        )

    # ── alternative constructors ──────────────────────────────────────────────

    @classmethod
    def from_model(cls, model) -> "PDABuilder":
        """
        Create a PDABuilder from a live PushdownAutomataModel.

        The model stores transitions as:
            { (src, input|None, stack_top): [(dst, push_list)] }
        This method converts that back into the JSON transition-list format
        so PDABuilder can be used for rendering without needing the original
        config dict.
        """
        transition_list = []
        for (src, ch, top), entries in model.transitions.items():
            for dst, push in entries:
                transition_list.append({
                    "from":      src,
                    "input":     ch,
                    "stack_top": top,
                    "to":        dst,
                    "push":      list(push),
                })
        config = {
            "states":               list(model.states),
            "alphabet":             list(getattr(model, "alphabet", [])),
            "stack_alphabet":       list(getattr(model, "stack_alphabet", [])),
            "initial_state":        model.initial_state,
            "initial_stack_symbol": getattr(model, "initial_stack_symbol", "Z"),
            "final_states":         list(model.final_states),
            "transitions":          transition_list,
        }
        return cls(config)
