"""VLightCam Widget."""

from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QFormLayout, QSizePolicy as QSzPlcy, QPushButton
from qtpy.QtCore import Qt
from pydm.widgets import PyDMPushButton
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from siriushla import util
from siriushla.common.cam_basler import SiriusImageView, create_propty_layout,\
    BaslerCamSettings
from siriushla.widgets.windows import create_window_from_widget


def conv_sec_2_device(sec):
    if sec == 'BO':
        return 'BO-50U:DI-VLightCam'
    elif sec == 'SI':
        return 'SI-01C2FE:DI-VLightCam'
    elif sec == 'IT':
        return 'IT-EGH:DI-Cam'
    else:
        raise ValueError('device not defined for section {}'.format(sec))


class VLightCamView(QWidget):
    """VLight Cam Viewer."""

    def __init__(self, parent=None, prefix=VACA_PREFIX, section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section.upper()
        self.device = _PVName(conv_sec_2_device(self.section))
        self.cam_prefix = self.device.substitute(prefix=prefix)
        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.device + ' View')
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h2>'+self.device+' View</h2>', self,
                       alignment=Qt.AlignCenter)

        self.cam_viewer = SiriusImageView(
            parent=self,
            image_channel=self.cam_prefix.substitute(propty='Data-Mon'),
            width_channel=self.cam_prefix.substitute(propty='AOIWidth-RB'),
            offsetx_channel=self.cam_prefix.substitute(propty='AOIOffsetX-RB'),
            offsety_channel=self.cam_prefix.substitute(propty='AOIOffsetY-RB'),
            maxwidth_channel=self.cam_prefix.substitute(
                propty='SensorWidth-Cte'),
            maxheight_channel=self.cam_prefix.substitute(
                propty='SensorHeight-Cte'))
        self.cam_viewer.setObjectName('camview')
        self.cam_viewer.setStyleSheet("""
            #camview{min-width:42em; min-height:32em;}""")

        self.settings = QGroupBox('Settings', self)
        self.settings.setLayout(self._setupSettingsLayout())

        lay = QVBoxLayout(self)
        lay.addWidget(label)
        lay.addWidget(self.cam_viewer)
        lay.addWidget(self.settings)

    def _setupSettingsLayout(self):
        label_CamEnbl = QLabel('Enable:', self)
        hbox_CamEnbl = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Enbl', propty_type='enbldisabl', width=3)

        label_FrameCnt = QLabel('Frame Count:', self)
        hbox_FrameCnt = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='FrameCnt', propty_type='mon')

        label_Conn = QLabel('Connection:', self)
        hbox_Conn = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Connection', propty_type='mon')

        label_Reset = QLabel('Reset Camera:', self)
        self.pb_dtl = PyDMPushButton(
            label='', icon=qta.icon('fa5s.sync'),
            parent=self, pressValue=1,
            init_channel=self.cam_prefix.substitute(propty='Rst-Cmd'))
        self.pb_dtl.setObjectName('reset')
        self.pb_dtl.setStyleSheet(
            "#reset{min-width:25px; max-width:25px; icon-size:20px;}")

        flay_sts = QFormLayout()
        flay_sts.setSpacing(6)
        flay_sts.setFormAlignment(Qt.AlignHCenter)
        flay_sts.setLabelAlignment(Qt.AlignRight)
        flay_sts.addRow(label_CamEnbl, hbox_CamEnbl)
        flay_sts.addRow(label_FrameCnt, hbox_FrameCnt)
        flay_sts.addRow(label_Conn, hbox_Conn)
        flay_sts.addRow(label_Reset, self.pb_dtl)

        label_AcqMode = QLabel('Acq. Mode:', self)
        hbox_AcqMode = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AcqMode', propty_type='enum')

        label_AcqPeriod = QLabel('Acq. Period [s]:', self)
        hbox_AcqPeriod = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='AcqPeriod', propty_type='sprb')

        label_ExpTime = QLabel('Exp. Time [us]:', self)
        hbox_ExpTime = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='ExposureTime', propty_type='sprb')

        label_Gain = QLabel('Gain [dB]:', self)
        hbox_Gain = create_propty_layout(
            parent=self, prefix=self.cam_prefix,
            propty='Gain', propty_type='sprb',
            cmd={'label': '', 'pressValue': 1, 'width': '25', 'height': '25',
                 'icon': qta.icon('mdi.auto-fix'), 'icon-size': '20',
                 'toolTip': 'Auto Gain', 'name': 'AutoGain'})

        flay_ctrl = QFormLayout()
        flay_ctrl.setSpacing(6)
        flay_ctrl.setFormAlignment(Qt.AlignHCenter)
        flay_ctrl.setLabelAlignment(Qt.AlignRight)
        flay_ctrl.addRow(label_AcqMode, hbox_AcqMode)
        flay_ctrl.addRow(label_AcqPeriod, hbox_AcqPeriod)
        flay_ctrl.addRow(label_ExpTime, hbox_ExpTime)
        flay_ctrl.addRow(label_Gain, hbox_Gain)

        self.pb_details = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        self.pb_details.setToolTip('More settings')
        self.pb_details.setObjectName('detail')
        self.pb_details.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        self.pb_details.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Preferred)
        MyWindow = create_window_from_widget(
            BaslerCamSettings, title=self.device+' Settings Details',
            is_main=True)
        util.connect_window(self.pb_details, MyWindow,
                            parent=self, prefix=self.prefix,
                            device=self.device)

        lay = QHBoxLayout()
        lay.setSpacing(20)
        lay.addLayout(flay_sts)
        lay.addLayout(flay_ctrl)
        lay.addWidget(self.pb_details, alignment=Qt.AlignTop)
        return lay
