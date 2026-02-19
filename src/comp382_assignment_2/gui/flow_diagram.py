"""
flow_diagram.py — Custom painted widget that draws the data-flow pipeline:

    Input Field
        |
    ---------
    |       |
   [DFA]  [PDA]     (two funnels)
    |       |
    ---------
        |
    [∩ Gate]
        |
   [Result: Language Label]
        |
        v
   [Super PDA View]

All geometry is computed as proportions of the widget's height/width so
it scales when the window is resized.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QBrush,
    QFont,
    QPainterPath,
    QLinearGradient,
)
from PySide6.QtWidgets import QWidget


# Palette
_BG = QColor("#1e1e2e")
_LINE = QColor("#5a7eaa")
_FUNNEL_DFA = QColor("#4A90D9")
_FUNNEL_PDA = QColor("#9B59B6")
_GATE_BG = QColor("#2d6a4f")
_GATE_BORDER = QColor("#40916c")
_RESULT_BG = QColor("#1a1a2e")
_RESULT_BORDER = QColor("#5a7eaa")
_LABEL = QColor("#cccccc")
_ARROW = QColor("#5a7eaa")
_LANG_LABEL_BG = QColor("#1e2a3e")
_LANG_LABEL_BORDER = QColor("#4A90D9")

# Proportional Y positions (fraction of widget height)
_Y_INPUT_BOT = 0.07
_Y_FORK = 0.14
_Y_FUNNEL_TOP = 0.17
_Y_FUNNEL_BOT = 0.38
_Y_GATE_TOP = 0.44
_Y_GATE_BOT = 0.55
_Y_LANG_TOP = 0.60
_Y_LANG_BOT = 0.70
_Y_RESULT_TOP = 0.74
_Y_RESULT_BOT = 0.83
_Y_ARROW_TIP = 0.92


class FlowDiagram(QWidget):
    """
    Decorative pipeline diagram.  Provides anchor points so the parent
    layout can position real widgets (dropdowns, input field, result label,
    PDA webview) at the correct spots.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Status text shown inside the intersection gate
        self.gate_status = ""
        # Text shown in the result box
        self.result_text = ""
        # DFA / PDA acceptance status: None = idle, True = accept, False = reject
        self.dfa_status: bool | None = None
        self.pda_status: bool | None = None
        # Intersection language label (e.g. "aⁿbⁿ", "∅ (empty)")
        self.language_label: str = ""

    # ── Y helpers (proportional) ─────────────────────────────────────────

    def _y(self, frac: float) -> float:
        return self.height() * frac

    def _cx(self) -> float:
        return self.width() / 2

    def _spread(self) -> float:
        """Half the horizontal distance between the two funnels."""
        return min(self.width() * 0.18, 160)

    # ── public geometry for parent to position real widgets ──────────────

    def result_box_rect(self) -> QRectF:
        cx = self._cx()
        w = min(self.width() * 0.45, 380)
        return QRectF(
            cx - w / 2,
            self._y(_Y_RESULT_TOP),
            w,
            self._y(_Y_RESULT_BOT) - self._y(_Y_RESULT_TOP),
        )

    def arrow_tip_y(self) -> float:
        return self._y(_Y_ARROW_TIP)

    # ── painting ────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self._cx()
        spread = self._spread()
        left_x = cx - spread
        right_x = cx + spread

        pen = QPen(_LINE, 2.0)
        p.setPen(pen)

        y_input_bot = self._y(_Y_INPUT_BOT)
        y_fork = self._y(_Y_FORK)
        y_funnel_top = self._y(_Y_FUNNEL_TOP)
        y_funnel_bot = self._y(_Y_FUNNEL_BOT)
        y_gate_top = self._y(_Y_GATE_TOP)
        y_gate_bot = self._y(_Y_GATE_BOT)
        y_lang_top = self._y(_Y_LANG_TOP)
        y_lang_bot = self._y(_Y_LANG_BOT)
        y_result_top = self._y(_Y_RESULT_TOP)
        y_result_bot = self._y(_Y_RESULT_BOT)
        y_arrow_tip = self._y(_Y_ARROW_TIP)

        # 1. Vertical line from input bottom to fork
        p.drawLine(QPointF(cx, y_input_bot), QPointF(cx, y_fork))

        # 2. Fork — horizontal bar then two verticals down to funnel tops
        p.drawLine(QPointF(left_x, y_fork), QPointF(right_x, y_fork))
        p.drawLine(QPointF(left_x, y_fork), QPointF(left_x, y_funnel_top))
        p.drawLine(QPointF(right_x, y_fork), QPointF(right_x, y_funnel_top))

        # 3. Funnels (trapezoids)
        self._draw_funnel(
            p,
            left_x,
            y_funnel_top,
            y_funnel_bot,
            _FUNNEL_DFA,
            "DFA",
            self.dfa_status,
        )
        self._draw_funnel(
            p,
            right_x,
            y_funnel_top,
            y_funnel_bot,
            _FUNNEL_PDA,
            "PDA",
            self.pda_status,
        )

        # 4. Lines from funnel bottoms converging to gate
        p.setPen(pen)
        p.drawLine(QPointF(left_x, y_funnel_bot), QPointF(cx, y_gate_top))
        p.drawLine(QPointF(right_x, y_funnel_bot), QPointF(cx, y_gate_top))

        # 5. Intersection gate
        self._draw_gate(p, cx, y_gate_top, y_gate_bot)

        # 6. Line from gate to language label box
        p.setPen(pen)
        p.drawLine(QPointF(cx, y_gate_bot), QPointF(cx, y_lang_top))

        # 7. Language label box (shows the intersection language name)
        self._draw_language_label(p, cx, y_lang_top, y_lang_bot)

        # 8. Line from language label to result box
        p.setPen(pen)
        p.drawLine(QPointF(cx, y_lang_bot), QPointF(cx, y_result_top))

        # 9. Result box
        result_rect = QRectF(
            cx - min(self.width() * 0.45, 380) / 2,
            y_result_top,
            min(self.width() * 0.45, 380),
            y_result_bot - y_result_top,
        )
        self._draw_result_box(p, result_rect)

        # 10. Arrow from result box down toward super PDA
        self._draw_arrow(p, QPointF(cx, y_result_bot), QPointF(cx, y_arrow_tip))

        p.end()

    # ── drawing helpers ──────────────────────────────────────────────────

    def _draw_funnel(
        self,
        p: QPainter,
        cx: float,
        top_y: float,
        bot_y: float,
        color: QColor,
        label: str,
        status: bool | None,
    ):
        half_top = 38
        half_bot = 10
        path = QPainterPath()
        path.moveTo(cx - half_top, top_y)
        path.lineTo(cx + half_top, top_y)
        path.lineTo(cx + half_bot, bot_y)
        path.lineTo(cx - half_bot, bot_y)
        path.closeSubpath()

        grad = QLinearGradient(cx, top_y, cx, bot_y)
        grad.setColorAt(0, color.lighter(130))
        grad.setColorAt(1, color.darker(130))
        p.setBrush(QBrush(grad))

        border_color = (
            QColor("#5CB85C")
            if status is True
            else (QColor("#E74C3C") if status is False else color.darker(150))
        )
        p.setPen(QPen(border_color, 2))
        p.drawPath(path)

        # Label
        p.setPen(_LABEL)
        font = QFont("sans-serif", 10, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(
            QRectF(cx - half_top, top_y, half_top * 2, bot_y - top_y),
            Qt.AlignmentFlag.AlignCenter,
            label,
        )

    def _draw_gate(self, p: QPainter, cx: float, top_y: float, bot_y: float):
        w = 100
        rect = QRectF(cx - w / 2, top_y, w, bot_y - top_y)
        p.setBrush(QBrush(_GATE_BG))
        p.setPen(QPen(_GATE_BORDER, 2))
        p.drawRoundedRect(rect, 6, 6)

        p.setPen(QColor("#ffffff"))
        font = QFont("sans-serif", 11, QFont.Weight.Bold)
        p.setFont(font)
        label = self.gate_status if self.gate_status else "\u2229 Gate"
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_language_label(self, p: QPainter, cx: float, top_y: float, bot_y: float):
        """Draw a box showing which intersection language was selected."""
        w = min(self.width() * 0.50, 400)
        rect = QRectF(cx - w / 2, top_y, w, bot_y - top_y)

        if self.language_label:
            p.setBrush(QBrush(_LANG_LABEL_BG))
            p.setPen(QPen(_LANG_LABEL_BORDER, 1.5))
            p.drawRoundedRect(rect, 5, 5)

            # Title line
            p.setPen(QColor("#8899bb"))
            font_sm = QFont("sans-serif", 9)
            p.setFont(font_sm)
            title_rect = QRectF(
                rect.x(), rect.y() + 2, rect.width(), (rect.height() / 2) - 2
            )
            p.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                "Intersection Language",
            )

            # Language name
            p.setPen(QColor("#ffffff"))
            font_lg = QFont("sans-serif", 13, QFont.Weight.Bold)
            p.setFont(font_lg)
            val_rect = QRectF(
                rect.x(),
                rect.y() + rect.height() / 2,
                rect.width(),
                rect.height() / 2 - 2,
            )
            p.drawText(
                val_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                self.language_label,
            )
        else:
            # No selection yet — dim placeholder
            p.setPen(QColor("#555555"))
            font = QFont("sans-serif", 10)
            p.setFont(font)
            p.drawText(
                rect, Qt.AlignmentFlag.AlignCenter, "Select both languages above"
            )

    def _draw_result_box(self, p: QPainter, rect: QRectF):
        p.setBrush(QBrush(_RESULT_BG))
        p.setPen(QPen(_RESULT_BORDER, 1.5))
        p.drawRoundedRect(rect, 5, 5)

        p.setPen(QColor("#e0e0e0"))
        font = QFont("monospace", 11)
        p.setFont(font)
        text = self.result_text if self.result_text else "(no match)"
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_arrow(self, p: QPainter, start: QPointF, end: QPointF):
        p.setPen(QPen(_ARROW, 2))
        p.drawLine(start, end)
        # Arrowhead
        head_size = 8
        p.setBrush(QBrush(_ARROW))
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.moveTo(end)
        path.lineTo(end.x() - head_size / 2, end.y() - head_size)
        path.lineTo(end.x() + head_size / 2, end.y() - head_size)
        path.closeSubpath()
        p.drawPath(path)
