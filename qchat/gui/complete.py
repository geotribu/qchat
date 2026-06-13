from qgis.PyQt.QtCore import QEvent, QObject, Qt
from qgis.PyQt.QtWidgets import (
    QCompleter,
)


class QChatTextMessageCompleter(QCompleter):
    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        """
        If enter key is pressed, hide the popup and do not propagate.
        This means that the enter event is not propagated, so no message sent.
        """
        if event.type() == QEvent.Type.KeyPress and event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            if self.popup().isVisible() and self.popup().currentIndex().isValid():
                self.popup().hide()
                return True

        return super().eventFilter(object, event)
