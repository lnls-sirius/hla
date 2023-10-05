import os as _os
from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import QLabel, QSizePolicy, QWidget, \
    QGridLayout
from qtpy.QtGui import QPixmap

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets import RelativeWidget, SiriusLabel
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LABELS, PVS
from .background import PolygonWidget


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

    def add_background_image(self, img_path):
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

    def get_label(self, text, config):
        if isinstance(config, dict):
            if config["shape"]=="round":
                color = config["color"]
                lbl = PolygonWidget(
                    text, color, self.image_container)
            else:
                lbl = QLabel(text)
                lbl.setAlignment(Qt.AlignCenter)
        else:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)

        return lbl

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
        lbl = self.get_label(text, config)
        position = self.handle_highlight(config, lbl)
        self.save_relative_widget(lbl, [7.8, 4], position)

    def add_labels(self):
        for text, config in LABELS.items():
            if isinstance(config, tuple):
                self.create_label(text, config[0])
                config = config[1]
            self.create_label(text, config)

    def add_label_egu(self, pvname, lay, line):
        pydm_lbl = SiriusLabel(
            init_channel=pvname)
        pydm_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(pydm_lbl, line, 0, 1, 1)

        pydm_lbl = SiriusLabel(
            init_channel=pvname+".EGU")
        pydm_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(pydm_lbl, line, 1, 1, 1)

        return lay

    def create_pydm_group(self, config, lay):
        line = 1
        pvname = config["pvname"]
        if isinstance(pvname, tuple):
            lay = self.add_label_egu(
                pvname[0], lay, line)
            pvname = pvname[1]
            line += 1

        lay = self.add_label_egu(
            pvname, lay, line)

        return lay

    def add_pvs(self):
        for text, config in PVS.items():
            wid = QWidget()
            glay = QGridLayout()
            glay.setContentsMargins(0, 0, 0, 0)
            glay.setSpacing(0)
            wid.setLayout(glay)

            color = config["color"]
            wid.setStyleSheet("""
                background-color: """+color+""";
                color: #ffffff;
                border-bottom: 1px solid #ffffff;
                border-right: 1px solid #ffffff;
            """)

            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            glay.addWidget(lbl, 0, 0, 1, 2)

            glay = self.create_pydm_group(config, glay)
            wid.setLayout(glay)

            if isinstance(config["pvname"], tuple):
                height = 8
            else:
                height = 6
            self.save_relative_widget(
                wid, [7.25, height], config["position"])

    def _setupUi(self):
        bg_img = self.add_background_image("cryo1")
        self.add_labels()
        self.add_pvs()

        self.setCentralWidget(bg_img)
