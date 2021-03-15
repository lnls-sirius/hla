#!/usr/bin/env python-sirius

"""HLA as_ap_posang module."""

import os as _os
from epics import PV as _PV
from qtpy.QtWidgets import QGridLayout, QLabel, QGroupBox, QAbstractItemView, \
    QSizePolicy as QSzPlcy, QSpacerItem, QPushButton, QHeaderView, QWidget, \
    QMessageBox, QApplication, QHBoxLayout
from qtpy.QtCore import Qt
import qtawesome as qta
from pydm.widgets import PyDMWaveformTable, PyDMLabel, PyDMLineEdit, \
    PyDMPushButton, PyDMSpinbox

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.posang.csdev import Const
from siriuspy.namesys import SiriusPVName as _PVName

from siriushla import util as _hlautil
from siriushla.widgets import SiriusMainWindow, PyDMLogLabel, SiriusLedAlert, \
    PyDMLinEditScrollbar, PyDMLedMultiChannel, SiriusConnectionSignal
from siriushla.as_ps_control import PSDetailWindow as _PSDetailWindow
from siriushla.as_pu_control import PUDetailWindow as _PUDetailWindow
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


UI_FILE = (_os.path.abspath(_os.path.dirname(__file__))+'/ui_as_ap_posang.ui')


class PosAngCorr(SiriusMainWindow):
    """Main Class."""

    def __init__(self, parent=None, prefix='', tl=None):
        """Class construc."""
        super(PosAngCorr, self).__init__(parent)
        if not prefix:
            self._prefix = _VACA_PREFIX
        else:
            self._prefix = prefix
        self._tl = tl.upper()
        self.posang_prefix = self._prefix + self._tl + '-Glob:AP-PosAng'
        self.setObjectName(self._tl+'App')
        self.setWindowTitle(self._tl + ' Position and Angle Correction Window')

        if self._tl == 'TS':
            self._is_chsept = False
            ch3_pv = _PV(self.posang_prefix+':CH3-Cte',
                         connection_timeout=1)
            if not ch3_pv.wait_for_connection():
                self._is_chsept = True

        if tl == 'ts':
            corr_h = (Const.TS_CORRH_POSANG_CHSEPT if self._is_chsept
                      else Const.TS_CORRH_POSANG_SEPTSEPT)
            corr_v = Const.TS_CORRV_POSANG
        elif tl == 'tb':
            corr_h = Const.TB_CORRH_POSANG
            corr_v = Const.TB_CORRV_POSANG

        self.corrs = dict()
        self.corrs['CH1'] = _PVName(corr_h[0])
        self.corrs['CH2'] = _PVName(corr_h[1])
        if len(corr_h) == 3:
            self.corrs['CH3'] = _PVName(corr_h[2])
        self.corrs['CV1'] = _PVName(corr_v[0])
        self.corrs['CV2'] = _PVName(corr_v[1])
        if len(corr_v) == 4:
            self.corrs['CV3'] = _PVName(corr_v[2])
            self.corrs['CV4'] = _PVName(corr_v[3])

        self._just_need_update = False
        self._update_ref_action = False
        self._my_input_widgets = list()
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self._ask_message = QMessageBox(self)
        self._ask_message.setWindowTitle('Message')
        self._ask_message.setText(
            'The '+self._tl+' PosAng IOC indicates reference needs to '
            'be updated! Do you want to update the reference?')
        self._ask_message.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        self._ask_message.setDefaultButton(QMessageBox.No)
        self.app = QApplication.instance()
        self.app.focusChanged.connect(self._spinbox_onfocus)

    def _setupUi(self):
        cwt = QWidget(self)
        self.setCentralWidget(cwt)

        # label
        lab = QLabel(
            '<h3>'+self._tl+' Position and Angle Correction</h3>', cwt)
        lab.setStyleSheet("""
            min-height:1.55em; max-height: 1.55em;
            qproperty-alignment: 'AlignVCenter | AlignRight';
            background-color: qlineargradient(spread:pad, x1:1, y1:0.0227273,
                              x2:0, y2:0, stop:0 rgba(173, 190, 207, 255),
                              stop:1 rgba(213, 213, 213, 255));""")

        # apply button
        self.pb_updateref = PyDMPushButton(
            self, 'Update Reference', pressValue=1,
            init_channel=self.posang_prefix+':SetNewRefKick-Cmd')
        self.pb_updateref.setStyleSheet(
            'min-height: 2.4em; max-height: 2.4em;')
        self.led_needrefupdt = SiriusLedAlert(
            self, self.posang_prefix+':NeedRefUpdate-Mon')
        self.ch_needrefupdt = SiriusConnectionSignal(
            self.posang_prefix+':NeedRefUpdate-Mon')
        self.ch_needrefupdt.new_value_signal[int].connect(
            self._handle_need_update_ref_led)
        self.led_needrefupdt.setStyleSheet(
            'QLed{min-width: 1.29em; max-width: 1.29em;}')
        box_ref = QHBoxLayout()
        box_ref.setContentsMargins(0, 0, 0, 0)
        box_ref.addWidget(self.pb_updateref)
        box_ref.addWidget(self.led_needrefupdt)

        # delta setters
        self.hgbox = QGroupBox('Horizontal', self)
        self.hgbox.setLayout(self._setupDeltaControlLayout('x'))

        self.vgbox = QGroupBox('Vertical', self)
        self.vgbox.setLayout(self._setupDeltaControlLayout('y'))

        # correctors
        self.corrgbox = QGroupBox('Correctors', self)
        self.corrgbox.setLayout(self._setupCorrectorsLayout())

        # status
        self.statgbox = QGroupBox('Correction Status', self)
        self.statgbox.setLayout(self._setupStatusLayout())

        glay = QGridLayout(cwt)
        glay.setHorizontalSpacing(12)
        glay.setVerticalSpacing(12)
        glay.addWidget(lab, 0, 0, 1, 2)
        glay.addLayout(box_ref, 1, 0, 1, 2)
        glay.addWidget(self.hgbox, 2, 0)
        glay.addWidget(self.vgbox, 2, 1)
        glay.addWidget(self.corrgbox, 3, 0, 1, 2)
        glay.addWidget(self.statgbox, 4, 0, 1, 2)

        # menu
        act_settings = self.menuBar().addAction('Settings')
        _hlautil.connect_window(act_settings, CorrParamsDetailWindow,
                                parent=self, tl=self._tl, prefix=self._prefix)

        # stlesheet
        self.setStyleSheet("""
            PyDMSpinbox{
                min-width: 5em; max-width: 5em;
            }
            PyDMLabel, PyDMLinEditScrollbar{
                min-width: 6em; max-width: 6em;
            }
            QPushButton{
                min-width: 8em;
            }
            QLabel{
                min-height: 1.35em;
                qproperty-alignment: AlignCenter;
            }
        """)

    def _setupDeltaControlLayout(self, axis=''):
        # pos
        label_pos = QLabel("<h4>Δ"+axis+"</h4>", self)
        sb_deltapos = PyDMSpinbox(
            self, self.posang_prefix + ':DeltaPos'+axis.upper()+'-SP')
        sb_deltapos.step_exponent = -2
        sb_deltapos.update_step_size()
        sb_deltapos.showStepExponent = False
        lb_deltapos = PyDMLabel(
            self, self.posang_prefix + ':DeltaPos'+axis.upper()+'-RB')
        lb_deltapos.showUnits = True
        self._my_input_widgets.append(sb_deltapos)
        # ang
        label_ang = QLabel("<h4>Δ"+axis+"'</h4>", self)
        sb_deltaang = PyDMSpinbox(
            self, self.posang_prefix + ':DeltaAng'+axis.upper()+'-SP')
        sb_deltaang.step_exponent = -2
        sb_deltaang.update_step_size()
        sb_deltaang.showStepExponent = False
        lb_deltaang = PyDMLabel(
            self, self.posang_prefix + ':DeltaAng'+axis.upper()+'-RB')
        lb_deltaang.showUnits = True
        self._my_input_widgets.append(sb_deltaang)

        lay = QGridLayout()
        lay.setVerticalSpacing(12)
        lay.setHorizontalSpacing(12)
        lay.addItem(
            QSpacerItem(10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 0)
        lay.addWidget(label_pos, 0, 1)
        lay.addWidget(sb_deltapos, 0, 2)
        lay.addWidget(lb_deltapos, 0, 3)
        lay.addWidget(label_ang, 1, 1)
        lay.addWidget(sb_deltaang, 1, 2)
        lay.addWidget(lb_deltaang, 1, 3)
        lay.addItem(
            QSpacerItem(10, 0, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 4)
        return lay

    def _setupCorrectorsLayout(self):
        lay = QGridLayout()
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(9)

        label_kicksp = QLabel('<h4>Kick-SP</h4>', self)
        label_kickrb = QLabel('<h4>Kick-RB</h4>', self)
        label_kickref = QLabel('<h4>RefKick-Mon</h4>', self)
        lay.addWidget(label_kicksp, 0, 2)
        lay.addWidget(label_kickrb, 0, 3)
        lay.addWidget(label_kickref, 0, 4)

        idx = 1
        for corrid, corr in self.corrs.items():
            pbt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            pbt.setObjectName('pbt')
            pbt.setStyleSheet("""
                #pbt{
                    min-width:25px; max-width:25px;
                    min-height:25px; max-height:25px;
                    icon-size:20px;}
                """)
            if corr.dis == 'PU':
                _hlautil.connect_window(
                    pbt, _PUDetailWindow, self, devname=corr)
            else:
                _hlautil.connect_window(
                    pbt, _PSDetailWindow, self, psname=corr)
            lb_name = QLabel(corr, self)
            le_sp = PyDMLinEditScrollbar(self._prefix+corr+':Kick-SP', self)
            le_sp.layout.setContentsMargins(0, 0, 0, 0)
            le_sp.layout.setSpacing(3)
            le_sp.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
            le_sp.sp_lineedit.setStyleSheet("min-height:1.29em;")
            le_sp.sp_lineedit.setAlignment(Qt.AlignCenter)
            le_sp.sp_lineedit.setSizePolicy(QSzPlcy.Ignored, QSzPlcy.Fixed)
            le_sp.sp_scrollbar.setStyleSheet("max-height:0.7em;")
            le_sp.sp_scrollbar.limitsFromPV = True
            lb_rb = PyDMLabel(self, self._prefix+corr+':Kick-RB')
            lb_ref = PyDMLabel(
                self, self.posang_prefix+':RefKick'+corrid+'-Mon')

            lay.addWidget(pbt, idx, 0, alignment=Qt.AlignTop)
            lay.addWidget(
                lb_name, idx, 1, alignment=Qt.AlignLeft | Qt.AlignTop)
            lay.addWidget(le_sp, idx, 2, alignment=Qt.AlignTop)
            lay.addWidget(lb_rb, idx, 3, alignment=Qt.AlignTop)
            lay.addWidget(lb_ref, idx, 4, alignment=Qt.AlignTop)
            idx += 1

        if self._tl == 'TB':
            lay.addItem(QSpacerItem(0, 8, QSzPlcy.Ignored, QSzPlcy.Fixed))

            label_voltsp = QLabel('<h4>Amplitude-SP</h4>', self)
            label_voltrb = QLabel('<h4>Amplitude-RB</h4>', self)
            lay.addWidget(label_voltsp, idx+2, 2)
            lay.addWidget(label_voltrb, idx+2, 3)

            lb_kly2_name = QLabel('Klystron 2', self)
            le_kly2_sp = PyDMLinEditScrollbar(
                self._prefix+'LA-RF:LLRF:KLY2:SET_AMP', self)
            le_kly2_sp.layout.setContentsMargins(0, 0, 0, 0)
            le_kly2_sp.layout.setSpacing(3)
            le_kly2_sp.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
            le_kly2_sp.sp_lineedit.setStyleSheet("min-height:1.29em;")
            le_kly2_sp.sp_lineedit.precisionFromPV = False
            le_kly2_sp.sp_lineedit.precision = 2
            le_kly2_sp.sp_lineedit.setAlignment(Qt.AlignCenter)
            le_kly2_sp.sp_lineedit.setSizePolicy(
                QSzPlcy.Ignored, QSzPlcy.Fixed)
            le_kly2_sp.sp_scrollbar.setStyleSheet("max-height:0.7em;")
            le_kly2_sp.sp_scrollbar.limitsFromPV = True
            lb_kly2_rb = PyDMLabel(
                self, self._prefix+'LA-RF:LLRF:KLY2:GET_AMP')
            lb_kly2_rb.precisionFromPV = False
            lb_kly2_rb.precision = 2
            lay.addWidget(lb_kly2_name, idx+3, 1,
                          alignment=Qt.AlignLeft | Qt.AlignTop)
            lay.addWidget(le_kly2_sp, idx+3, 2, alignment=Qt.AlignTop)
            lay.addWidget(lb_kly2_rb, idx+3, 3, alignment=Qt.AlignTop)
            self._kckr_name = 'BO-01D:PU-InjKckr'
        else:
            self._kckr_name = 'SI-01SA:PU-InjNLKckr'

        label_voltsp = QLabel('<h4>Voltage-SP</h4>', self)
        label_voltrb = QLabel('<h4>Voltage-RB</h4>', self)
        lay.addWidget(label_voltsp, idx+4, 2)
        lay.addWidget(label_voltrb, idx+4, 3)

        lay.addItem(QSpacerItem(0, 8, QSzPlcy.Ignored, QSzPlcy.Fixed))
        pb_kckr = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        pb_kckr.setObjectName('pb')
        pb_kckr.setStyleSheet("""
            #pb{
                min-width:25px; max-width:25px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
            """)
        lb_kckr_name = QLabel(self._kckr_name, self)
        _hlautil.connect_window(
            pb_kckr, _PUDetailWindow, self, devname=self._kckr_name)
        lb_kckr_sp = PyDMLinEditScrollbar(
            self._prefix+self._kckr_name+':Voltage-SP', self)
        lb_kckr_sp.layout.setContentsMargins(0, 0, 0, 0)
        lb_kckr_sp.layout.setSpacing(3)
        lb_kckr_sp.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        lb_kckr_sp.sp_lineedit.setStyleSheet("min-height:1.29em;")
        lb_kckr_sp.sp_lineedit.setAlignment(Qt.AlignCenter)
        lb_kckr_sp.sp_lineedit.setSizePolicy(QSzPlcy.Ignored, QSzPlcy.Fixed)
        lb_kckr_sp.sp_scrollbar.setStyleSheet("max-height:0.7em;")
        lb_kckr_sp.sp_scrollbar.limitsFromPV = True
        lb_kckr_rb = PyDMLabel(
            self, self._prefix+self._kckr_name+':Voltage-RB')
        lay.addWidget(pb_kckr, idx+5, 0, alignment=Qt.AlignTop)
        lay.addWidget(
            lb_kckr_name, idx+5, 1, alignment=Qt.AlignLeft | Qt.AlignTop)
        lay.addWidget(lb_kckr_sp, idx+5, 2, alignment=Qt.AlignTop)
        lay.addWidget(lb_kckr_rb, idx+5, 3, alignment=Qt.AlignTop)
        return lay

    def _setupStatusLayout(self):
        self.log = PyDMLogLabel(self, self.posang_prefix+':Log-Mon')
        self.lb_sts0 = QLabel(Const.STATUSLABELS[0], self)
        self.led_sts0 = SiriusLedAlert(
            self, self.posang_prefix+':Status-Mon', bit=0)
        self.lb_sts1 = QLabel(Const.STATUSLABELS[1], self)
        self.led_sts1 = SiriusLedAlert(
            self, self.posang_prefix+':Status-Mon', bit=1)
        self.lb_sts2 = QLabel(Const.STATUSLABELS[2], self)
        self.led_sts2 = SiriusLedAlert(
            self, self.posang_prefix+':Status-Mon', bit=2)
        self.lb_sts3 = QLabel(Const.STATUSLABELS[3], self)
        self.led_sts3 = SiriusLedAlert(
            self, self.posang_prefix+':Status-Mon', bit=3)
        self.pb_config = PyDMPushButton(
            self, label='Config Correctors', pressValue=1,
            init_channel=self.posang_prefix+':ConfigPS-Cmd')

        lay = QGridLayout()
        lay.setVerticalSpacing(12)
        lay.setHorizontalSpacing(12)
        lay.addWidget(self.log, 0, 0, 6, 1)
        lay.addWidget(self.lb_sts0, 1, 2)
        lay.addWidget(self.led_sts0, 1, 1)
        lay.addWidget(self.lb_sts1, 2, 2)
        lay.addWidget(self.led_sts1, 2, 1)
        lay.addWidget(self.lb_sts2, 3, 2)
        lay.addWidget(self.led_sts2, 3, 1)
        lay.addWidget(self.lb_sts3, 4, 2)
        lay.addWidget(self.led_sts3, 4, 1)
        lay.addWidget(self.pb_config, 5, 1, 1, 2)

        if self._tl == 'TS':
            self.led_corrtype = PyDMLedMultiChannel(
                self, {self.posang_prefix+':CH1-Cte': self.corrs['CH1']})
            self.lb_corrtype = QLabel(
                'Control ' + ('CH-Sept' if self._is_chsept else 'Sept-Sept'))
            lay.addWidget(self.led_corrtype, 0, 1)
            lay.addWidget(self.lb_corrtype, 0, 2)
        return lay

    def _set_correctors_channels(self, corrs):
        self.centralwidget.pushButton_CH1.setText(corrs[0])
        _hlautil.connect_window(
            self.centralwidget.pushButton_CH1, _PSDetailWindow, self,
            psname=corrs[0])
        self.centralwidget.PyDMLabel_KickRBCH1.channel = (
            self._prefix + corrs[0] + ':Kick-RB')

        self.centralwidget.pushButton_CH2.setText(corrs[1])
        if corrs[1].dis == 'PU':
            _hlautil.connect_window(
                self.centralwidget.pushButton_CH2, _PUDetailWindow, self,
                devname=corrs[1])
        else:
            _hlautil.connect_window(
                self.centralwidget.pushButton_CH2, _PSDetailWindow, self,
                psname=corrs[1])
        self.centralwidget.PyDMLabel_KickRBCH2.channel = (
            self._prefix + corrs[1] + ':Kick-RB')

        self.centralwidget.pushButton_CV1.setText(corrs[2])
        _hlautil.connect_window(
            self.centralwidget.pushButton_CV1, _PSDetailWindow, self,
            psname=corrs[2])
        self.centralwidget.PyDMLabel_KickRBCV1.channel = (
            self._prefix + corrs[2] + ':Kick-RB')

        self.centralwidget.pushButton_CV2.setText(corrs[3])
        _hlautil.connect_window(
            self.centralwidget.pushButton_CV2, _PSDetailWindow, self,
            psname=corrs[3])
        self.centralwidget.PyDMLabel_KickRBCV2.channel = (
            self._prefix + corrs[3] + ':Kick-RB')

    def _handle_need_update_ref_led(self, value):
        self._just_need_update = bool(value)

    def _spinbox_onfocus(self, old_focus, new_focus):
        if not self._update_ref_action and not self._just_need_update:
            return

        if self.led_needrefupdt.value != 0:
            if new_focus in self._my_input_widgets and self._just_need_update:
                ans = self._ask_message.exec_()
                if ans == QMessageBox.No:
                    self._update_ref_action = False
                else:
                    self._update_ref_action = True
                    self.pb_updateref.sendValue()
                self._just_need_update = False


class CorrParamsDetailWindow(SiriusMainWindow):
    """Correction parameters detail window."""

    def __init__(self, tl, parent=None, prefix=None):
        """Class constructor."""
        super(CorrParamsDetailWindow, self).__init__(parent)
        self._tl = tl
        self.setObjectName(tl.upper()+'App')
        self._prefix = prefix
        self.setWindowTitle(
            self._tl + ' Position and Angle Correction Parameters')
        self._setupUi()

    def _setupUi(self):
        label_configname = QLabel('<h4>Configuration Name</h4>', self,
                                  alignment=Qt.AlignCenter)
        self.pydmlinedit_configname = _ConfigLineEdit(
            self, self._prefix+self._tl+'-Glob:AP-PosAng:ConfigName-SP')
        self.pydmlabel_configname = PyDMLabel(
            self, self._prefix+self._tl+'-Glob:AP-PosAng:ConfigName-RB')

        label_matrix_x = QLabel('<h4>Matrix X</h4>', self,
                                alignment=Qt.AlignCenter)
        self.table_matrix_x = PyDMWaveformTable(
            self, self._prefix+self._tl+'-Glob:AP-PosAng:RespMatX-Mon')
        self.table_matrix_x.setObjectName('table_matrix_x')
        self.table_matrix_x.setStyleSheet("""
            #table_matrix_x{
                min-width:12em; max-width:12em;
                min-height:4.65em; max-height:4.65em;}""")
        self.table_matrix_x.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix_x.setRowCount(2)
        self.table_matrix_x.setColumnCount(2)
        self.table_matrix_x.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_x.horizontalHeader().setVisible(False)
        self.table_matrix_x.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_x.verticalHeader().setVisible(False)
        self.table_matrix_x.setSizePolicy(
           QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)

        columns = 2 if self._tl == 'TB' else 4
        width = 12 if self._tl == 'TB' else 24
        label_matrix_y = QLabel('<h4>Matrix Y</h4>', self,
                                alignment=Qt.AlignCenter)
        self.table_matrix_y = PyDMWaveformTable(
            self, self._prefix+self._tl+'-Glob:AP-PosAng:RespMatY-Mon')
        self.table_matrix_y.setObjectName('table_matrix_y')
        self.table_matrix_y.setStyleSheet("""
            #table_matrix_y{
                min-width:valem; max-width:valem;
                min-height:4.65em; max-height:4.65em;}""".replace(
                    'val', str(width)))
        self.table_matrix_y.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix_y.setRowCount(2)
        self.table_matrix_y.setColumnCount(columns)
        self.table_matrix_y.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_y.horizontalHeader().setVisible(False)
        self.table_matrix_y.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_y.verticalHeader().setVisible(False)
        self.table_matrix_y.setSizePolicy(
            QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)

        self.bt_apply = QPushButton('Ok', self)
        self.bt_apply.clicked.connect(self.close)

        lay = QGridLayout()
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 0, 0)
        lay.addWidget(label_configname, 1, 0, 1, columns)
        lay.addWidget(self.pydmlinedit_configname, 2, 0, 1, columns)
        lay.addWidget(self.pydmlabel_configname, 3, 0, 1, columns)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 4, 0)
        lay.addWidget(label_matrix_x, 5, 0, 1, columns)
        lay.addWidget(self.table_matrix_x, 6, (columns/2)-1, 1, columns)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 7, 0)
        lay.addWidget(label_matrix_y, 8, 0, 1, columns)
        lay.addWidget(self.table_matrix_y, 9, 0, 1, columns)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 10, 0)
        lay.addWidget(self.bt_apply, 11, columns-1)
        for i in range(columns):
            lay.setColumnStretch(i, 1)
        self.centralwidget = QGroupBox('Correction Parameters')
        self.centralwidget.setLayout(lay)
        self.setCentralWidget(self.centralwidget)

        self.setStyleSheet("""
            PyDMLabel{
                min-width:valem; max-width:valem;
            }""".replace('val', str(width)))


class _ConfigLineEdit(PyDMLineEdit):
    """Configuration line edit."""

    def mouseReleaseEvent(self, _):
        """Reimplement mouseReleaseEvent."""
        if 'TB' in self.channel:
            config_type = 'tb_posang_respm'
        elif 'TS' in self.channel:
            config_type = 'ts_posang_respm'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)
