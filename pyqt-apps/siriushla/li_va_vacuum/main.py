"""Main module of the Application Interface."""

import os as _os
import qtawesome as _qta
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QPushButton
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, COLORS, VGC_DETAILS
from .chart import ChartWindow
from .details import DetailWindow, IpsDetailWindow, VgcDetailWindow
from .widgets import QGroupBoxButton
from .functions import buildIPSInfo, buildIdsVac, buildIdName, buildLed, buildVacPv, getGroupTitle, \
    getLayoutWidget, getVacPosition, getVgcLed, showLegend, showUnitView
from ..widgets import RelativeWidget

class VacuumMain(QWidget):
    """."""

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
        self.pumpList = []
        self.vacList = []
        self.graphs = []
        self.genBtn = []
        self._setupui()
        
    def selWindow(self, cat, id=0):
        if cat == "CCG Graphs":
            self.window = ChartWindow()
        elif cat == "Pump":
            self.window = IpsDetailWindow(id_ips=id)
        elif cat == "Vacuum":
            self.window = VgcDetailWindow(id_vgc=id)
        else:
            self.window = DetailWindow()
        self.window.show()

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(1580, 0)
        return self.image_container

    def buildVacInfo(self, config, id_num, lay):
        name, dev_gen = buildVacPv(id_num)
        pv_name = config['prefix'] + name
        led_config = VGC_DETAILS["led"]
        led_name = pv_name+led_config["text"]
        unit_name = pv_name+VGC_DETAILS["Pressure<br/>Readback"]+str(dev_gen)
        lay.addWidget(
            showUnitView(unit_name),
            alignment=Qt.AlignCenter)
        led = getVgcLed(self, led_name, id_num, led_config["sufix"])
        lay.addWidget(led, alignment=Qt.AlignCenter)

    def getGroupWidgets(self, config, item, cat, orient):
        pv_name = buildIdName(item, cat=="Valve")
        pv_name = config["prefix"] + pv_name
        if(cat == "Valve"):
            widget = buildLed(
                self, pv_name, config['sufix'], "on/off")
        elif(cat == "Pump"):
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            buildIPSInfo(
                pv_name, lay, orient)
        else:
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            self.buildVacInfo(config, item, lay)
        return widget

    def saveRelWid(self, widget, size, coord):
        rel_wid = RelativeWidget(
            parent=self.image_container,
            widget=widget,
            relative_pos=coord + size)
        self.relative_widgets.append(rel_wid)

    def saveWidToList(self, widget, cat):
        if cat == "Vacuum":
            self.vacList.append(widget)
        else:
            self.pumpList.append(widget)

    def showMainWidgets(self, cat="Vacuum"):
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

    def showVacList(self, config):
        wid, lay = getLayoutWidget()
        id = 1
        for item in self.vacList:
            pos = getVacPosition(id)
            lay.addWidget(item, pos[0], pos[1])   
            self.saveRelWid(
                wid, config['size'], config['coord'])
            id += 1

    def showPumpList(self, config):
        wid, lay = getLayoutWidget()
        pos = [0, 0]
        for item in self.pumpList:
            if pos[0]>=10 and pos[1]==0:
                pos[0] = 0
                pos[1] = 1
            lay.addWidget(item, pos[0], pos[1])   
            self.saveRelWid(
                wid, config['size'], config['coord'])
            pos[0] += 1

    def showLists(self, cat):
        config = PVS_CONFIG[cat]['list']
        if cat == "Vacuum":
            self.showVacList(config)
        else:      
            self.showPumpList(config)
    
    def showAllLegends(self):
        size = LEGEND['size'] 
        coord = [50, 85]
        for leg in ['CCG', 'PRG']:
            self.saveRelWid( 
                showLegend(self, leg), size, coord)
            coord[0] += 6

    def buildBasicGroup(self, cat, id_num, orient="V"):
        group = QGroupBoxButton(
            title=getGroupTitle(cat, id_num))
        wid, lay = getLayoutWidget(orient)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 2, 0, 0)
        group.setLayout(lay)
        group.clicked.connect(
            lambda: self.selWindow(cat, id_num))
        group.setObjectName("group")
        group.setStyleSheet("QGroupBox#group{background-color:"+COLORS['btn_bg']+"};")
        if orient == "H":
            lay.addWidget(
                self.setWindowBtn(cat, id_num),
                alignment=Qt.AlignLeft)
        return lay, group

    def setWindowBtn(self, cat, id_num):
        button = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        button.clicked.connect(
            lambda: self.selWindow(cat, id_num))
        button.setStyleSheet("margin: 0.1em;")
        return button

    def showButtons(self):
        size = [10, 8]
        coord = [35, 85]
        count = 0
        for title in ['Details', 'CCG Graphs']:
            btn = QPushButton(title)
            btn.clicked.connect(
                lambda state, title=title: self.selWindow(title))
            self.genBtn.append(btn)
            self.saveRelWid(
                self.genBtn[-1], 
                size, coord)
            coord[1] += 5
            count += 1

    def _setupui(self):
        """ . """
        lay = QGridLayout()
        self.setLayout(lay)

        lay.addWidget(self.imageViewer(), 0, 0)
        for wid_cat in PVS_CONFIG:
            self.showMainWidgets(wid_cat)
            if wid_cat != "Valve":
                self.showLists(wid_cat)

        self.showAllLegends()
        self.showButtons()
