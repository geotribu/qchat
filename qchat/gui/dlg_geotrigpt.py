import random
import string
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

POOL = string.ascii_letters + string.digits + string.punctuation


# ############################################################################
# ########## Classes ###############
# ##################################


class GeotriGPTDialog(FORM_CLASS, QDialog):
    """Dialog of GeotriGPT, the AI Agent powered by GeoTribu(c)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.lne_prompt.textEdited.connect(self.scramble_prompt_text)

    def scramble_prompt_text(self, text: str) -> None:
        # Messes up characters in the prompt text
        pos = self.lne_prompt.cursorPosition()
        diff = len(text) - len(getattr(self, "_prev", ""))

        if diff > 0:
            start = pos - diff
            chars = list(text)
            for i in range(start, pos):
                chars[i] = random.choice(POOL)
            text = "".join(chars)

            self.lne_prompt.blockSignals(True)
            self.lne_prompt.setText(text)
            self.lne_prompt.setCursorPosition(pos)
            self.lne_prompt.blockSignals(False)

        if not hasattr(self, "_prev"):
            self._prev = text
        else:
            self._prev = text
