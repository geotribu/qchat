# standard library
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QObject, QPoint, Qt, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QFrame, QPushButton, QWidget

# plugin
from qchat.__about__ import __icon_path__
from qchat.gui.emojis.dlg_emoji_picker_full import FullEmojiPicker


class EmojiHoverPreview(QFrame):
    """Quick emoji picker appearing when end-user hovers on a button."""

    emoji_selected = pyqtSignal(str)
    open_full_picker = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Load UI
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)
        self.setWindowIcon(QIcon(str(__icon_path__)))

        # Set window flags for popup behavior
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Popup | Qt.FramelessWindowHint)

        # Connect emoji buttons
        self.connect_emoji_buttons()

        # Connect more button
        self.moreButton.clicked.connect(self.open_full_picker.emit)

    def connect_emoji_buttons(self):
        """Connect all emoji buttons to the selection handler"""
        emoji_buttons = [
            self.emoji1,
            self.emoji2,
            self.emoji3,
            self.emoji4,
            self.emoji5,
            self.emoji6,
        ]

        for button in emoji_buttons:
            emoji = button.text()
            button.clicked.connect(lambda checked, e=emoji: self.emoji_clicked(e))
            button.setToolTip(f"Insert {emoji}")

    def emoji_clicked(self, emoji: str):
        """Handle quick emoji selection"""
        self.emoji_selected.emit(emoji)
        self.hide()

    def show_at_position(self, pos: QPoint):
        """Show the preview at a specific position"""
        # Ensure proper size before positioning
        if self.size().isEmpty():
            self.resize(250, 50)

        self.move(pos)
        self.show()


class EmojiButtonHandler(QObject):
    """Event filter class to handle emoji button hover and click behavior.
    Theorically, it can be attached to any QPushButton.
    """

    emoji_selected = pyqtSignal(str)

    def __init__(self, parent_button: QPushButton):
        super().__init__(parent_button)

        self.parent_button = parent_button

        # Create hover preview
        self.hover_preview = EmojiHoverPreview(parent_button.window())
        self.hover_preview.emoji_selected.connect(self.emoji_selected.emit)
        self.hover_preview.open_full_picker.connect(self.show_full_picker)

        # Hover timer
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_hover_preview)

        # Install event filter on the button
        self.parent_button.installEventFilter(self)

        # Connect button click to full picker
        self.parent_button.clicked.connect(self.show_full_picker)

    def eventFilter(self, qpush_button: QPushButton, event):
        """Handle hover events"""
        if qpush_button == self.parent_button:
            if event.type() == event.Enter:
                self.hover_timer.start(500)
            elif event.type() == event.Leave:
                self.hover_timer.stop()
                if not self.hover_preview.underMouse():
                    self.hover_preview.hide()

        return super().eventFilter(qpush_button, event)

    def show_hover_preview(self):
        """Show the hover preview popup"""
        if self.parent_button.isEnabled():
            global_pos = self.parent_button.mapToGlobal(
                self.parent_button.rect().bottomLeft()
            )
            global_pos.setY(global_pos.y() + 5)
            self.hover_preview.show_at_position(global_pos)

    def show_full_picker(self):
        """Show the full emoji picker dialog"""
        self.hover_preview.hide()

        picker = FullEmojiPicker(self.parent_button)
        picker.emoji_selected.connect(self.emoji_selected.emit)
        picker.exec_()
