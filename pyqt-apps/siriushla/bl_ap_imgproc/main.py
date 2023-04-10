from qtpy.QtWidgets import QSizePolicy
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QLabel
from siriushla.widgets import SiriusLabel, SiriusLedState, \
    SiriusLineEdit, PyDMLogLabel, PyDMStateButton
from pydm.widgets import PyDMImageView
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from .util import PVS, IMG_PVS, LED_PVS, LOG_PV, SPRB_LED_PV

class CaxImgProc(QWidget):
    """."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.beamline = 'CAX'
        self.hutch = 'B'
        self.basler = 'BASLER01'
        self._setupUi()

    def add_prefixes(self, sufix):
        return self.beamline+":"+self.hutch+":"+self.basler+":"+sufix

    def generate_pv_name(self, sufix):
        if len(sufix) != 2:
            return self.add_prefixes(sufix)

        pv_list = []
        for sf in sufix:
            pvname = self.add_prefixes(sf)
            pv_list.append(pvname)
        return pv_list

    def select_widget(self, pv_name, widget_type='label'):
        pvname = self.generate_pv_name(pv_name)
        if widget_type == 'label':
            wid = SiriusLabel(init_channel=pvname)
            wid.showUnits = True
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
        return wid

    def setpoint_readback_widget(self, pv_list, sprb_type):
        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)

        setpoint = self.select_widget(
            pv_list[0], sprb_type[0])
        hlay.addWidget(setpoint)

        readback = self.select_widget(
            pv_list[1], sprb_type[1])
        hlay.addWidget(readback)

        wid.setMaximumWidth(400)
        return wid

    def create_widget_w_title(self, title, pv_name):
        hlay = QHBoxLayout()

        title_wid = QLabel(title)
        hlay.addWidget(title_wid)

        if title in LED_PVS:
            wid_type = 'led'
        elif len(pv_name) != 2:
            wid_type = 'label'
        else:
            wid_type = 'setpoint_readback'

        wid = self.select_widget(pv_name, wid_type)
        hlay.addWidget(wid)

        return hlay

    def create_box_group(self, title, pv_info):
        wid = QGroupBox()
        vbox = QVBoxLayout()
        wid.setLayout(vbox)
        wid.setStyleSheet("QGroupBox{ border: 4px groove #777777 }")
        wid.setTitle(title)

        for title, pv in pv_info.items():
            special_wid = IMG_PVS+LOG_PV
            if title not in special_wid:
                pv_lay = self.create_widget_w_title(title, pv)
                vbox.addLayout(pv_lay)
            else:
                if title in LOG_PV:
                    pv_type = 'log'
                else:
                    pv_type = 'image'
                vbox.addWidget(self.select_widget(pv, pv_type))

        return wid

    def _setupUi(self):
        glay = QGridLayout()

        for title, pv_data in PVS.items():
            loc = pv_data[0]
            wid = self.create_box_group(title, pv_data[1])
            glay.addWidget(
                wid, loc[1], loc[0], loc[3], loc[2])

        self.setLayout(glay)
