from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt

CONTROL_KEY_MIN = 0
CONTROL_KEY_MAX = 0x01000000
CONTROL_MODIFIER = Qt.KeyboardModifier.ControlModifier
META_MODIFIER = Qt.KeyboardModifier.MetaModifier

class ValidatedLineEdit(QLineEdit):
    def __init__(self, allowed_chars=None, parent=None):
        super().__init__(parent)
        self.allowed_chars = allowed_chars if allowed_chars is not None else set()

    def keyPressEvent(self, event: QKeyEvent):
        text = event.text()
        key = event.key()

        # Always allow control keys (Backspace, Delete, Left, Right, etc.)
        is_control = (key < CONTROL_KEY_MIN) or (key > CONTROL_KEY_MAX) or \
                     (event.modifiers() & CONTROL_MODIFIER) or \
                     (event.modifiers() & META_MODIFIER)

        if is_control or not text:
             super().keyPressEvent(event)
             return

        if text in self.allowed_chars:
            super().keyPressEvent(event)
        else:
            ## Ignoring invalid characters
            pass
