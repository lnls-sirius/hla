import os as _os
from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import QLabel, QSizePolicy, QWidget, \
    QGridLayout, QTabWidget
from qtpy.QtGui import QPixmap

from pydm.widgets import PyDMLineEdit
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.widgets import RelativeWidget, SiriusLabel, \
    SiriusLedAlert
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import SCREENS
from .widgets import PolygonWidget, RotatedQLabel


class CryoControl(SiriusMainWindow):

    def __init__(self, parent=None, screen="All", prefix=_VACA_PREFIX):
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.prefix += "UA-10DHall:CR-IHMCtrl:"
        self.relative_widgets = []
        self.screen = screen
        self._setupUi()

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def get_pvname(self, name):
        return self.prefix + name + "-Mon"

    def add_background_image(self):
        img_path = SCREENS[self.screen]["image"]
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
        labels = SCREENS[self.screen]["labels"]
        for text, config in labels.items():
            isTuple = isinstance(config, tuple)
            if isTuple:
                self.create_label(text, config[0])
                config = config[1]
            self.create_label(text, config)

    def get_label_widget(self, text, config):
        isDict = isinstance(config, dict)
        if isDict:
            hasSideArrows = (config["shape"] == "side_arrows")
            isRotated = "rotation" in config
            if hasSideArrows:
                color = config["color"]
                return PolygonWidget(
                    text, color, self.image_container)
            if isRotated:
                return RotatedQLabel(text, config["rotation"])
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def handle_label_highlight(self, config, lbl):
        isDict = isinstance(config, dict)
        if isDict:
            lbl.setStyleSheet("""
                background-color: """+config["color"]+""";
                color: #ffffff;
                font-size: 12px;
            """)
            return config["position"]
        return config

    def get_label_height(self, text, config):
        hasJumpLine = "\n" in text
        isRotated = "rotation" in config
        if hasJumpLine:
            return 6
        if isRotated:
            return 25
        return 4

    def get_label_width(self, config):
        isRotated = "rotation" in config
        if isRotated:
            return 4
        return 7.9

    def create_label(self, text, config):
        lbl = self.get_label_widget(text, config)
        position = self.handle_label_highlight(config, lbl)
        height = self.get_label_height(text, config)
        width = self.get_label_width(config)
        self.save_relative_widget(lbl, [width, height], position)

    def get_pydm_widget(self, pvname, isEditable):
        if isEditable:
            pydm_line = PyDMLineEdit(init_channel=pvname)
            pydm_line.setStyleSheet("background-color: #ffffff;")
            return pydm_line
        pydm_lbl = SiriusLabel(
            init_channel=pvname)
        pydm_lbl.setAlignment(Qt.AlignCenter)
        return pydm_lbl

    def add_label_egu(self, pvname, lay, line, isEditable=False):
        pvname = self.get_pvname(pvname)
        wid = self.get_pydm_widget(pvname, isEditable)
        lay.addWidget(wid, line, 0, 1, 1)
        pydm_lbl = SiriusLabel(
            init_channel=pvname+".EGU")
        pydm_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(pydm_lbl, line, 1, 1, 1)

        return lay

    def set_pydm_widget(self, config, lay):
        line = 1
        pvname = config["pvname"]
        isEditable = ("editable" in config)
        isTuple = isinstance(pvname, tuple)
        if isTuple:
            lay = self.add_label_egu(
                pvname[0], lay, line)
            pvname = pvname[1]
            line += 1

        lay = self.add_label_egu(
            pvname, lay, line, isEditable)

        return lay

    def get_pv_height(self, config):
        isTuple = isinstance(config["pvname"], tuple)
        if isTuple:
            return 8
        return 6

    def create_pv_group(self):
        wid = QWidget()
        lay = QGridLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        wid.setLayout(lay)

        return wid, lay

    def handle_group_highlight(self, config, group):
        bg_color = config["color"]
        isTransparent = len(bg_color)>=8
        white = "#ffffff"
        black = "#000000"
        txt_color = black if isTransparent else white
        group.setStyleSheet("""
            background-color: """+bg_color+""";
            color: """+txt_color+""";
            border-bottom: 1px solid #ffffff;
            border-right: 1px solid #ffffff;
        """)

    def set_group_title(self, title, glay):
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, 0, 0, 1, 2)

    def add_pvs(self):
        pvs = SCREENS[self.screen]["pvs"]
        for text, config in pvs.items():
            wid, glay = self.create_pv_group()
            self.handle_group_highlight(config, wid)
            self.set_group_title(text, glay)
            self.set_pydm_widget(config, glay)
            height = self.get_pv_height(config)
            self.save_relative_widget(
                wid, [7.25, height], config["position"])

    def get_led(self, pvname):
        pvname = self.get_pvname(pvname)
        led = SiriusLedAlert(
            init_channel=pvname)
        led.shape = 3
        led.setFixedSize(7, 7)
        return led

    def add_leds(self):
        ledsExist = "leds" in SCREENS[self.screen]
        if ledsExist:
            leds = SCREENS[self.screen]["leds"]
            for config in leds.values():
                wid = self.get_led(config["pvname"])
                self.save_relative_widget(
                    wid, [10, 10], config["position"])

    def setup_one_screen(self):

        bg_img = self.add_background_image()
        self.add_labels()
        self.add_pvs()
        self.add_leds()

        return bg_img

    def get_tab_stylesheet(self):
        return """
            QTabWidget::pane {
                border-bottom: 2px solid black;
            }

            QTabWidget::tab-bar {
                left: 20em;
            }

            QTabBar::tab {
                color: black;
                /*background-color: white;*/
                padding: 0 1em 0 1em;
                margin: 0em;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                border: 0.1em solid black;
                margin-top: 0.0em;
            }
            QTabBar::tab:!selected {
                background-color: grey;
                margin-bottom: 0.2em;
                font-weight: 200;
            }
        """

    def setup_all_screens(self):
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.South)
        tabs.setStyleSheet(self.get_tab_stylesheet())
        for title in SCREENS.keys():
            self.screen = title
            bg_img = self.setup_one_screen()
            tabs.addTab(bg_img, title)

        return tabs

    def _setupUi(self):
        if self.screen != "All":
            wid = self.setup_one_screen()
        else:
            wid = self.setup_all_screens()

        self.setCentralWidget(wid)
