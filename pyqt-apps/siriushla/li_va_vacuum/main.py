"""Main module of the Application Interface."""

import os as _os
from qtpy.QtCore import Qt, QEvent, QSize
from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QGroupBox, QHBoxLayout
from pydm.widgets.display_format import DisplayFormat
from qtpy.QtGui import QPixmap
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import LEGEND, PVS_CONFIG, COLORS
from .widgets import LedLegend
from ..widgets import RelativeWidget, PyDMLedMultiChannel, SiriusLabel

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

    def showUnitView(self, pv_name):
        widget = SiriusLabel(init_channel=pv_name)
        widget.showUnits = True
        return widget

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
            0, 0, 1, 2, Qt.AlignCenter)
        row = 1
        for item in LEGEND[legend]:
            column = 0
            if 'color' in item:
                leg_glay.addWidget(
                    LedLegend(self,
                        item['color']),
                    row, column, 1, 1, Qt.AlignCenter)
                column = 1

            leg_glay.addWidget(
                self.legendText(item['text']),
                row, column, 1, 1, Qt.AlignLeft)
            row += 1
        return leg_glay

    def imageViewer(self):
        """Build the image"""
        self.image_container.setPixmap(self.pixmap)
        self.image_container.installEventFilter(self)
        self.image_container.setScaledContents(True)
        self.image_container.setMinimumSize(1000, 500)
        return self.image_container

    def buildValveLed(self, pv_name, config):
        chan2vals = {
            pv_name + config["sufix"][0]: 1,
            pv_name + config["sufix"][1]: 0
        }
        color_list = [
            COLORS["yellow"], COLORS["light_green"], COLORS["gray"]]
        led = PyDMLedMultiChannel(
            self, chan2vals, color_list)
        return led

    def buildIdName(self, name, number, isValve):
        pv_id = ""
        if not isValve:
            if number < 10:
                pv_id = "0"
        pv_id += str(number)
        return name + pv_id

    def buildIPSInfo(self, pv_name, config, number, orientation="V"):
        group = QGroupBox()
        size = config["size"][orientation]
        if orientation == "V":
            lay_ips = QVBoxLayout()
            group.setMaximumSize(size[0]*12, size[1]*6)
        else:
            lay_ips = QHBoxLayout()
            group.setMaximumSize(8*8, 17*8)

        lay_ips.setContentsMargins(0, 0, 0, 0)
        lay_ips.setSpacing(0)
        group.setLayout(lay_ips)

        id_name = QLabel(
            "<strong>"+self.buildIdName("IPS", number, False)+"</strong>")
        lay_ips.addWidget(id_name,
            alignment=Qt.AlignCenter)
        for info_type in ['voltage', 'current']:
            wid = self.showUnitView(pv_name + config[info_type]['text'])
            lay_ips.addWidget(wid,
                alignment=Qt.AlignCenter)
            wid.setStyleSheet(
                "color: "+config[info_type]['color']+";"+
                "padding: 0.05em;"+
                "border: 0.2em solid"+config[info_type]['color']+";")
        #Add to IPS Widget List
        return group

    def showMainWidgets(self, category_name="Vacuum"):
        config = PVS_CONFIG[category_name]
        pv_range = config["iterations"]
        for item in range(pv_range[0], pv_range[1]+1):
            pv_name = self.buildIdName(
                config["prefix"], item, category_name=="Valve")
            if(category_name == "Valve"):
                widget = self.buildValveLed(pv_name, config)
                position = config["position"][item-1] + config["size"]
            elif(category_name == "Pump"):
                widget = self.buildIPSInfo(pv_name, config, item, "V")
                position = config["position"][item-1] + config["size"]["V"]
            else:
                widget = None
                position = config["position"][item-1][0] + config["size"]["H"]
            rel_wid = RelativeWidget(
                parent=self.image_container,
                widget=widget,
                relative_pos=position)
            self.relative_widgets.append(rel_wid)

    def _setupui(self):
        """ . """
        layG = QGridLayout()
        self.setLayout(layG)

        layG.addWidget(self.imageViewer(), 0, 0)
        for wid_cat in PVS_CONFIG:
            self.showMainWidgets(wid_cat)
