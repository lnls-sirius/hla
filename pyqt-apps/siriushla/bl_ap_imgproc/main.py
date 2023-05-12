from datetime import datetime

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QLabel, QSizePolicy

import qtawesome as qta

from pydm.widgets import PyDMImageView

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from ..util import get_appropriate_color
from ..widgets import SiriusLabel, SiriusLedState, \
    SiriusLineEdit, PyDMLogLabel, PyDMStateButton, \
    SiriusConnectionSignal, SiriusSpinbox

from .util import PVS, IMG_PVS, LED_PVS, LOG_PV


class BLImgProc(QWidget):
    """Image Processing Window."""

    def __init__(self, beamline, hutch, cam, parent=None, prefix=_VACA_PREFIX):
        super().__init__(parent=parent)
        self.setObjectName('SIApp')
        self.prefix = prefix + ('-' if prefix else '')
        self.beamline = beamline
        self.hutch = hutch
        self.cam = cam
        self.device = self.prefix + self.beamline + ":" + \
            self.hutch + ":" + self.cam
        self.setWindowTitle(self.device + ' Image Processing Window')
        self.setWindowIcon(
            qta.icon('mdi.camera-metering-center',
                     color=get_appropriate_color('SI')))
        self._lbl_timestamp = {}
        self.timestamp = {}
        self._setupUi()

    def add_prefixes(self, sufix):
        return self.device + ":" + sufix

    def generate_pv_name(self, sufix):
        if len(sufix) != 2:
            return self.add_prefixes(sufix)

        pv_list = []
        for sf in sufix:
            pvname = self.add_prefixes(sf)
            pv_list.append(pvname)
        return pv_list

    def format_datetime_lbl(self, value, pvname):
        dtval = datetime.fromtimestamp(value)
        datetime_lbl = dtval.strftime("%d/%m/%Y, %H:%M:%S")
        self._lbl_timestamp[pvname].setText(datetime_lbl)

    def create_time_widget(self, pvname):
        lbl_time = QLabel('0000-00-00 0:00:00', self)
        self._lbl_timestamp[pvname] = lbl_time
        self._lbl_timestamp[pvname].channel = pvname
        self.timestamp[pvname] = SiriusConnectionSignal(pvname)
        self.timestamp[pvname].new_value_signal[float].connect(
            lambda value: self.format_datetime_lbl(value, pvname))
        return self._lbl_timestamp[pvname]

    def select_widget(self, pv_name, widget_type='label', units=True):
        pvname = self.generate_pv_name(pv_name)
        if widget_type == 'label':
            wid = SiriusLabel(init_channel=pvname)
            wid.showUnits = units
            wid.setAlignment(Qt.AlignCenter)
            wid.setMaximumHeight(50)
        elif widget_type == 'setpoint_readback':
            if 'Sel' in pv_name[0]:
                sprb_type = ['switch', 'led', True]
            else:
                isSpin = 'FWHM' in pv_name[0] or 'Intensity' in pv_name[0]
                setwid = 'edit'
                if isSpin:
                    setwid = 'spin'
                sprb_type = [setwid, 'label', False]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'led':
            wid = SiriusLedState(init_channel=pvname)
        elif widget_type == 'log':
            wid = PyDMLogLabel(init_channel=pvname)
        elif widget_type == 'edit':
            wid = SiriusLineEdit(init_channel=pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'switch':
            wid = PyDMStateButton(init_channel=pvname)
        elif widget_type == 'image':
            wid = PyDMImageView(
                image_channel=pvname[0],
                width_channel=pvname[1])
        elif widget_type == 'time':
            wid = self.create_time_widget(pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'spin':
            wid = SiriusSpinbox(init_channel=pvname)
        else:
            wid = QLabel("Widget has not been implemented yet!")
        return wid

    def setpoint_readback_widget(self, pv_list, sprb_type):
        wid = QWidget()
        wid.setContentsMargins(0, 0, 0, 0)
        if sprb_type[2]:
            lay = QHBoxLayout()
        else:
            lay = QVBoxLayout()
        wid.setLayout(lay)

        for x in range(0, 2):
            widget = self.select_widget(
                pv_list[x], sprb_type[x], units=False)
            widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            lay.addWidget(widget)
        return wid

    def create_widget_w_title(self, title, pv_name):
        hlay = QHBoxLayout()

        title_wid = QLabel(title)
        title_wid.setAlignment(Qt.AlignCenter)
        hlay.addWidget(title_wid)

        if title in LED_PVS:
            wid_type = 'led'
        elif "Time" in pv_name:
            wid_type = 'time'
        elif len(pv_name) != 2:
            wid_type = 'label'
        else:
            wid_type = 'setpoint_readback'

        wid = self.select_widget(pv_name, wid_type)
        hlay.addWidget(wid)
        return hlay

    def get_special_wid(self, pvname, title):
        if title in LOG_PV:
            pv_type = 'log'
        else:
            pv_type = 'image'
        return self.select_widget(pvname, pv_type)

    def create_box_group(self, title, pv_info):
        wid = QGroupBox(title)
        gbox = QGridLayout(wid)

        count = 0
        for title, pv in pv_info.items():
            special_list = IMG_PVS+LOG_PV
            if title in ['X', 'Y']:
                widget = self.create_box_group(title, pv)
                hpos = 0 if title == 'X' else 1
                gbox.addWidget(widget, count, hpos, 1, 1)
                if title == 'Y':
                    count += 1
            elif title not in special_list:
                pv_lay = self.create_widget_w_title(title, pv)
                gbox.addLayout(pv_lay, count, 0, 1, 2)
                count += 1
            else:
                spec_wid = self.get_special_wid(pv, title)
                gbox.addWidget(spec_wid, count, 0, 1, 2)
                if title in LOG_PV:
                    wid.setMaximumHeight(175)
                count += 1

        return wid

    def _setupUi(self):
        glay = QGridLayout()

        title = QLabel(
            '<h3>'+self.device+' Image Processing<h3>', self,
            alignment=Qt.AlignCenter)
        glay.addWidget(title, 0, 0, 1, 3)

        for title, pv_data in PVS.items():
            loc = pv_data[0]
            wid = self.create_box_group(title, pv_data[1])
            glay.addWidget(wid, *loc)

        self.setLayout(glay)
