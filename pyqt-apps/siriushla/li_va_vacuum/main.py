"""Main module of the Application Interface."""

import os as _os
import math as _math
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QGroupBox, QHBoxLayout, QPushButton
import qtawesome as _qta
from pydm.widgets.display_format import DisplayFormat
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, COLORS
from .widgets import LedLegend, QGroupBoxButton
from ..widgets import RelativeWidget, PyDMLedMultiChannel, \
    SiriusLabel, PyDMLed
from siriushla.as_di_bpms.base import GraphTime
from ..si_di_bbb.custom_widgets import MyScaleIndicator

class VacuumMain(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.setObjectName('LIApp')
        self.setWindowTitle('LI Vacuum')
        self.display_format = DisplayFormat
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "vacuum.png"))
        self.relative_widgets = []
        self.pumpList = []
        self.vacList = []
        self.graphs = []
        self._setupui()

    def showUnitView(self, pv_name, color="#000000"):
        widget = SiriusLabel(init_channel=pv_name)
        styled = "min-height:0.75em;max-height:0.75em;background-color:"+color+";min-width: 3em;"
        widget.setStyleSheet(styled)
        widget.showUnits = True
        widget._keep_unit = True
        widget.setAlignment(Qt.AlignCenter)
        if "RdPrs" in pv_name:
            widget.precisionFromPV = False
            widget.precision = 2
            widget.displayFormat = self.display_format.Exponential
        return widget

    def buildIdName(self, name, id_num, isValve):
        pv_id = ""
        if not isValve:
            if id_num < 10:
                pv_id = "0"
        pv_id += str(id_num)
        return name + pv_id

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
                lay.addWidget(
                    LedLegend(self,
                        item['color']),
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

    def buildLed(self, pv_name, sufix_list, comp):
        if comp == 'normal':
            led = PyDMLed(
                init_channel=pv_name+sufix_list)
            shape = 1
        else: 
            if comp == 'on/off':
                chan2vals = {
                    pv_name + sufix_list[0]: 0,
                    pv_name + sufix_list[1]: 1
                }
                shape = 4
            elif comp == 'equal':
                chan2vals = {
                    pv_name + sufix_list[0]: 0,
                    pv_name + sufix_list[1]: 0
                }
                shape = 3
            color_list = [
                COLORS["light_green"], COLORS["yellow"], COLORS["red"]]
            led = PyDMLedMultiChannel(
                self, chan2vals, color_list)
        led.shape = shape
        if shape != 1: shape-=2
        led.setStyleSheet("min-width:"+str(shape)+"em; max-width:"+str(shape)+"em;")
        return led

    def setWindowBtn(self):
        button = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        #Connect to window
        button.setStyleSheet("margin: 0.1em;")
        return button

    def getGroupTitle(self, cat, id_num):
        dev_number = id_num
        if cat == "Pump":
            name = "IPS"
        else:
            dev_number, dev_gen = self.buildIdsVac(id_num)
            if dev_gen == 3:
                name = "PRG"
            else:
                name = "CCG"
        return self.buildIdName(name, dev_number, False)

    def selWindow(self, cat, id):
        if cat == "Vacuum":
           dev_number, dev_gen = self.buildIdsVac(id)
           print(str(cat) + str(dev_number) + str(dev_gen)) 
        print(str(cat) + str(id))

    def buildBasicGroup(self, cat, id_num, orient="V"):
        group = QGroupBoxButton(
            title=self.getGroupTitle(cat, id_num))
        lay = self.setLayOrientation(orient)
        group.setLayout(lay)
        group.setObjectName("group")
        group.setStyleSheet("QGroupBox#group{background-color:"+COLORS['btn_bg']+"};")
        group.clicked.connect(lambda: self.selWindow(cat, id_num))
        if orient == "H":
            lay.addWidget(
                self.setWindowBtn(),
                alignment=Qt.AlignLeft)
        return lay, group

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

    def buildIPSInfo(self, pv_name, config, lay, orient):
        for info_type in ['voltage', 'current']:
            info = config[info_type]
            name = pv_name + info['text']
            if info_type == 'current' and orient == 'H':
                lay.addWidget(
                    self.getProgressBar(name),
                    alignment=Qt.AlignCenter)
            wid = self.showUnitView(
                name, info['color'])
            lay.addWidget(
                wid, alignment=Qt.AlignCenter)
        return lay

    def buildVacPv(self, config, id_num):
        dev_number, dev_gen = self.buildIdsVac(id_num)
        if dev_gen == 2:
            dev_number -= 5
        pv_name = self.buildIdName(
            config["prefix"], dev_number, False)
        return pv_name, dev_gen

    def buildVacInfo(self, config, id_num, lay, orient):
        name, dev_gen = self.buildVacPv(config, id_num)
        led_config = config["led"]
        led_name = name+led_config["text"]
        unit_name = name+config["text"]+str(dev_gen)
        sufix_list = led_config["sufix"]
        lay.addWidget(
            self.showUnitView(
                unit_name, config['color']),
            alignment=Qt.AlignCenter)
        if id_num % 3 != 0:
            comp = 'equal'
        else:
            comp = 'normal'
        led = self.buildLed(
            led_name, sufix_list[id_num % 3], comp)
        lay.addWidget(led, alignment=Qt.AlignCenter)
        return lay

    def getWidget(self, config, item, cat, orient):
        pv_name = self.buildIdName(
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
            self.buildVacInfo(
                config, item, lay, orient)
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
    
    def buildIdsVac(self, id_num):
        dev_number = _math.ceil(id_num / 3)
        dev_gen = id_num % 3
        if dev_gen == 2:
            dev_number += 5
        if not dev_gen:
            dev_gen = 3
        return dev_number, dev_gen

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
            pos[0], pos[1]  = self.buildIdsVac(id)
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
        for title in ['Details', 'CCG Graphs']:
            self.saveRelWid(
                QPushButton(title), 
                size, coord)
            coord[1] += 5


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
