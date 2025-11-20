# standard library
import json
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import Qgis
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QGridLayout, QPushButton, QScrollArea, QWidget

# plugin
from qchat.__about__ import DIR_PLUGIN_ROOT, __icon_path__
from qchat.toolbelt import PlgLogger
from qchat.toolbelt.font_helper import PlgFontHelper


class FullEmojiPicker(QDialog):
    """Full emoji picker."""

    emoji_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.log = PlgLogger().log
        self.font_helper = PlgFontHelper()

        # Load UI
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)
        self.setWindowIcon(QIcon(str(__icon_path__)))

        # Load emoji data
        self.emoji_categories = self.load_emojis_from_json()

        # Setup the picker
        self.setup_emoji_tabs()

        # Connect search
        self.lne_search_box.textChanged.connect(self.filter_emojis)

        self.adjustSize()

    def load_emojis_from_json(self):
        """Load emoji categories from JSON file"""
        try:
            with DIR_PLUGIN_ROOT.joinpath("resources/emojis/selection.json").open(
                mode="r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            # Convert JSON structure
            categories = {}
            json_categories = data.get("categories", {})

            for category_id, category_data in json_categories.items():
                category_name = category_data.get("name", category_id.title())
                emojis_list = []

                for emoji_data in category_data.get("emojis", []):
                    emojis_list.append(emoji_data.get("emoji", ""))

                if emojis_list:
                    categories[category_name] = emojis_list

            return categories

        except (FileNotFoundError, json.JSONDecodeError) as err:
            self.log(
                message=self.tr(
                    "Error loading emojis: {}\Fallback to defaults embedded shortlist."
                ).format(err),
                log_level=Qgis.MessageLevel.Warning,
                duration=3,
                push=True,
            )
            return self.get_default_emojis()

    def get_default_emojis(self):
        """Fallback emoji categories"""
        return {
            "Smileys": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇"],
            "Gestures": ["👍", "👎", "👌", "✌️", "🤞", "👋", "👏", "🙌", "🙏", "💪"],
        }

    def setup_emoji_tabs(self):
        """Create tabs with emoji grids"""
        for category_name, emojis in self.emoji_categories.items():
            emojis_tab = self.create_emoji_tab(emojis)
            self.tabWidget.addTab(emojis_tab, category_name.title())

    def create_emoji_tab(self, emojis):
        """Create a tab with emoji buttons"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)

        row, col = 0, 0
        for emoji in emojis:
            if not emoji:
                continue

            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.setFont(self.font_helper.get_font_from_settings())
            btn.clicked.connect(lambda checked, e=emoji: self.emoji_clicked(e))
            btn.setToolTip(f"Insert {emoji}")

            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= 10:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area

    def emoji_clicked(self, emoji):
        """Handle emoji selection"""
        self.emoji_selected.emit(emoji)
        self.close()

    def filter_emojis(self, search_text):
        """Basic emoji filtering"""
        if search_text:
            self.tabWidget.setCurrentIndex(0)
