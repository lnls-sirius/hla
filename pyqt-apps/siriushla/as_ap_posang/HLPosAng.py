#!/usr/bin/env python-sirius

"""HLA as_ap_posang module."""

import epics as _epics
from pydm.PyQt.uic import loadUi as _loadUi
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _hlautil
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
from siriushla.as_pm_control.PulsedMagnetDetailWindow import (
                                PulsedMagnetDetailWindow)

UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
           'as_ap_posang/ui_as_ap_posang.ui')


class ASAPPosAngCorr(SiriusMainWindow):
    """Main Class."""

    def __init__(self, parent=None, prefix='', tl=None):
        """Class construc."""
        super(ASAPPosAngCorr, self).__init__(parent)
        if prefix == '':
            prefix = _vaca_prefix

        tmp_file = _substitute_in_file(UI_FILE, {'TRANSPORTLINE': tl.upper(),
                                                 'PREFIX': prefix})
        self.centralwidget = _loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        self._tl = tl
        self.setWindowTitle(self._tl.upper() +
                            ' Position and Angle Correction Window')

        widget2pv_list = [[self.centralwidget.PyDMLineEdit_OrbXDeltaPos_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaPos_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaPos_RB,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbXDeltaAng_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbXDeltaAng_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngX-SP'],
                          [self.centralwidget.PyDMLabel_OrbXDeltaAng_RB,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngX-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaPos_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaPos_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaPos_RB,
                           tl.upper()+'-Glob:AP-PosAng:DeltaPosY-RB'],
                          [self.centralwidget.PyDMLineEdit_OrbYDeltaAng_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMScrollBar_OrbYDeltaAng_SP,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngY-SP'],
                          [self.centralwidget.PyDMLabel_OrbYDeltaAng_RB,
                           tl.upper()+'-Glob:AP-PosAng:DeltaAngY-RB'],
                          [self.centralwidget.PyDMPushButton_SetNewRefKick,
                           tl.upper()+'-Glob:AP-PosAng:SetNewRefKick-Cmd'],
                          [self.centralwidget.PyDMPushButton_ConfigMA,
                           tl.upper()+'-Glob:AP-PosAng:ConfigMA-Cmd'],
                          [self.centralwidget.PyDMLabel_RefKickCH1Mon,
                           tl.upper()+'-Glob:AP-PosAng:RefKickCH1-Mon'],
                          [self.centralwidget.PyDMLabel_RefKickCH2Mon,
                           tl.upper()+'-Glob:AP-PosAng:RefKickCH2-Mon'],
                          [self.centralwidget.PyDMLabel_RefKickCV1Mon,
                           tl.upper()+'-Glob:AP-PosAng:RefKickCV1-Mon'],
                          [self.centralwidget.PyDMLabel_RefKickCV2Mon,
                           tl.upper()+'-Glob:AP-PosAng:RefKickCV2-Mon'],
                          [self.centralwidget.PyDMLineEdit_ConfigName,
                           tl.upper()+'-Glob:AP-PosAng:ConfigName-SP'],
                          [self.centralwidget.PyDMLabel_ConfigName,
                           tl.upper()+'-Glob:AP-PosAng:ConfigName-RB'],
                          [self.centralwidget.PyDMLabel_RespMatX,
                           tl.upper()+'-Glob:AP-PosAng:RespMatX-Mon'],
                          [self.centralwidget.PyDMLabel_RespMatY,
                           tl.upper()+'-Glob:AP-PosAng:RespMatY-Mon']]
        self.set_widgets_channel(widget2pv_list, prefix)

        correctors = ['', '', '', '']
        if tl == 'ts':
            correctors[0] = 'TS-04:MA-CH'
            correctors[1] = 'TS-04:PM-InjSeptF'
            correctors[2] = 'TS-04:MA-CV-1'
            correctors[3] = 'TS-04:MA-CV-2'
        elif tl == 'tb':
            correctors[0] = 'TB-03:MA-CH'
            correctors[1] = 'TB-04:PM-InjSept'
            correctors[2] = 'TB-04:MA-CV-1'
            correctors[3] = 'TB-04:MA-CV-2'
        self._setCorrectorsLabels(correctors, prefix)

        self.statusLabel_pv = _epics.PV(
            prefix + tl.upper() + '-Glob:AP-PosAng:Status-Cte')
        self.statusLabel_pv.add_callback(self._setStatusLabels)

    def set_widgets_channel(self, widget2pv_list, prefix):
        """Set the PyDMWidgets channels.

        Receive:
        widget_list --list of widgets to set channel
        pv_list     --list of correspondent pvs
        """
        for widget, pv in widget2pv_list:
            widget.channel = 'ca://' + prefix + pv

    def _setCorrectorsLabels(self, correctors, prefix):
        if prefix is None:
            prefix = _vaca_prefix

        self.centralwidget.pushButton_CH1.setText(correctors[0])
        _hlautil.connect_window(self.centralwidget.pushButton_CH1,
                                PSDetailWindow, self,
                                maname=correctors[0])
        self.centralwidget.SiriusLedState_CH1.channel = (
            'ca://' + prefix + correctors[0] + ':PwrState-Sts')
        self.centralwidget.PyDMLabel_OpModeCH1.channel = (
            'ca://' + prefix + correctors[0] + ':OpMode-Sts')
        self.centralwidget.PyDMLabel_KickRBCH1.channel = (
            'ca://' + prefix + correctors[0] + ':Kick-RB')
        self.centralwidget.pushButton_CH2.setText(correctors[1])
        _hlautil.connect_window(self.centralwidget.pushButton_CH2,
                                PulsedMagnetDetailWindow, self,
                                maname=correctors[1])
        self.centralwidget.SiriusLedState_CH2.channel = (
            'ca://' + prefix + correctors[1] + ':PwrState-Sts')
        self.centralwidget.PyDMLabel_KickRBCH2.channel = (
            'ca://' + prefix + correctors[1] + ':Kick-RB')
        self.centralwidget.pushButton_CV1.setText(correctors[2])
        _hlautil.connect_window(self.centralwidget.pushButton_CV1,
                                PSDetailWindow, self,
                                maname=correctors[2])
        self.centralwidget.SiriusLedState_CV1.channel = (
            'ca://' + prefix + correctors[2] + ':PwrState-Sts')
        self.centralwidget.PyDMLabel_OpModeCV1.channel = (
            'ca://' + prefix + correctors[2] + ':OpMode-Sts')
        self.centralwidget.PyDMLabel_KickRBCV1.channel = (
            'ca://' + prefix + correctors[2] + ':Kick-RB')
        self.centralwidget.pushButton_CV2.setText(correctors[3])
        _hlautil.connect_window(self.centralwidget.pushButton_CV2,
                                PSDetailWindow, self,
                                maname=correctors[3])
        self.centralwidget.SiriusLedState_CV2.channel = (
            'ca://' + prefix + correctors[3] + ':PwrState-Sts')
        self.centralwidget.PyDMLabel_OpModeCV2.channel = (
            'ca://' + prefix + correctors[3] + ':OpMode-Sts')
        self.centralwidget.PyDMLabel_KickRBCV2.channel = (
            'ca://' + prefix + correctors[3] + ':Kick-RB')

    def _setStatusLabels(self, value, **kws):
        for i in range(4):
            exec('self.centralwidget.label_status{0}.setText'
                 '(value[{0}])'.format(i))
