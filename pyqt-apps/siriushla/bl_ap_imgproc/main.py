from datetime import datetime
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QLabel
from siriushla.widgets import SiriusLabel, SiriusLedState, \
    SiriusLineEdit, PyDMLogLabel, PyDMStateButton, SiriusConnectionSignal
from pydm.widgets import PyDMImageView
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import PVS, IMG_PVS, LED_PVS, LOG_PV

class CaxImgProc(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.setObjectName('SIApp')
        self.prefix = prefix + ('-' if prefix else '')
        self.beamline = 'CAX'
        self.hutch = 'A'
        self.basler = 'BASLER01'
        self._lbl_timestamp = {}
        self.timestamp = {}
        self._setupUi()

    def add_prefixes(self, sufix):
        return self.prefix + self.beamline + ":" + \
            self.hutch + ":" + self.basler + ":" + sufix

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
        datetime_lbl = dtval.strftime("%m/%d/%Y, %H:%M:%S")
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
        elif widget_type == 'setpoint_readback':
            if 'Sel' in pv_name[0]:
                sprb_type = ['switch', 'led']
            else:
                sprb_type = ['edit', 'label']
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'led':
            wid = SiriusLedState(init_channel=pvname)
        elif widget_type == 'log':
            wid = PyDMLogLabel(init_channel=pvname)
        elif widget_type == 'edit':
            wid = SiriusLineEdit(init_channel=pvname)
        elif widget_type == 'switch':
            wid = PyDMStateButton(init_channel=pvname)
        elif widget_type == 'image':
            wid = PyDMImageView(image_channel=pvname[0])
        elif widget_type == 'time':
            wid = self.create_time_widget(pvname)
        else:
            wid = QLabel("Widget has not been implemented yet!")
        return wid

    def setpoint_readback_widget(self, pv_list, sprb_type):
        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)

        for x in range(0, 2):
            widget = self.select_widget(
                pv_list[x], sprb_type[x], units=False)
            widget.setMaximumWidth(200)
            hlay.addWidget(widget)

        wid.setMaximumWidth(400)
        return wid

    def create_widget_w_title(self, title, pv_name):
        hlay = QHBoxLayout()

        title_wid = QLabel(title)
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
        wid = QGroupBox()
        vbox = QVBoxLayout()
        wid.setLayout(vbox)
        wid.setStyleSheet(
            "QGroupBox{ border: 4px groove #777777 }")
        wid.setTitle(title)

        for title, pv in pv_info.items():
            special_list = IMG_PVS+LOG_PV
            if title not in special_list:
                pv_lay = self.create_widget_w_title(title, pv)
                vbox.addLayout(pv_lay)
            else:
                spec_wid = self.get_special_wid(pv, title)
                vbox.addWidget(spec_wid)

        return wid

    def _setupUi(self):
        glay = QGridLayout()

        for title, pv_data in PVS.items():
            loc = pv_data[0]
            wid = self.create_box_group(title, pv_data[1])
            glay.addWidget(
                wid, loc[1], loc[0], loc[3], loc[2])

        self.setLayout(glay)
