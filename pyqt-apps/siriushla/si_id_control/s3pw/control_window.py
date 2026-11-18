"""S3PW Control Module."""

import qtawesome as qta

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QFrame, QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout, QSpacerItem

from pydm.widgets import PyDMPushButton

from siriushla.util import connect_newprocess, connect_window
from siriushla.widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox, \
    PyDMStateButton, SiriusTimePlot

from ..base import IDCommonControlWindow, IDCommonSummaryBase, \
    IDCommonSummaryHeader, IDCommonSummaryWidget

from .interlocks_window import S3PWInterlocks
from .compressor_window import S3PWCompressors
from .heaters_window import S3PWHeaters
from .quench_window import S3PWQuench
from .ramp_window import S3PWRamp
from .vacuum_window import S3PWVacuum
from .utils import MAIN_CONTROL_PVS, SCANS_PVS


class S3PWControlWindow(IDCommonControlWindow):
    """S3PW Control Window."""
    
    def _setupUi(self):
        cwid = QWidget()
        self.setCentralWidget(cwid)
        lay = QVBoxLayout(cwid)

        label_title = QLabel(
            '<h3>'+self._device+' Control - '+self._beamline+'</h3 >', self,
            alignment=Qt.AlignCenter)
        label_title.setStyleSheet('max-height:1.29em;')

        lay.addWidget(label_title, Qt.AlignCenter)
        lay.addWidget(self._s3pwContent())

    def _s3pwContent(self):
        frame = QFrame()
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(0,0,0,0)

        lay.addWidget(self._headerFrame())
        lay.addWidget(self._contentFrame())
        lay.addWidget(self._graphFrame())

        return frame

    def _graphFrame(self):
        frame = QFrame()
        lay = QHBoxLayout(frame)

        lay.addWidget(self._temperatureGroup())

        return frame

    def _temperatureGroup(self):
        group = QGroupBox('Temperature')
        lay = QGridLayout(group)
        lay.setContentsMargins(12, 12, 12, 12)

        self.timeplot = SiriusTimePlot(parent=self, background='w')
        timespan = 60*60*6
        colors = ['blue', 'red', 'green', 'magenta']
        self.timeplot.timeSpan = timespan  # [s]
        self.timeplot.bufferSize = 2*timespan  # [2 samples/s]
        self.timeplot.autoRangeY = True
        self.timeplot.showXGrid = True
        self.timeplot.showYGrid = True
        self.timeplot.setLabel('left', text='Charge', units='C', color='gray')
        self.timeplot.setObjectName('timeplot')
        self.timeplot.setStyleSheet(
            '#timeplot{min-width:28em; min-height: 18em;}')

        lay.addWidget(self.timeplot, 0, 0, 1, 3)

        return group

    def _contentFrame(self):
        frame = QFrame()
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(0,0,0,0)

        right_frame = QFrame()
        right_lay = QVBoxLayout(right_frame)

        right_lay.addWidget(self._powerGroup())

        left_frame = QFrame()
        left_lay = QHBoxLayout(left_frame)

        left_lay.addWidget(self._heaterGroup())
        left_lay.addWidget(self.vacuumGroup())
        left_lay.addWidget(self._compressorGroup())

        lay.addWidget(left_frame)
        lay.addWidget(right_frame)

        return frame

    def vacuumGroup(self):
        statusbox = QGroupBox("Vacuum")
        lay = QGridLayout(statusbox)

        alarm_labels = [
            'Error',
            'Power Off',
            'Software limit disabled',
            'Hardware limit disabled',
            'Kill switches enabled',
            'Emergency stop button',
            'One or more SW limit reached',
            'One or more HW limit reached',
            'One or more kill SW reached',
        ]

        self._createStsDetail('Vacuum Window', 'VacIntlk-Mon', 
                    lay, 0, S3PWVacuum)

        return statusbox

    def _compressorGroup(self):
        group = QGroupBox("Compressor")
        lay = QGridLayout(group)
        lay.setContentsMargins(12,12,12,12)

        self._createStsDetail('Compressors Window', 'CompIntlk-Mon', 
                    lay, 0, S3PWCompressors)

        lbl = QLabel("Start Group", alignment=Qt.AlignRight | Qt.AlignHCenter)
        led = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="AllCompEnbl-Sel")
        )
        lay.addWidget(lbl, 1, 0)
        lay.addWidget(led, 1, 1, 1, 2)

        lbl = QLabel("Compressor 1", alignment=Qt.AlignHCenter)
        led = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="Comp1Enbl-Sts")
        )
        lay.addWidget(lbl, 2, 0)
        lay.addWidget(led, 2, 1, 1, 2)

        lbl = QLabel("Compressor 2", alignment=Qt.AlignHCenter)
        led = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="Comp2Enbl-Sts")
        )
        lay.addWidget(lbl, 3, 0)
        lay.addWidget(led, 3, 1, 1, 2)

        lbl = QLabel("Compressor 3", alignment=Qt.AlignHCenter)
        led = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="Comp3Enbl-Sts")
        )
        lay.addWidget(lbl, 4, 0)
        lay.addWidget(led, 4, 1, 1, 2)

        lbl = QLabel("Compressor 4", alignment=Qt.AlignHCenter)
        led = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="Comp4Enbl-Sts")
        )
        lay.addWidget(lbl, 5, 0)
        lay.addWidget(led, 5, 1, 1, 2)

        return group

    def _powerGroup(self):
        group = QGroupBox('Power Supplies')
        group.setMaximumHeight(260)
        lay = QVBoxLayout(group)

        status_frame = QFrame()
        status_lay = QGridLayout(status_frame)

        self._createStsDetail('Power Supplies Window', 'AllPSEnblIntlk-Mon', 
                    status_lay, 0, S3PWRamp)

        top_frame = QFrame()
        top_lay = QHBoxLayout(top_frame)
        
        comm_frame = QFrame()
        comm_frame.setMaximumHeight(60)
        comm_lay = QHBoxLayout(comm_frame)

        comm_lbl = QLabel("PS2 Communication")
        comm_sts = SiriusLedState(self)
        comm_lay.addWidget(comm_sts, alignment=Qt.AlignRight | Qt.AlignVCenter)
        comm_lay.addWidget(comm_lbl, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        
        top_lay.addWidget(status_frame)
        top_lay.addWidget(comm_frame)

        gframe = QFrame()
        glay = QGridLayout(gframe)
        glay.addWidget(QLabel('<h4>Current</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        glay.addWidget(QLabel('<h4>Current Ramp</h4>', self, alignment=Qt.AlignCenter), 0, 2)
        glay.addWidget(QLabel('<h4>Interlock</h4>', self, alignment=Qt.AlignCenter), 0, 3)

        row = 1
        for title, pv_info in MAIN_CONTROL_PVS.items():
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            glay.addWidget(label, row, 0)

            if isinstance(pv_info, dict):
                if "Cmd" in pv_info:
                    self._createCmdBtns(pv_info, glay, row)
                elif "StateMon" in pv_info:
                    self._createLedState(pv_info, glay, row)
                else:
                    self._createParam(pv_info, glay, row)
            else:
                raise NotImplementedError
            row += 1

        lay.addWidget(top_frame)
        lay.addWidget(gframe)

        return group

    def _heaterGroup(self):
        group = QGroupBox('Heaters')
        # group.setMaximumHeight(200)
        lay = QVBoxLayout(group)

        hframe = QFrame()
        hlay = QHBoxLayout(hframe)

        rframe = QFrame()
        rlay = QHBoxLayout(rframe)

        lb_glob = QLabel("Heaters Control", alignment=Qt.AlignCenter)
        bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="WarmUpEnbl-Sel")
        )
        led_idffglob = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="WarmUpEnbl-Sts")
        )
        rlay.addWidget(lb_glob,)
        rlay.addWidget(bt_idffglob)
        rlay.addWidget(led_idffglob)
        hlay.addWidget(rframe)

        lframe = QFrame()
        llay = QHBoxLayout(lframe)

        lb_glob = QLabel("Demag", alignment=Qt.AlignCenter)
        bt_idffglob = PyDMStateButton(
            self, init_channel=self.dev_pref.substitute(propty="DemagEnbl-Sel")
        )
        led_idffglob = SiriusLedState(
            self, init_channel=self.dev_pref.substitute(propty="DemagEnbl-Sts")
        )
        llay.addWidget(lb_glob)
        llay.addWidget(bt_idffglob)
        llay.addWidget(led_idffglob)
        hlay.addWidget(lframe)

        gframe = QFrame()
        hist_lay = QGridLayout(gframe)

        self._createStsDetail('Heaters Window', 'WarmUpInit-Mon', 
                    hist_lay, 0, S3PWHeaters)
        hist_lay.setVerticalSpacing(20)
        hist_lay.addWidget(QLabel('<h4>Cold Bus</h4>', self, alignment=Qt.AlignCenter), 1, 1)
        hist_lay.addWidget(QLabel('<h4>Bottom Yoke</h4>', self, alignment=Qt.AlignCenter), 1, 2)
        hist_lay.addWidget(QLabel('<h4>Base Frame</h4>', self, alignment=Qt.AlignCenter), 1, 3)

        hist_lbl = QLabel('Histerese', self, 
                          alignment=Qt.AlignRight | Qt.AlignVCenter)
        hist_lay.addWidget(hist_lbl, 2, 0)

        self._createReadback('ColdBusHist-Mon', hist_lay, 2, 1)
        self._createReadback('BottomYoke-Mon', hist_lay, 2, 2)
        self._createReadback('BaseFrameHist-Mon', hist_lay, 2, 3)

        lay.addWidget(gframe)
        lay.addWidget(hframe)

        return group

    def _headerFrame(self):
        frame = QFrame()
        lay = QHBoxLayout(frame)

        lay.addWidget(self._quenchGroup())
        lay.addWidget(self._interlockGroup())

        return frame

    def _quenchGroup(self):
        group = QGroupBox('Quench')
        lay = QGridLayout(group)
        group.setMaximumWidth(200)

        self._createStsDetail('Quench Window', 'QDSIntlk-Mon', 
                    lay, 0, S3PWQuench)

        return group

    def _interlockGroup(self):
        group = QGroupBox('Interlock')
        hlay = QHBoxLayout(group)
        hlay.setAlignment(Qt.AlignVCenter)
        
        emergency_btn = PyDMPushButton(self, label='Emergency')
        emergency_btn.channel = self.dev_pref.substitute(propty='RemoteEStop-Cmd')
        emergency_btn.pressValue = 1
        
        remote_reset_btn = PyDMPushButton(self, label='Remote Reset')
        remote_reset_btn.channel = self.dev_pref.substitute(propty='RemoteReset-Cmd')
        remote_reset_btn.pressValue = 1

        status_frame = QFrame()
        glay = QGridLayout(status_frame)

        self._createStsDetail('Interlocks Window', 'GlobIntlk-Mon', 
                glay, 0, S3PWInterlocks)

        hlay.addWidget(emergency_btn)
        hlay.addWidget(remote_reset_btn)
        hlay.addWidget(status_frame)

        return group

    def _createStatusComponents(self, pvname, label):
        lbl = QLabel(
            f'{label}', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led = SiriusLedAlert(self, pvname)
        # led.setMaximumWidth(40)
        btn = QPushButton('', self)
        btn.setIcon(qta.icon('fa.external-link-square'))
        btn.setIconSize(QSize(22,22))

        return lbl, led, btn

    def _createCmdBtns(self, pv_info, lay, row):
        btn = PyDMPushButton(self, label='')
        btn.channel = self.dev_pref.substitute(propty=pv_info["Cmd"])
        btn.pressValue = 1
        btn.setIconSize(QSize(20, 20))
        btn.setMaximumWidth(25)
        btn.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        lay.addWidget(btn, row, 1, 1, 4)

    def _createLedState(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["StateMon"])
        led = SiriusLedState(self, init_channel=pvname)
        lay.addWidget(led, row, 1, alignment=Qt.AlignLeft)

    def _createParam(self, pv_info, lay, row):
        if "SP" in pv_info:
            pvname = self.dev_pref.substitute(propty=pv_info["SP"])
            widtype = SiriusEnumComboBox if pvname.endswith('Sel') \
                else SiriusLineEdit
            cb = widtype(self, init_channel=pvname)
            lay.addWidget(cb, row, 1, 1, 1)

        if "RB" in pv_info:
            self._createReadback(pv_info["RB"], lay, row, 2)

        if "Btn" in pv_info:
            pvname = self.dev_pref.substitute(propty=pv_info["Btn"])
            btn = PyDMPushButton(self, label=pv_info.get("Lbl", ""))
            icon = pv_info.get("icon", "")
            if icon:
                btn.setIcon(qta.icon(icon))
                btn.setIconSize(QSize(24, 24))
            btn.channel = pvname
            btn.pressValue = 1
            btn.setMaximumWidth(300)
            btn.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            lay.addWidget(btn, row, 3, 1, 1)

    def _createReadback(self, pv, lay, row, col):
        pvname = self.dev_pref.substitute(propty=pv)
        lbl = SiriusLabel(self, init_channel=pvname, keep_unit=True)
        lbl.showUnits = True
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl, row, col, 1, 1)

    def _createStsDetail(self, title, pv, lay, row, window):
        pvname = self.dev_pref.substitute(propty=pv)
        lbl, led, btn = self._createStatusComponents(pvname, "Status")
        lay.addWidget(lbl, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(led, row, 1, alignment=Qt.AlignVCenter)
        lay.addWidget(btn, row, 2, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        connect_window(
            btn, window, parent=self, prefix=self._prefix, 
            device=self._device, title=f'{self.dev_pref} {title}',
        )


class S3PWSummaryBase(IDCommonSummaryBase):
    """S3PW Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Alarms', 4),
        ('PSCenCoil', 6),
        ('PSLatCoil', 6),
    )

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.setObjectName('IDApp')
        model_headers = list()
        for title, width in self.MODEL_WIDTHS:
            model_headers.append((title, width))
        self.prop2width = (
            ('Beamline', 9),
            ('Device', 9),
        ) + tuple(model_headers) + (
            ('Moving', 4),
        )


class S3PWSummaryHeader(IDCommonSummaryHeader, S3PWSummaryBase):
    """S3PW Summary Header."""


class S3PWSummaryWidget(IDCommonSummaryWidget, S3PWSummaryBase):
    """S3PW Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if prop == 'Alarms':
            led = SiriusLedAlert(
                self, self.dev_pref.substitute(propty='GlobIntlk-Mon'))
            wids.append(led)
        elif prop == 'PSCenCoil':
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='PSCenCoilCurrent-Mon'))
            wids.append(lbl)
        elif prop == 'PSLatCoil':
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='PSLatCoilCurrent-Mon'))
            wids.append(lbl)
        return wids, orientation
