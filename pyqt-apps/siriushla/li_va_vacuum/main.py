"""Main module of the Application Interface."""

import os as _os
import math as _math
from qtpy.QtCore import Qt, QEvent, QSize
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QGroupBox, QHBoxLayout, QPushButton
from pydm.widgets.display_format import DisplayFormat
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, COLORS
from .widgets import LedLegend
from ..widgets import RelativeWidget, PyDMLedMultiChannel, \
    SiriusLabel, PyDMLed

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
        self._setupui()

    def showUnitView(self, pv_name, color="#000000"):
        widget = SiriusLabel(init_channel=pv_name)
        widget.setStyleSheet(
            "color: "+color+";"+
            "padding: 0.05em;"+
            "border: 0.2em solid "+color+";")
        widget.showUnits = True
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
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        return lay

    def eventFilter(self, obj, event):
        """Signal the resize event to the relative Widgets"""
        if (event.type() == QEvent.Resize):
            for relative_item in self.relative_widgets:
                relative_item.relativeResize()
        return super().eventFilter(obj, event)

    def legendText(self, text):
        text = QLabel(text)
        text.setMaximumHeight(30)
        return text

    def showLegend(self, legend):
        """ Show one of the legends present in the LEGEND variable in util"""
        leg_glay = QGridLayout()
        leg_glay.addWidget(
            self.legendText('<b>'+legend+'</b>'),
            0, 0, 1, 2, alignment=Qt.AlignCenter)
        row = 1
        for item in LEGEND[legend]:
            column = 0
            if 'color' in item:
                leg_glay.addWidget(
                    LedLegend(self,
                        item['color']),
                    row, column, 1, 1,
                    alignment=Qt.AlignCenter)
                column = 1

            leg_glay.addWidget(
                self.legendText(item['text']),
                row, column, 1, 1,
                alignment=Qt.AlignLeft)
            row += 1
        return leg_glay

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(1000, 500)
        return self.image_container

    def buildLed(self, pv_name, sufix_list, comp):
        if comp == 'on/off':
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 0
            }
        elif comp == 'equal':
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 1
            }
        color_list = [
            COLORS["yellow"], COLORS["light_green"], COLORS["gray"]]
        led = PyDMLedMultiChannel(
            self, chan2vals, color_list)
        return led

    def setWindowBtn(self, cat, id_num):
        button = QPushButton(
            self.getBtnTitle(cat, id_num))
        #Connect to window
        button.setStyleSheet("font-weight: bold;")
        return button

    def getBtnTitle(self, cat, id_num):
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

    def buildBasicGroup(self, cat, id_num, orient="V"):
        group = QGroupBox()
        lay = self.setLayOrientation(orient)
        group.setLayout(lay)
        lay.addWidget(
            self.setWindowBtn(cat, id_num),
            alignment=Qt.AlignCenter)
        return lay, group

    def buildIPSInfo(self, pv_name, config, lay):
        for info_type in ['voltage', 'current']:
            info = config[info_type]
            name = pv_name + info['text']
            wid = self.showUnitView(
                name, info['color'])
            lay.addWidget(wid,
                alignment=Qt.AlignCenter)
        return lay

    def buildIdsVac(self, id_num):
        dev_number = _math.ceil(id_num / 3)
        dev_gen = id_num % 3
        if dev_gen == 2:
            dev_number += 5
        if not dev_gen:
            dev_gen = 3
        return dev_number, dev_gen

    def buildVacPv(self, config, id_num):
        dev_number, dev_gen = self.buildIdsVac(id_num)
        if dev_gen == 2:
            dev_number -= 5
        pv_name = self.buildIdName(
            config["prefix"], dev_number, False)
        return pv_name, dev_gen

    def buildVacInfo(self, config, id_num, lay):
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
            led = self.buildLed(
                led_name, sufix_list[id_num % 3], "equal")
        else:
            led = PyDMLed(
                init_channel=led_name+sufix_list[0])
        lay.addWidget(led, alignment=Qt.AlignCenter)
        return lay

    def getPosition(self, coord, size, orient):
        if isinstance(size, dict):
            return coord + size[orient]
        return coord + size

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
                pv_name, config, lay)
        else:
            lay, widget = self.buildBasicGroup(
                cat, item, orient)
            self.buildVacInfo(
                config, item, lay)
        return widget

    def saveWidget(self, widget, size, coord, orient, lay):
        if orient == 'H':
            lay.addWidget(widget, alignment=Qt.AlignCenter)
        else:
            rel_wid = RelativeWidget(
                parent=self.image_container,
                widget=widget,
                relative_pos=self.getPosition(
                    coord, size, orient))
            self.relative_widgets.append(rel_wid)
        return lay

    def showMainWidgets(self, cat="Vacuum"):
        lay = QVBoxLayout()
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
                lay = self.saveWidget(
                    widget, config["size"], coord,
                    orient, lay)
        return lay

    def _setupui(self):
        """ . """
        layG = QGridLayout()
        self.setLayout(layG)

        layG.addWidget(self.imageViewer(), 0, 0)
        row = 1
        for wid_cat in PVS_CONFIG:
            widget = self.showMainWidgets(wid_cat)
            layG.addLayout(widget, row, 0)
            row+=1
