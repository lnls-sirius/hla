"""BL AP ImgProc."""

from datetime import datetime
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QGroupBox, QLabel, QSizePolicy, QTabWidget, \
    QPushButton, QScrollArea

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from ..widgets import SiriusEnumComboBox
from ..widgets.dialog import StatusDetailDialog

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from .. import util as _util
from ..util import get_appropriate_color
from ..widgets import SiriusLabel, SiriusLedState, \
    SiriusLineEdit, PyDMLogLabel, PyDMStateButton, \
    SiriusConnectionSignal, SiriusSpinbox, SiriusLedAlert

from .util import PVS_IMGPROCCTRL, PVS_IMGPROCOVERVIEW, PVS_DVF, \
    IMG_PVS, LOG_PV, COMBOBOX_PVS, LINEEDIT_PVS, STATEBUT_PVS, \
    LED_ALERT_PVS, LED_STATE_PVS, LED_DETAIL_PVS, INTLK_PVS
from .image import DVFImageView
from .blintlkctl import BLIntckCtrl


class BLImgProc(QWidget):
    """Image Processing Window."""

    def __init__(self, dvf, parent=None, prefix=_VACA_PREFIX):
        """."""
        super().__init__(parent=parent)
        self.setObjectName('SIApp')
        self.prefix = prefix + ('-' if prefix else '')
        self.dvf = dvf
        self.device = self.prefix + self.dvf
        self.blpps = BLIntckCtrl(self.device)
        self.setWindowTitle(self.device + ' Image Processing Window')
        self.setWindowIcon(
            qta.icon('mdi.camera-metering-center',
                     color=get_appropriate_color('SI')))
        self._lbl_timestamp = {}
        self.timestamp = {}
        self.img_view = None

        self.loading = QPushButton("")
        self.open_beamline_btn = None
        self.enable_gamma_btn = None
        self.gamma_enabled_conn = None
        self._setupUi()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bl_open_status)
        self.timer.start(1000)

    def add_prefixes(self, sufix):
        """."""
        return self.device + ":" + sufix

    def generate_pv_name(self, sufix):
        """."""
        if len(sufix) != 2:
            return self.add_prefixes(sufix)

        pv_list = []
        for sf in sufix:
            try:
                pvname = self.add_prefixes(sf)
                pv_list.append(pvname)
            except:
                pv_list.append(sf)
        return pv_list

    def format_datetime_lbl(self, value, pvname):
        """."""
        dtval = datetime.fromtimestamp(value)
        datetime_lbl = dtval.strftime("%d/%m/%Y, %H:%M:%S")
        datetime_lbl += '.{:03d}'.format(int(1e3*(value % 1)))
        self._lbl_timestamp[pvname].setText(datetime_lbl)

    def create_time_widget(self, pvname):
        """."""
        lbl_time = QLabel('0000-00-00 0:00:00.0', self)
        self._lbl_timestamp[pvname] = lbl_time
        self._lbl_timestamp[pvname].channel = pvname
        self.timestamp[pvname] = SiriusConnectionSignal(pvname)
        self.timestamp[pvname].new_value_signal[float].connect(
            lambda value: self.format_datetime_lbl(value, pvname))
        return self._lbl_timestamp[pvname]

    def select_widget(
            self, pv_name, widget_type='label', units=True, labels=None):
        """."""
        pvname = self.generate_pv_name(pv_name)
        if widget_type == 'label':
            wid = SiriusLabel(init_channel=pvname, keep_unit=True)
            wid.showUnits = units
            wid.setAlignment(Qt.AlignCenter)
            wid.setMaximumHeight(50)
        elif widget_type == 'setpoint_readback_combo':
            sprb_type = ['enumcombo', 'label', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_edit':
            sprb_type = ['edit', 'label', False]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_sbut':
            sprb_type = ['switch', 'led_state', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'setpoint_readback_spin':
            sprb_type = ['spin', 'label', True]
            wid = self.setpoint_readback_widget(pv_name, sprb_type)
        elif widget_type == 'led_state':
            wid = SiriusLedState(init_channel=pvname)
            wid.offColor = wid.Yellow
        elif widget_type == 'led_alert':
            wid = SiriusLedAlert(init_channel=pvname)
            wid.onColor = wid.Yellow
        elif widget_type == 'leddetail':
            led = SiriusLedAlert(init_channel=pvname[0])
            details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
            details.setObjectName('bt')
            details.setStyleSheet(
                '#bt{min-width:25px;max-width:25px;icon-size:20px;}')
            _util.connect_window(
                details, StatusDetailDialog, pvname=pvname[0], parent=self,
                labels=pvname[1], section="SI", title='Status Detailed')
            wid = QWidget()
            hlay = QHBoxLayout(wid)
            hlay.addWidget(led)
            hlay.addWidget(details)
        elif widget_type == 'log':
            wid = PyDMLogLabel(init_channel=pvname)
        elif widget_type == 'edit':
            wid = SiriusLineEdit(init_channel=pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'switch':
            wid = PyDMStateButton(init_channel=pvname)
        elif widget_type == 'enumcombo':
            wid = SiriusEnumComboBox(self, init_channel=pvname)
        elif widget_type == 'image':
            wid = DVFImageView(self.device, pvname)
        elif widget_type == 'time':
            wid = self.create_time_widget(pvname)
            wid.setAlignment(Qt.AlignCenter)
        elif widget_type == 'spin':
            wid = SiriusSpinbox(init_channel=pvname)
        elif widget_type == 'cmd':
            wid = PyDMPushButton(init_channel=pvname, pressValue=1)
            wid.setIcon(qta.icon('fa5s.sync'))
            wid.setObjectName('bt')
            wid.setStyleSheet(
                '#bt{min-width:25px;max-width:25px;icon-size:20px;}')
        else:
            wid = QLabel("Widget has not been implemented yet!")
        return wid

    def setpoint_readback_widget(self, pv_list, sprb_type):
        """."""
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

    def create_widget(self, title, pv_name):
        """."""
        if title in LED_ALERT_PVS:
            wid_type = 'led_alert'
        elif title in LED_STATE_PVS:
            wid_type = 'led_state'
        elif title in LED_DETAIL_PVS:
            wid_type = 'leddetail'
        elif 'Time' in pv_name and 'Proc' not in pv_name:
            wid_type = 'time'
        elif '-Cmd' in pv_name:
            wid_type = 'cmd'
        elif title in LOG_PV:
            wid_type = 'log'
        elif title in IMG_PVS:
            wid_type = 'image'
        elif len(pv_name) != 2:
            wid_type = 'label'
        elif title in COMBOBOX_PVS:
            wid_type = 'setpoint_readback_combo'
        elif title in LINEEDIT_PVS:
            wid_type = 'setpoint_readback_edit'
        elif title in STATEBUT_PVS:
            wid_type = 'setpoint_readback_sbut'
        else:
            wid_type = 'setpoint_readback_spin'

        hlay = QHBoxLayout()
        wid = self.select_widget(pv_name, wid_type)
        if wid_type not in ['log', 'image']:
            title_wid = QLabel(title + ': ')
            title_wid.setAlignment(Qt.AlignRight)
            hlay.addWidget(
                title_wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
            hlay.addWidget(wid, alignment=Qt.AlignLeft)
        else:
            hlay.addWidget(wid)

        return hlay

    def create_box_group(self, title, pv_info):
        """."""
        wid = QGroupBox(title) if title else QWidget()
        gbox = QGridLayout(wid)

        count = 0
        for title, pv in pv_info.items():
            if title in ['X', 'Y']:
                widget = self.create_box_group(title, pv)
                hpos = 0 if title == 'X' else 1
                gbox.addWidget(widget, count, hpos, 1, 1)
                if title == 'Y':
                    count += 1
            else:
                pv_lay = self.create_widget(title, pv)
                gbox.addLayout(pv_lay, count, 0, 1, 2)
                count += 1

        return wid

    def _setupTab(self, content, use_scroll=False):
        cont_wid = QWidget()
        cont_wid.setObjectName('wid')
        glay = QGridLayout()

        for title, pv_data in content.items():
            loc = pv_data[0]
            if len(pv_data[1:]) > 1:
                wid = QGroupBox(title, self)
                widlay = QHBoxLayout(wid)
                for data in pv_data[1:]:
                    col = self.create_box_group("", data)
                    widlay.addWidget(col)
            else:
                wid = self.create_box_group(title, pv_data[1])
            glay.addWidget(wid, *loc)

        glay.setColumnStretch(0, 3)
        glay.setColumnStretch(1, 1)
        glay.setColumnStretch(2, 1)
        cont_wid.setLayout(glay)

        if use_scroll:
            sc_area = QScrollArea()
            sc_area.setWidgetResizable(True)
            cont_wid.setStyleSheet('#wid{background-color: transparent;}')
            sc_area.setWidget(cont_wid)
            return sc_area
        return cont_wid

    def toggle_beamline_btns(self, value):
        """."""
        if value == 1:
            state = True
        else:
            state = False

        self.end_processing_cmd()
        self.open_beamline_btn.setEnabled(state)

    def end_processing_cmd(self):
        """."""
        self.enable_gamma_btn.setEnabled(True)
        self.open_beamline_btn.setEnabled(True)
        self.loading.setVisible(False)

    def start_processing_cmd(self):
        """."""
        self.enable_gamma_btn.setEnabled(False)
        self.open_beamline_btn.setEnabled(False)
        self.loading.setVisible(True)

    def intlk_cmd(self, cmd):
        """."""
        self.start_processing_cmd()
        if cmd == "enable_gamma":
            self.blpps.gamma_enable()
        elif cmd == "open_beamline":
            self.blpps.beamline_open()

    def _setup_gamma_control_widget(self):
        wid = QGroupBox()
        lay = QHBoxLayout()
        wid.setLayout(lay)
        wid.setTitle("Gamma")
        wid.setMaximumHeight(200)

        self.enable_gamma_btn = QPushButton("Enable")
        self.enable_gamma_btn.clicked.connect(
            lambda: self.intlk_cmd("enable_gamma"))
        lay.addWidget(self.enable_gamma_btn)

        pvname = INTLK_PVS["gamma"]
        widget = SiriusLedState(init_channel=pvname)
        self.gamma_enabled_conn = SiriusConnectionSignal(pvname)
        self.gamma_enabled_conn.new_value_signal[int].connect(
            self.toggle_beamline_btns)
        lay.addWidget(widget)

        return wid

    def update_bl_open_status(self):
        """."""
        # update open status led
        status_bl = self.blpps.beamline_opened
        old_val = self.pydm_led.value
        self.pydm_led.value_changed(status_bl)
        if old_val != status_bl:
            self.end_processing_cmd()

        # update log error label
        error_bl = self.blpps.blintlk.error_log
        self.pydm_lbl.setText(error_bl)

    def _setup_enable_beamline_widgets(self):
        wid = QGroupBox()
        lay = QHBoxLayout()
        wid.setLayout(lay)
        wid.setTitle("Open Beamline")
        wid.setMaximumHeight(200)

        self.open_beamline_btn = QPushButton("Open")
        self.open_beamline_btn.clicked.connect(
            lambda: self.intlk_cmd("open_beamline"))
        lay.addWidget(self.open_beamline_btn)

        self.pydm_led = SiriusLedState()
        self.pydm_led.stateColors = [
            self.pydm_led.DarkGreen,
            self.pydm_led.LightGreen, self.pydm_led.Gray]
        lay.addWidget(self.pydm_led)

        return wid

    def _setup_beamline_error_log(self):
        wid = QGroupBox()
        lay = QHBoxLayout()
        wid.setLayout(lay)
        wid.setTitle("Beamline Status")
        wid.setMaximumHeight(200)

        self.beamline_error_log = QLabel('Error log: ')
        lay.addWidget(self.beamline_error_log)

        self.pydm_lbl = QLabel(self.blpps.blintlk.error_log)
        lay.addWidget(self.pydm_lbl)

        return wid

    def _setup_beamline_controls_widgets(self):
        wid = QGroupBox()
        lay = QVBoxLayout()
        wid.setLayout(lay)

        self.loading.setIcon(qta.icon(
            'fa5s.spinner', animation=qta.Spin(self.loading)))
        self.loading.setVisible(False)
        self.loading.setFlat(True)
        lay.addWidget(self.loading)

        widget = self._setup_gamma_control_widget()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(widget)

        widget = self._setup_enable_beamline_widgets()
        lay.addWidget(widget)

        widget = self._setup_beamline_error_log()
        lay.addWidget(widget)

        return wid

    def _setupUi(self):
        main_lay = QVBoxLayout()
        tab = QTabWidget()
        tab.setObjectName('SITab')

        title = QLabel(
            '<h3>'+self.device+' Image Processing<h3>', self,
            alignment=Qt.AlignCenter)
        main_lay.addWidget(title)

        img_wid = self._setupTab(PVS_IMGPROCOVERVIEW)
        tab.addTab(img_wid, "View")
        imgproc_wid = self._setupTab(PVS_IMGPROCCTRL, use_scroll=True)
        tab.addTab(imgproc_wid, "Settings")
        dvf_wid = self._setupTab(PVS_DVF, use_scroll=True)
        tab.addTab(dvf_wid, "DVF")
        cax_wid = self._setup_beamline_controls_widgets()
        tab.addTab(cax_wid, "CAX")

        main_lay.addWidget(tab)
        self.setLayout(main_lay)
