"""Main module of the Application Interface."""

import os as _os
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QHBoxLayout, QPushButton
import qtawesome as _qta
from qtpy.QtGui import QPixmap
from siriushla.li_va_vacuum.chart import ChartWindow
from siriushla.li_va_vacuum.details import IpsDetailWindow
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, COLORS
from .functions import buildIdsVac, buildIdName, buildVacPv, getGroupTitle, showUnitView
from .widgets import LedLegend, QGroupBoxButton
from ..widgets import RelativeWidget, PyDMLedMultiChannel, PyDMLed
from ..si_di_bbb.custom_widgets import MyScaleIndicator

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

    def setLayOrientation(self, orient):
        if orient == "V":
            lay = QVBoxLayout()
        else:
            lay = QHBoxLayout()
        lay.setContentsMargins(0, 2, 0, 0)
        lay.setSpacing(0)
        return lay

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def showLegend(self, legend):
        """ Show one of the legends present in the LEGEND variable in util"""
        wid, lay = self.getGridWidget()
        lay.addWidget(
            QLabel('<b>'+legend+'</b>'),
            0, 0, 1, 2, alignment=Qt.AlignCenter)
        row = 1
        for item in LEGEND[legend]:
            column = 0
            if 'color' in item:
                shape = self.getShape(legend)
                lay.addWidget(
                    LedLegend(self, shape,
                        item['color'].name()),
                    row, column, 1, 1,
                    alignment=Qt.AlignCenter)
                column = 1

            lay.addWidget(
                QLabel(item['text']),
                row, column, 1, 1,
                alignment=Qt.AlignLeft)
            row += 1
        return wid

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(1580, 0)
        return self.image_container

    def getShape(self, name):
        if any(x in name for x in ["PRG", "normal"]):
            shape = 1
        elif any(x in name for x in ["CCG", "equal"]):
            shape = 3
        elif "on/off" in name:
            shape = 4
        else:
            shape = 2
        return shape

    def buildLed(self, pv_name, sufix_list, comp):
        if comp == 'normal':
            led = PyDMLed(
                init_channel=pv_name+sufix_list)
        else: 
            if comp == 'on/off':
                chan2vals = {
                    pv_name + sufix_list[0]: 0,
                    pv_name + sufix_list[1]: 1
                }
            elif comp == 'equal':
                chan2vals = {
                    pv_name + sufix_list[0]: 0,
                    pv_name + sufix_list[1]: 0
                }
            color_list = [
                COLORS["light_green"], COLORS["yellow"], COLORS["red"]]
            led = PyDMLedMultiChannel(
                self, chan2vals, color_list)
        shape = self.getShape(comp)
        led.shape = shape
        if shape != 1: shape-=2
        led.setStyleSheet("min-width:"+str(shape)+"em; max-width:"+str(shape)+"em;")
        return led

    def setWindowBtn(self, cat, id_num):
        button = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        button.clicked.connect(
            lambda: self.selWindow(cat, id_num))
        button.setStyleSheet("margin: 0.1em;")
        return button
    
    def buildBasicGroup(self, cat, id_num, orient="V"):
        group = QGroupBoxButton(
            title=getGroupTitle(cat, id_num))
        lay = self.setLayOrientation(orient)
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

    def selWindow(self, cat, id=0):
        if cat == "CCG Graphs":
            self.window = ChartWindow()
        elif cat == "Pump":
            self.window = IpsDetailWindow(id_ips=id)
        # if cat == "Vacuum":
        #     window = ChartWindow()
        #     dev_number, dev_gen = buildIdsVac(id)
        #     print(str(cat) + str(dev_number) + str(dev_gen)) 
        # print(str(cat) + str(id))
        else:
            self.window = ChartWindow()
        self.window.show()

    def getProgressBar(self, pv_name):
        bar = MyScaleIndicator(
            init_channel=pv_name)
        bar.limitsFromChannel = False
        bar.showLimits = False
        bar.showValue = False
        bar.barIndicator = True
        bar.userLowerLimit = 0
        bar.userUpperLimit = 200
        bar.indicatorColor = COLORS['purple']
        bar.setStyleSheet('min-height:1em; min-width:5em;')
        return bar

    def buildVacInfo(self, config, id_num, lay):
        name, dev_gen = buildVacPv(config, id_num)
        led_config = config["led"]
        led_name = name+led_config["text"]
        unit_name = name+config["text"]+str(dev_gen)
        sufix_list = led_config["sufix"]
        lay.addWidget(
            showUnitView(
                unit_name, config['color']),
            alignment=Qt.AlignCenter)
        if id_num % 3 != 0:
            comp = 'equal'
        else:
            comp = 'normal'
        led = self.buildLed(
            led_name, sufix_list[id_num % 3], comp)
        lay.addWidget(led, alignment=Qt.AlignCenter)

    def buildIPSInfo(self, pv_name, config, lay, orient):
        for info_type in ['voltage', 'current']:
            info = config[info_type]
            name = pv_name + info['text']
            if info_type == 'current' and orient == 'H':
                lay.addWidget(
                    self.getProgressBar(name),
                    alignment=Qt.AlignCenter)
            wid = showUnitView(
                name, info['color'])
            lay.addWidget(
                wid, alignment=Qt.AlignCenter)
        return lay

    def getWidget(self, config, item, cat, orient):
        pv_name = buildIdName(
                config["prefix"], item, cat=="Valve")
        if(cat == "Valve"):
            widget = self.buildLed(
                pv_name, config['sufix'], "on/off")
        elif(cat == "Pump"):
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            self.buildIPSInfo(
                pv_name, config, lay, orient)
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
                widget = self.getWidget(
                    config, item, cat, orient)
                if orient == 'H':
                    self.saveWidToList(widget, cat)
                else:
                    self.saveRelWid(
                        widget, config["size"], coord)

    def getGridWidget(self):
        wid = QWidget()
        lay = QGridLayout()
        wid.setLayout(lay)
        return wid, lay

    def showVacList(self, config):
        wid, lay = self.getGridWidget()
        pos = [0, 0]
        id = 1
        for item in self.vacList:
            pos[0], pos[1]  = buildIdsVac(id)
            if pos[1] == 2:
                pos[1] = 1
            elif pos[1] == 3:
                pos[1] = 0
            lay.addWidget(item, pos[0], pos[1])   
            self.saveRelWid(
                wid, config['size'], config['coord'])
            id += 1

    def showPumpList(self, config):
        wid, lay = self.getGridWidget()
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
                self.showLegend(leg), size, coord)
            coord[0] += 6

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


    # def getGraph(self):
    #     if len(self.graphs) == 0:
    #         self.graphs[0] = GraphTime()

    # def createGraph(self, graph_data):
    #     '''Build a graph widget'''

    #     graph_plot.graph.title = graph_data.get("title")
    #     graph_plot.setLabel(
    #         'left',
    #         text=graph_data.get("labelY"),
    #         units=graph_data.get("unitY"))
    #     graph_plot.setLabel(
    #         'bottom',
    #         text=graph_data.get("labelX"),
    #         units=graph_data.get("unitX"))

    #     for channel in graph_data.get("channels"):

    #         channel_data = graph_data.get("channels").get(channel)
    #         graph_plot.addChannel(
    #             y_channel=self.prefix + self.device_name + ':' + channel_data.get('path'),
    #             name=channel_data.get('name'),
    #             color=channel_data.get('color'),
    #             lineWidth=1)

    #     graph_plot.setMinimumWidth(600)
    #     graph_plot.setMinimumHeight(250)

    #     return graph_plot

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
