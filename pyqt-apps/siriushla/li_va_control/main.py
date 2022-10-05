"""Main window of the Vacuum Control."""

import os as _os
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QPushButton
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, VGC_DETAILS
from .chart import ChartWindow
from .details import DetailWindow, IpsDetailWindow, VgcDetailWindow
from .functions import BaseFunctionsInterface
from ..widgets import RelativeWidget


class VacuumMain(QWidget, BaseFunctionsInterface):
    """ Vaccum Control Main Window """

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.setObjectName('LIApp')
        self.setWindowTitle('LI Vacuum')
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "vacuum.png"))
        self.relative_widgets = []
        self.pump_list = []
        self.vgc_list = []
        self.graphs = []
        self.gen_btn = []
        self.window = None

        self._setupui()

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if event.type() == QEvent.Resize:
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def saveRelWid(self, widget, size, coord):
        """ Save relative widget to list """
        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=widget,
            relative_pos=coord + size)
        self.relative_widgets.append(rel_wid)

    def saveWidToList(self, widget, cat):
        """ Save widget to list """
        if cat == "Vacuum":
            self.vgc_list.append(widget)
        else:
            self.pump_list.append(widget)

    def selWindow(self, cat, id_win=0):
        """ Open selected window with click """
        if cat == "CCG Graphs":
            self.window = ChartWindow()
        elif cat == "Pump":
            self.window = IpsDetailWindow(id_ips=id_win)
        elif cat == "Vacuum":
            self.window = VgcDetailWindow(id_vgc=id_win)
        else:
            self.window = DetailWindow()
        self.window.show()

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(1580, 0)
        return self.image_container

    def setupVgcList(self, config):
        """ Display VGC Widget List with all VGC elements """
        wid, lay = self.getLayoutWidget()
        id_vgc = 1
        for item in self.vgc_list:
            pos = self.getVacPosition(id_vgc)
            lay.addWidget(item, pos[0], pos[1])
            self.saveRelWid(
                wid, config['size'], config['coord'])
            id_vgc += 1

    def setupIPSList(self, config):
        """ Display IPS Widget List with all IPS elements """
        wid, lay = self.getLayoutWidget()
        pos = [0, 0]
        for item in self.pump_list:
            if pos[0] >= 10 and pos[1] == 0:
                pos[0] = 0
                pos[1] = 1
            lay.addWidget(item, pos[0], pos[1])
            self.saveRelWid(
                wid, config['size'], config['coord'])
            pos[0] += 1

    def setupLists(self, cat):
        """ Select which widget list to build """
        config = PVS_CONFIG[cat]['list']
        if cat == "Vacuum":
            self.setupVgcList(config)
        else:
            self.setupIPSList(config)

    def buildVacInfo(self, config, id_num, lay):
        """ Display VGC basic information """

        name, dev_gen = self.buildVacPv(id_num)
        pv_name = config['prefix'] + name
        led_config = VGC_DETAILS["led"]
        led_name = pv_name+led_config["text"]
        unit_name = pv_name+VGC_DETAILS["Pressure<br/>Readback"]+str(dev_gen)
        lay.addWidget(
            self.setupUnitView(unit_name),
            alignment=Qt.AlignCenter)
        led = self.getVgcLed(led_name, id_num, led_config["sufix"])
        lay.addWidget(led, alignment=Qt.AlignCenter)

    def getGroupWidgets(self, config, item, cat, orient):
        """ Select and build group widget """

        pv_name = self.buildIdName(item, cat == "Valve")
        pv_name = config["prefix"] + pv_name
        if cat == "Valve":
            widget = self.buildLed(
                pv_name, config['sufix'], "on/off")
        elif cat == "Pump":
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            self.buildIPSInfo(
                pv_name, lay, orient)
        else:
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            self.buildVacInfo(config, item, lay)
        return widget

    def setupMainWidgets(self, cat="Vacuum"):
        """ Display relative widgets and save list items """
        lay = QVBoxLayout()
        lay.setSpacing(0)
        config = PVS_CONFIG[cat]
        pv_range = config["iterations"]
        lists = ['V', 'H']
        if cat == "Valve":
            lists = ['']
        for orient in lists:
            for item in range(pv_range[0], pv_range[1]+1):
                coord = config["position"][item-1]
                widget = self.getGroupWidgets(
                    config, item, cat, orient)
                if orient == 'H':
                    self.saveWidToList(widget, cat)
                else:
                    self.saveRelWid(
                        widget, config["size"], coord)

    def buildAllLegendsRel(self):
        """ Display Legend in a relative widget"""
        size = LEGEND['size']
        coord = [50, 85]
        for leg in ['CCG', 'PRG']:
            self.saveRelWid(
                self.setupLegend(leg), size, coord)
            coord[0] += 6
            coord[1] -= 0.25

    def setupButtons(self):
        """ Display button menu """
        size = [10, 8]
        coord = [35, 85]
        count = 0
        for title in ['Details', 'CCG Graphs']:
            btn = QPushButton(title)
            btn.clicked.connect(
                lambda state, title=title: self.selWindow(title))
            self.gen_btn.append(btn)
            self.saveRelWid(
                self.gen_btn[-1],
                size, coord)
            coord[1] += 5
            count += 1

    def _setupui(self):
        """."""
        lay = QGridLayout()
        self.setLayout(lay)

        lay.addWidget(self.imageViewer(), 0, 0)
        for wid_cat in PVS_CONFIG:
            self.setupMainWidgets(wid_cat)
            if wid_cat != "Valve":
                self.setupLists(wid_cat)

        self.buildAllLegendsRel()
        self.setupButtons()
