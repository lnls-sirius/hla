import os as _os
from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import QLabel, QSizePolicy, QGroupBox, \
    QVBoxLayout
from qtpy.QtGui import QPixmap

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets import RelativeWidget, SiriusLabel
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LABELS, PVS


class CryoMain(SiriusMainWindow):

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.relative_widgets = []
        self._setupUi()

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def add_image(self, img_path):
        self.image_container = QLabel()
        img_file = (img_path + ".png")
        pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), img_file))
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_container.setPixmap(pixmap)
        self.image_container.setMinimumSize(1750, 850)
        self.image_container.installEventFilter(self)

        return self.image_container

    def save_relative_widget(self, widget, size, coord):
        """ Save relative widget to list """
        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=widget,
            relative_pos=coord + size)

        self.relative_widgets.append(rel_wid)

    def add_labels(self):
        for text, config in LABELS.items():
            if isinstance(config, tuple):
                self.create_label(text, config[0])
                config = config[1]
            self.create_label(text, config)

    def handle_highlight(self, config, lbl):
        if isinstance(config, dict):
            lbl.setStyleSheet("""
                background-color: """+config["color"]+""";
                color: #ffffff;
                font-size: 12px;
            """)

            return config["position"]
        return config

    def create_label(self, text, config):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        position = self.handle_highlight(config, lbl)
        self.save_relative_widget(lbl, [7.5, 4], position)

    def add_labels(self):
        for text, config in LABELS.items():
            if isinstance(config, tuple):
                self.create_label(text, config[0])
                config = config[1]
            self.create_label(text, config)

    def add_sirius_label(self, pvname, color):
        pydm_lbl = SiriusLabel(init_channel=pvname)
        pydm_lbl.showUnits = True

        pydm_lbl.setStyleSheet("""
            background-color: """+color+""";
            color: #ffffff;
            margin-top: 2px;
        """)

        return pydm_lbl

    def create_pydm_group(self, config):
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)

        pvname = config["pvname"]
        color = config["color"]
        if isinstance(pvname, tuple):
            pydm_lbl = self.add_sirius_label(
                pvname[0], color)
            lay.addWidget(pydm_lbl)
            pvname = pvname[1]

        pydm_lbl = self.add_sirius_label(
            pvname, color)
        lay.addWidget(pydm_lbl)

        return lay

    def add_pvs(self):
        for text, config in PVS.items():
            group = QGroupBox()
            group.setTitle(text)

            lay = self.create_pydm_group(config)
            group.setLayout(lay)

            if isinstance(config["pvname"], tuple):
                height = 10
            else:
                height = 7
            self.save_relative_widget(
                group, [7.5, height], config["position"])

    def _setupUi(self):
        bg_img = self.add_image("cryo1")
        self.add_labels()
        self.add_pvs()

        self.setCentralWidget(bg_img)
