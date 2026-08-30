import base64
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union

from processing.modeler.ModelerUtils import ModelerUtils
from processing.script import ScriptUtils
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsMapLayer,
    QgsPointXY,
    QgsProcessingModelAlgorithm,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QDateTime, QModelIndex, QSize, Qt
from qgis.PyQt.QtGui import QBrush, QColor, QFontMetrics, QIcon, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from qchat.constants import ADMIN_MESSAGES_AVATAR, ADMIN_MESSAGES_NICKNAME
from qchat.logic.qchat_messages import (
    QChatBboxMessage,
    QChatCrsMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatModelMessage,
    QChatPositionMessage,
    QChatScriptMessage,
    QChatTextMessage,
)
from qchat.toolbelt import PlgOptionsManager
from qchat.toolbelt.log_handler import PlgLogger
from qchat.toolbelt.preferences import PlgSettingsStructure

TIME_COLUMN = 0
AUTHOR_COLUMN = 1
MESSAGE_COLUMN = 2

MAX_IMAGE_ITEM_HEIGHT = 24


class QChatMessageWrapDelegate(QStyledItemDelegate):
    """
    Delegate to wrap text column in QTreeWidgetItem.
    """

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        self.initStyleOption(option, index)
        painter.save()

        style = option.widget.style() if option.widget else QApplication.style()
        if style:
            style.drawPrimitive(
                QStyle.PrimitiveElement.PE_PanelItemViewItem,
                option,
                painter,
                option.widget,
            )

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            color_data = index.data(Qt.ItemDataRole.ForegroundRole)
            if color_data:
                painter.setPen(color_data.color())
            elif option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(option.palette.highlightedText().color())
            else:
                painter.setPen(option.palette.text().color())

            rect = option.rect.adjusted(4, 2, -4, -2)
            painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        tree = option.widget
        column_width = (
            tree.columnWidth(index.column()) - 8 if tree else option.rect.width() - 8
        )
        if column_width <= 0:
            return super().sizeHint(option, index)

        fm = QFontMetrics(option.font)
        bounding = fm.boundingRect(
            0, 0, column_width, 0, Qt.TextFlag.TextWordWrap, text
        )
        return QSize(column_width, max(bounding.height() + 4, 20))


class QChatTreeWidgetItem(QTreeWidgetItem):
    """
    Custom QTreeWidgetItem implementation for QChat
    A QChatTreeWidgetItem should not be implemented
    See inheriting classes for implementation
    """

    def __init__(
        self,
        parent: Union[QTreeWidget, "QChatTreeWidgetItem"],
        datetime: QDateTime,
        author: str,
        avatar: Optional[str],
        message_id: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.plg_settings = PlgOptionsManager()
        self.datetime = datetime
        self.author = author
        self.avatar = avatar
        self.message_id = message_id

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def init_time_and_author(self) -> None:
        self.setText(TIME_COLUMN, self.datetime.toLocalTime().time().toString())
        self.setToolTip(TIME_COLUMN, self.datetime.date().toString())
        self.setText(AUTHOR_COLUMN, self.author)
        if self.settings.show_avatars and self.avatar:
            self.setIcon(AUTHOR_COLUMN, QIcon(QgsApplication.iconPath(self.avatar)))

    def set_foreground_color(self, color: str) -> None:
        fg_color = QBrush(QColor(color))
        self.setForeground(TIME_COLUMN, fg_color)
        self.setForeground(AUTHOR_COLUMN, fg_color)
        self.setForeground(MESSAGE_COLUMN, fg_color)

    def on_click(self, column: int) -> None:
        """
        Triggered when simple clicking on the item
        Empty because this is the expected behaviour
        :param column: column that has been clicked
        """
        pass

    @property
    def can_be_replied_to(self) -> bool:
        return self.message_id is not None

    @property
    def can_be_liked(self) -> bool:
        """
        Returns if the item can be liked
        """
        return self.author != self.settings.nickname

    @property
    def liked_message(self) -> str:
        """
        Returns the text message that was liked
        """
        pass

    @property
    def can_be_mentioned(self) -> bool:
        """
        Returns if the item can be mentioned
        """
        return self.author != self.settings.nickname

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        """
        Returns if the item can be copied to clipboard
        """
        return False

    def copy_to_clipboard(self) -> None:
        """
        Performs action of copying message to clipboard
        If the can_be_copied_to_clipboard is enabled ofc
        """
        pass

    def tr(self, text: str) -> str:
        return self.treeWidget().tr(text)


class QChatAdminTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, text: str, timestamp: Optional[int] = None):
        if timestamp is None:
            datetime = QDateTime.currentDateTime()
        else:
            datetime = QDateTime.fromSecsSinceEpoch(timestamp)
        super().__init__(
            parent, datetime, ADMIN_MESSAGES_NICKNAME, ADMIN_MESSAGES_AVATAR
        )
        self.text = text
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, text)
        self.setToolTip(MESSAGE_COLUMN, text)
        self.set_foreground_color(self.settings.color_admin)

    @property
    def can_be_liked(self) -> bool:
        return False

    @property
    def can_be_mentioned(self) -> bool:
        return False


class QChatTextTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatTextMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, message.text)
        self.setToolTip(MESSAGE_COLUMN, message.text)

        # set foreground color if user is mentioned
        words = message.text.split(" ")
        if f"@{self.settings.nickname}" in words or "@all" in words:
            self.set_foreground_color(self.settings.color_mention)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

    @property
    def liked_message(self) -> str:
        return self.message.text

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.text)


class QChatImageTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatImageMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        self.pixmap = QPixmap()
        data = base64.b64decode(message.image_data)
        self.pixmap.loadFromData(data)

        image_button = QPushButton(self.tr("Image - click to view"))
        scaled = self.pixmap.scaledToHeight(
            MAX_IMAGE_ITEM_HEIGHT, Qt.TransformationMode.SmoothTransformation
        )
        image_button.setIcon(QIcon(scaled))
        image_button.setCursor(Qt.CursorShape.PointingHandCursor)
        image_button.clicked.connect(self.show_image)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, image_button)

    def show_image(self) -> None:
        dialog = QDialog(self.treeWidget())
        dialog.setWindowTitle(
            self.tr("QChat image sent by {author}").format(author=self.author)
        )
        layout = QVBoxLayout()
        label = QLabel()
        label.setPixmap(self.pixmap)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.setModal(True)
        dialog.show()

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.show_image()

    @property
    def liked_message(self) -> str:
        return "image"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setPixmap(self.pixmap)


class QChatGeojsonTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatGeojsonMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        vector_layer_button = QPushButton(
            self.tr("Layer '{layer}' (#{nb}) - click to load").format(
                layer=self.message.layer_name,
                nb=len(self.message.geojson["features"]),
                crs=self.message.crs_authid,
            )
        )
        vector_layer_button.setIcon(
            QIcon(QgsApplication.iconPath("mActionAddLayer.svg"))
        )
        vector_layer_button.setCursor(Qt.CursorShape.PointingHandCursor)
        vector_layer_button.setToolTip(self.liked_message)
        vector_layer_button.clicked.connect(self.load_layer_from_geojson)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, vector_layer_button)

    def load_layer_from_geojson(self) -> None:
        temp_directory = Path(tempfile.gettempdir())
        save_path = temp_directory / f"{self.message.layer_name}.geojson"
        with open(save_path, "w") as file:
            json.dump(self.message.geojson, file)

        save_style_path = temp_directory / f"{self.message.layer_name}_style.qml"
        with open(save_style_path, "w", encoding="utf-8") as style_file:
            style_file.write(self.message.style)

        layer = QgsVectorLayer(str(save_path), self.message.layer_name, "ogr")
        layer.setCrs(QgsCoordinateReferenceSystem.fromWkt(self.message.crs_wkt))
        layer.loadNamedStyle(
            str(save_style_path),
            loadFromLocalDb=False,
            categories=QgsMapLayer.StyleCategory.AllStyleCategories,
        )
        QgsProject.instance().addMapLayer(layer)

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.load_layer_from_geojson()

    @property
    def liked_message(self) -> str:
        layer_name = self.message.layer_name
        nb_features = len(self.message.geojson["features"])
        crs = self.message.crs_authid
        return f'<layer "{layer_name}": {nb_features} features, CRS={crs}>'

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(json.dumps(self.message.geojson))


class QChatCrsTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatCrsMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        crs_button = QPushButton(
            self.tr("CRS ({crs}) - click to set").format(crs=self.message.crs_authid)
        )
        crs_button.setIcon(QIcon(QgsApplication.iconPath("mActionSetProjection.svg")))
        crs_button.setCursor(Qt.CursorShape.PointingHandCursor)
        crs_button.setToolTip(self.liked_message)
        crs_button.clicked.connect(self.set_project_crs)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, crs_button)

    def set_project_crs(self) -> None:
        crs = QgsCoordinateReferenceSystem.fromWkt(self.message.crs_wkt)
        QgsProject.instance().setCrs(crs)

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.set_project_crs()

    @property
    def liked_message(self) -> str:
        return f"<CRS {self.message.crs_authid}>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.crs_wkt)


class QChatBboxTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatBboxMessage, canvas: QgsMapCanvas):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp).toLocalTime(),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.canvas = canvas
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        bbox_button = QPushButton(
            self.tr("BBOX ({crs}) - click to fit").format(crs=self.message.crs_authid)
        )
        bbox_button.setIcon(
            QIcon(QgsApplication.iconPath("mActionViewExtentInCanvas.svg"))
        )
        bbox_button.setCursor(Qt.CursorShape.PointingHandCursor)
        bbox_button.setToolTip(self.liked_message)
        bbox_button.clicked.connect(self.zoom_to_bbox)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, bbox_button)

    def zoom_to_bbox(self) -> None:
        project = QgsProject.instance()
        tr = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(self.message.crs_wkt),
            project.crs(),
            project,
        )
        rect = QgsRectangle(
            tr.transform(QgsPointXY(self.message.xmin, self.message.ymin)),
            tr.transform(QgsPointXY(self.message.xmax, self.message.ymax)),
        )
        self.canvas.setExtent(rect)
        self.canvas.refresh()

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.zoom_to_bbox()

    @property
    def liked_message(self) -> str:
        msg = f"[{self.message.xmin} {self.message.ymin}, {self.message.xmax} {self.message.ymax}]"
        return f"<BBOX {self.message.crs_authid}: {msg}>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        msg = f"[{self.message.xmin} {self.message.ymin}, {self.message.xmax} {self.message.ymax}]"
        QgsApplication.instance().clipboard().setText(msg)


class QChatPositionTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatPositionMessage, canvas: QgsMapCanvas):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp).toLocalTime(),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.canvas = canvas
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        position_button = QPushButton(self.tr("Position - click to move to"))
        position_button.setIcon(QIcon(QgsApplication.iconPath("mActionPanTo.svg")))
        position_button.setCursor(Qt.CursorShape.PointingHandCursor)
        position_button.setToolTip(self.liked_message)
        position_button.clicked.connect(self.move_to_position)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, position_button)

    def move_to_position(self) -> None:
        source_crs = QgsCoordinateReferenceSystem.fromWkt(self.message.crs_wkt)
        dest_crs = self.canvas.mapSettings().destinationCrs()
        transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())

        point = transform.transform(QgsPointXY(self.message.x, self.message.y))

        self.canvas.setCenter(point)
        self.canvas.refresh()

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.move_to_position()

    @property
    def liked_message(self) -> str:
        return f"({self.message.x}-{self.message.y})"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.liked_message)


class QChatModelTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatModelMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp).toLocalTime(),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        model_button = QPushButton(
            self.tr("Graphic Model '{model}' - click to load").format(
                model=self.message.model_name,
            )
        )
        model_button.setIcon(QIcon(QgsApplication.iconPath("processingModel.svg")))
        model_button.setCursor(Qt.CursorShape.PointingHandCursor)
        model_button.setToolTip(self.liked_message)
        model_button.clicked.connect(self.load_graphical_model)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, model_button)

    def load_graphical_model(self) -> None:
        temp_file_path = (
            Path(tempfile.gettempdir()) / f"{self.message.model_name}.model3"
        )
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(self.message.raw_xml)

        # load the xml into a processing model
        model = QgsProcessingModelAlgorithm()
        if not model.fromFile(str(temp_file_path)):
            PlgLogger().log(
                message=f"Error while loading model '{self.message.model_name}': invalid model file.",
                log_level=Qgis.MessageLevel.Critical,
            )
            return

        # check that there is at least one model directory to copy the file into,
        # otherwise the model won't be loaded in the registry and thus not usable
        if len(ModelerUtils.modelsFolders()) == 0:
            PlgLogger().log(
                message=f"Error while loading model '{self.message.model_name}': no model directory found. Please set a model directory in Processing options.",
                log_level=Qgis.MessageLevel.Critical,
            )
            return

        model_dest_path = (
            Path(ModelerUtils.modelsFolders()[0]) / "qchat" / temp_file_path.name
        )
        model_dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(str(temp_file_path), str(model_dest_path))
        QgsApplication.processingRegistry().providerById("model").refreshAlgorithms()

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.load_graphical_model()

    @property
    def liked_message(self) -> str:
        return f"<MODEL {self.message.model_name} [{self.message.model_group or self.tr('no group')}]>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.raw_xml)


class QChatScriptTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent, message: QChatScriptMessage):
        super().__init__(
            parent,
            QDateTime.fromSecsSinceEpoch(message.timestamp).toLocalTime(),
            message.author,
            message.avatar,
            message_id=message.id,
        )
        self.message = message
        self.init_time_and_author()
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.nickname:
            self.set_foreground_color(self.settings.color_self)

        script_button = QPushButton(
            self.tr("Script '{script}' - click to load").format(
                script=self.message.name,
            )
        )
        script_button.setIcon(QIcon(QgsApplication.iconPath("processingScript.svg")))
        script_button.setCursor(Qt.CursorShape.PointingHandCursor)
        script_button.setToolTip(self.liked_message)
        script_button.clicked.connect(self.load_script)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, script_button)

    def load_script(self) -> None:
        temp_file_path = Path(tempfile.gettempdir()) / f"{self.message.name}.py"
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(self.message.raw_pycode)

        script_dest_path = (
            Path(ScriptUtils.scriptsFolders()[0]) / "qchat" / temp_file_path.name
        )
        script_dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(str(temp_file_path), str(script_dest_path))
        QgsApplication.processingRegistry().providerById("script").refreshAlgorithms()

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            self.load_script()

    @property
    def liked_message(self) -> str:
        return f"<SCRIPT {self.message.name}>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.raw_pycode)
