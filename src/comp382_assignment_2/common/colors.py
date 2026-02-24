from enum import Enum


class Color(str, Enum):
    # Primary dark background for vis-network canvases.
    GRAPH_BACKGROUND_DARK = "#1a1a2a"

    # Default node fill and border for non-active states.
    NODE_DEFAULT_BG = "#4A90D9"
    NODE_DEFAULT_BORDER = "#2C5F8A"

    # Highlight for currently active/running node.
    NODE_ACTIVE_BG = "#FFD700"
    NODE_ACTIVE_BORDER = "#B8860B"

    # Accepted/final-state emphasis.
    NODE_ACCEPTED_BG = "#5CB85C"
    NODE_ACCEPTED_BORDER = "#3A7A3A"

    # Initial-state emphasis.
    NODE_INITIAL_BG = "#9B59B6"
    NODE_INITIAL_BORDER = "#6C3483"

    # Rejected/stuck-state emphasis.
    NODE_REJECTED_BG = "#E74C3C"
    NODE_REJECTED_BORDER = "#922B21"

    # Primary light text on dark graph nodes.
    TEXT_WHITE = "#ffffff"

    # Button theme colors (right-panel controls).
    BUTTON_BG = "#495057"
    BUTTON_BORDER = "#6c757d"
    BUTTON_HOVER_BG = "#6c757d"
    BUTTON_PRESSED_BG = "#343a40"

    # Status badge neutral tones and muted helper labels.
    STATUS_IDLE_TEXT = "#888"
    STATUS_IDLE_BORDER = "#444"
    LABEL_MUTED = "#cfcfcf"
