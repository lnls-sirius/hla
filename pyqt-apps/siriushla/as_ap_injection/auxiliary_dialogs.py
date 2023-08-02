"""Auxiliary Dialogs."""

import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, \
    QTabWidget, QWidget, QLabel, QGroupBox, QSizePolicy as QSzPlcy, \
    QSpacerItem

from pyqtgraph import mkBrush, FillBetweenItem

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName

from ..widgets import SiriusDialog, SiriusWaveformPlot, \
    SiriusEnumComboBox, SiriusSpinbox, SiriusLabel, \
    SiriusLedState, PyDMStateButton, SiriusConnectionSignal


class BiasFBDetailDialog(SiriusDialog):
    """Bias FB detail dialog."""

    def __init__(self, parent=None, device='', prefix=''):
        super().__init__(parent)
        self._prefix = prefix
        self._inj_dev = SiriusPVName(device)
        self._inj_prefix = device.substitute(prefix=prefix)
        self.setObjectName('ASApp')
        self.setWindowTitle('Injection Controls - Bias Feedback Settings')
        self._setupUi()

    def _setupUi(self):
        title = QLabel(
            '<h4>Bias Feedback Settings</h4>', self,
            alignment=Qt.AlignCenter)

        # global parameters
        wid_global = self._setupGlobalParams()

        # fitting settings
        wid_model = self._setupModelParams()

        # graphs: model inference and prediction
        tab_graphs = QTabWidget(self)
        wid_graphinf = self._setupInferenceGraph()
        tab_graphs.addTab(wid_graphinf, 'Inferences')
        wid_graphpred = self._setupPredictionGraph()
        tab_graphs.addTab(wid_graphpred, 'Models')
        tab_graphs.setObjectName('ASTab')
        tab_graphs.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")

        lay = QVBoxLayout(self)
        lay.addWidget(title)
        lay.addWidget(wid_global)
        lay.addWidget(wid_model)
        lay.addWidget(tab_graphs)

    def _setupGlobalParams(self):
        ld_minv = QLabel(
            'Min.:', self, alignment=Qt.AlignRight)
        sb_minv = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='BiasFBMinVoltage-SP'))
        lb_minv = SiriusLabel(
            self, self._inj_prefix.substitute(propty='BiasFBMinVoltage-RB'))
        lb_minv.showUnits = True
        ld_maxv = QLabel(
            'Max.:', self, alignment=Qt.AlignRight)
        sb_maxv = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='BiasFBMaxVoltage-SP'))
        lb_maxv = SiriusLabel(
            self, self._inj_prefix.substitute(propty='BiasFBMaxVoltage-RB'))
        lb_maxv.showUnits = True

        wid = QGroupBox('Bias Limits')
        lay = QHBoxLayout(wid)
        lay.addStretch()
        lay.addWidget(ld_minv)
        lay.addWidget(sb_minv)
        lay.addWidget(lb_minv)
        lay.addStretch()
        lay.addWidget(ld_maxv)
        lay.addWidget(sb_maxv)
        lay.addWidget(lb_maxv)
        lay.addStretch()

        wid.setStyleSheet("""
            .QLabel{
                min-width: 7em; min-height: 1.5em; max-height: 1.5em;
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }""")
        return wid

    def _setupModelParams(self):
        ld_modtyp = QLabel(
            'Type:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        cb_modtyp = SiriusEnumComboBox(
            self, self._inj_prefix.substitute(propty='BiasFBModelType-Sel'))
        lb_modtyp = SiriusLabel(
            self, self._inj_prefix.substitute(propty='BiasFBModelType-Sts'))

        ld_modupd = QLabel(
            'Update data:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_modupd = PyDMStateButton(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelUpdateData-Sel'))
        led_modupd = SiriusLedState(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelUpdateData-Sts'))

        lay1 = QHBoxLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addStretch()
        lay1.addWidget(ld_modtyp)
        lay1.addWidget(cb_modtyp)
        lay1.addWidget(lb_modtyp)
        lay1.addStretch()
        lay1.addWidget(ld_modupd)
        lay1.addWidget(sb_modupd)
        lay1.addWidget(led_modupd, alignment=Qt.AlignLeft)
        lay1.addStretch()

        gbox_autofit = QGroupBox('Auto Fit')
        ld_autofit = QLabel(
            'Enable:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        cb_autofit = PyDMStateButton(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelAutoFitParams-Sel'))
        led_autofit = SiriusLedState(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelAutoFitParams-Sts'))
        ld_autofitnp = QLabel(
            'Every # pts.:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        cb_autofitnp = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelAutoFitEveryNrPts-SP'))
        lb_autofitnp = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelAutoFitEveryNrPts-RB'))
        glay_autofit = QGridLayout(gbox_autofit)
        glay_autofit.addWidget(ld_autofit, 0, 0)
        glay_autofit.addWidget(cb_autofit, 0, 1)
        glay_autofit.addWidget(led_autofit, 0, 2, alignment=Qt.AlignLeft)
        glay_autofit.addWidget(ld_autofitnp, 1, 0)
        glay_autofit.addWidget(cb_autofitnp, 1, 1)
        glay_autofit.addWidget(lb_autofitnp, 1, 2)

        ld_modmaxnp = QLabel(
            'Max. # pts.:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_modmaxnp = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelMaxNrPts-SP'))
        lb_modmaxnp = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelMaxNrPts-RB'),
            alignment=Qt.AlignCenter)
        slash = QLabel('/', self, alignment=Qt.AlignCenter)
        slash.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        lb_modnp = SiriusLabel(
            self, self._inj_prefix.substitute(propty='BiasFBModelNrPts-Mon'),
            alignment=Qt.AlignCenter)
        hlay_modmaxnp = QHBoxLayout()
        hlay_modmaxnp.setContentsMargins(0, 0, 0, 0)
        hlay_modmaxnp.addWidget(sb_modmaxnp)
        hlay_modmaxnp.addWidget(lb_modnp)
        hlay_modmaxnp.addWidget(slash)
        hlay_modmaxnp.addWidget(lb_modmaxnp)

        ld_npafterfit = QLabel(
            '# pts. after last fit:', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        lb_npafterfit = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBModelNrPtsAfterFit-Mon'))

        pb_fitnow = PyDMPushButton(
            self, label='Fit Now', pressValue=1,
            init_channel=self._inj_prefix.substitute(
                propty='BiasFBModelFitParamsNow-Cmd'))
        pb_fitnow.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        pb_fitnow.setDefault(False)
        pb_fitnow.setAutoDefault(False)

        lay2 = QGridLayout()
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.setAlignment(Qt.AlignCenter)
        lay2.addWidget(gbox_autofit, 0, 0, 2, 3, alignment=Qt.AlignCenter)
        lay2.addItem(
            QSpacerItem(20, QSzPlcy.Minimum, QSzPlcy.Preferred), 0, 3)
        lay2.addWidget(ld_modmaxnp, 0, 4)
        lay2.addLayout(hlay_modmaxnp, 0, 5, 1, 2)
        lay2.addWidget(ld_npafterfit, 1, 4)
        lay2.addWidget(lb_npafterfit, 1, 5)
        lay2.addWidget(pb_fitnow, 1, 6, alignment=Qt.AlignCenter)

        tab_models = QTabWidget(self)
        wid_linmod = self._setupLinearParams()
        tab_models.addTab(wid_linmod, 'Linear')
        wid_gpmod = self._setupGPParams()
        tab_models.addTab(wid_gpmod, 'Gaussian Process')
        tab_models.setObjectName('ASTab')
        tab_models.setStyleSheet("""
            QTabWidget::pane{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")

        wid = QGroupBox('Model settings')
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignTop)
        lay.addLayout(lay1)
        lay.addLayout(lay2)
        lay.addWidget(tab_models)
        return wid

    def _setupLinearParams(self):
        ld_ang = QLabel('Ang. Coeff.:', self, alignment=Qt.AlignRight)
        sb_ang = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModAngCoeff-SP'))
        lb_ang = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModAngCoeff-RB'))
        lb_ang_mon = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModAngCoeff-Mon'))

        ld_offset = QLabel('Offset Coeff.:', self, alignment=Qt.AlignRight)
        sb_offset = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModOffCoeff-SP'))
        lb_offset = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModOffCoeff-RB'))
        lb_offset_mon = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBLinModOffCoeff-Mon'))

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        lay.addWidget(ld_ang, 0, 0)
        lay.addWidget(sb_ang, 0, 1)
        lay.addWidget(lb_ang, 0, 2)
        lay.addWidget(lb_ang_mon, 0, 3)
        lay.addWidget(ld_offset, 1, 0)
        lay.addWidget(sb_offset, 1, 1)
        lay.addWidget(lb_offset, 1, 2)
        lay.addWidget(lb_offset_mon, 1, 3)

        wid.setStyleSheet("""
            .QLabel{
                min-width: 7em; min-height: 1.5em; max-height: 1.5em;
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }""")
        return wid

    def _setupGPParams(self):
        ld_likehdvar = QLabel(
            'Likelihood std.:', self, alignment=Qt.AlignRight)
        sb_likehdvar = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModNoiseStd-SP'))
        lb_likehdvar = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModNoiseStd-RB'))
        lb_likehdvar_mon = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModNoiseStd-Mon'))
        pb_likehdvarfit = PyDMStateButton(self, self._inj_prefix.substitute(
            propty='BiasFBGPModNoiseStdFit-Sel'))
        lb_likehdvarfit = SiriusLabel(self, self._inj_prefix.substitute(
            propty='BiasFBGPModNoiseStdFit-Sts'))

        ld_kernvar = QLabel(
            'Kernel std.:', self, alignment=Qt.AlignRight)
        sb_kernvar = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernStd-SP'))
        lb_kernvar = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernStd-RB'))
        lb_kernvar_mon = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernStd-Mon'))
        pb_kernvarfit = PyDMStateButton(self, self._inj_prefix.substitute(
            propty='BiasFBGPModKernStdFit-Sel'))
        lb_kernvarfit = SiriusLabel(self, self._inj_prefix.substitute(
            propty='BiasFBGPModKernStdFit-Sts'))

        ld_kernlenscl = QLabel(
            'Kernel length scale:', self, alignment=Qt.AlignRight)
        sb_kernlenscl = SiriusSpinbox(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernLenScl-SP'))
        lb_kernlenscl = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernLenScl-RB'))
        lb_kernlenscl_mon = SiriusLabel(
            self, self._inj_prefix.substitute(
                propty='BiasFBGPModKernLenScl-Mon'))
        pb_kernlensclfit = PyDMStateButton(self, self._inj_prefix.substitute(
            propty='BiasFBGPModKernLenSclFit-Sel'))
        lb_kernlensclfit = SiriusLabel(self, self._inj_prefix.substitute(
            propty='BiasFBGPModKernLenSclFit-Sts'))

        ld_dofit = QLabel('  Fit?', self)
        ld_dofit.setStyleSheet("""
            min-width: 3em; min-height: 1.5em; max-height: 1.5em;
            qproperty-alignment: 'AlignRight | AlignVCenter';""")

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        lay.addWidget(ld_likehdvar, 0, 1)
        lay.addWidget(sb_likehdvar, 0, 2)
        lay.addWidget(lb_likehdvar, 0, 3)
        lay.addWidget(lb_likehdvar_mon, 0, 4)
        lay.addWidget(pb_likehdvarfit, 0, 6)
        lay.addWidget(lb_likehdvarfit, 0, 7)
        lay.addWidget(ld_kernvar, 1, 1)
        lay.addWidget(sb_kernvar, 1, 2)
        lay.addWidget(lb_kernvar, 1, 3)
        lay.addWidget(lb_kernvar_mon, 1, 4)
        lay.addWidget(pb_kernvarfit, 1, 6)
        lay.addWidget(lb_kernvarfit, 1, 7)
        lay.addWidget(ld_kernlenscl, 2, 1)
        lay.addWidget(sb_kernlenscl, 2, 2)
        lay.addWidget(lb_kernlenscl, 2, 3)
        lay.addWidget(lb_kernlenscl_mon, 2, 4)
        lay.addWidget(pb_kernlensclfit, 2, 6)
        lay.addWidget(lb_kernlensclfit, 2, 7)
        lay.addWidget(ld_dofit, 0, 5, 3, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(8, 2)

        wid.setStyleSheet("""
            .QLabel{
                min-width: 7em; min-height: 1.5em; max-height: 1.5em;
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }
            .PyDMStateButton{
                min-width: 3.2em; min-height: 1.5em; max-height: 1.5em;
            }""")
        return wid

    def _setupInferenceGraph(self):
        # Injcurr X Bias: model inference about the bias
        self.graph_inf = SiriusWaveformPlot()
        self.graph_inf.addChannel(
            y_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModInferenceBias-Mon'),
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModInferenceInjCurr-Mon'),
            name='GP', color=QColor(80, 80, 80), lineWidth=2)
        self.graph_inf.addChannel(
            y_channel=self._inj_prefix.substitute(
                propty='BiasFBLinModInferenceBias-Mon'),
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBLinModInferenceInjCurr-Mon'),
            name='Linear', color='blue', lineWidth=2)
        self.graph_inf.autoRangeX = True
        self.graph_inf.autoRangeY = True
        self.graph_inf.showXGrid = True
        self.graph_inf.showYGrid = True
        self.graph_inf.showLegend = True
        self.graph_inf.title = 'Model inference: Inj.Current X Bias Voltage'
        self.graph_inf.setLabel(
            'bottom', text='Inj. current [mA]')
        self.graph_inf.setLabel(
            'left', text='Bias voltage [V]', color='gray')
        self.graph_inf.setBackgroundColor(QColor(255, 255, 255))

        return self.graph_inf

    def _setupPredictionGraph(self):
        # Bias x InjCurr: model prediction about current (check sanity)
        self.graph_pred = SiriusWaveformPlot()
        self.graph_pred.addChannel(
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModPredBias-Mon'),
            y_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModPredInjCurrAvg-Mon'),
            name='GP with 95% Conf.', color=QColor(80, 80, 80), lineWidth=2)
        self.graph_pred.addChannel(
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModPredBias-Mon'),
            y_channel='FAKE:GP_Avg_plus_Std',
            name='extra1', color='gray',
            lineWidth=2, lineStyle=Qt.DashLine)
        self._curve_gp_pred_avg_p_std = self.graph_pred.curveAtIndex(-1)
        self.graph_pred.addChannel(
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBGPModPredBias-Mon'),
            y_channel='FAKE:GP_Avg_minus_Std',
            name='extra2', color='gray',
            lineWidth=2, lineStyle=Qt.DashLine)
        self._curve_gp_pred_avg_m_std = self.graph_pred.curveAtIndex(-1)
        self.graph_pred.legend.removeItem('extra1')
        self.graph_pred.legend.removeItem('extra2')
        self._curve_gp_fill_std = FillBetweenItem(
            self._curve_gp_pred_avg_p_std, self._curve_gp_pred_avg_m_std,
            brush=mkBrush(QColor('lightGray')))
        self.graph_pred.addChannel(
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBLinModPredBias-Mon'),
            y_channel=self._inj_prefix.substitute(
                propty='BiasFBLinModPredInjCurrAvg-Mon'),
            name='Linear', color='blue', lineWidth=2)
        self.graph_pred.addChannel(
            x_channel=self._inj_prefix.substitute(
                propty='BiasFBModelDataBias-Mon'),
            y_channel=self._inj_prefix.substitute(
                propty='BiasFBModelDataInjCurr-Mon'),
            name='Model data', color='black', lineStyle=Qt.NoPen,
            symbol='o', symbolSize=6)
        curve = self.graph_pred.curveAtIndex(-1)
        curve.opts['symbolBrush'] = mkBrush(QColor(0, 0, 0))
        self.graph_pred.addItem(self._curve_gp_fill_std)
        self.graph_pred.autoRangeX = True
        self.graph_pred.autoRangeY = True
        self.graph_pred.showXGrid = True
        self.graph_pred.showYGrid = True
        self.graph_pred.showLegend = True
        self.graph_pred.title = 'Model prediction: Bias Voltage X Inj.Current'
        self.graph_pred.setLabel(
            'bottom', text='Bias voltage [V]')
        self.graph_pred.setLabel(
            'left', text='Inj. current [mA]', color='gray')
        self.graph_pred.setBackgroundColor(QColor(255, 255, 255))

        self._chn_gp_injcurr_avg = SiriusConnectionSignal(
            self._inj_prefix.substitute(
                propty='BiasFBGPModPredInjCurrAvg-Mon'))
        self._chn_gp_injcurr_std = SiriusConnectionSignal(
            self._inj_prefix.substitute(
                propty='BiasFBGPModPredInjCurrStd-Mon'))
        self._chn_gp_injcurr_avg.new_value_signal[_np.ndarray].connect(
            self._plot_gp_prediction_confidance)
        self._chn_gp_injcurr_std.new_value_signal[_np.ndarray].connect(
            self._plot_gp_prediction_confidance)

        return self.graph_pred

    def _plot_gp_prediction_confidance(self, _):
        avg = self._chn_gp_injcurr_avg.value
        std = self._chn_gp_injcurr_std.value
        if avg is None or std is None:
            return
        avg = _np.asarray(avg)
        std = _np.asarray(std)
        if avg.size != std.size:
            return
        self._curve_gp_pred_avg_p_std.receiveYWaveform(avg + 1.96*std)
        self._curve_gp_pred_avg_m_std.receiveYWaveform(avg - 1.96*std)


class TopUpSettingsDialog(SiriusDialog):
    """Top up settings dialog."""

    def __init__(self, parent=None, device='', prefix=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._inj_dev = SiriusPVName(device)
        self._inj_prefix = device.substitute(prefix=prefix)
        self.setObjectName('ASApp')
        self.setWindowTitle(
            'Injection Controls - Top Up Standby and Warm Up Settings')
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        title = QLabel(
            '<h4>Top Up Standby and Warm Up Settings</h4>', self,
            alignment=Qt.AlignCenter)

        pvname = self._inj_prefix.substitute(propty='TopUpPUStandbyEnbl-Sel')
        self._sb_tupuenb = PyDMStateButton(self, pvname)
        self._led_tupuenb = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        pvname = self._inj_prefix.substitute(propty='TopUpPUWarmUpTime-SP')
        self._sb_tuputim = SiriusSpinbox(self, pvname)
        self._lb_tuputim = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_tuputim.showUnits = True

        pvname = self._inj_prefix.substitute(propty='TopUpLIWarmUpEnbl-Sel')
        self._sb_tulienb = PyDMStateButton(self, pvname)
        self._led_tulienb = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        pvname = self._inj_prefix.substitute(propty='TopUpLIWarmUpTime-SP')
        self._sb_tulitim = SiriusSpinbox(self, pvname)
        self._lb_tulitim = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_tulitim.showUnits = True

        pvname = self._inj_prefix.substitute(propty='TopUpBOPSStandbyEnbl-Sel')
        self._sb_tubopsenb = PyDMStateButton(self, pvname)
        self._led_tubopsenb = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        pvname = self._inj_prefix.substitute(propty='TopUpBOPSWarmUpTime-SP')
        self._sb_tubopstim = SiriusSpinbox(self, pvname)
        self._lb_tubopstim = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_tubopstim.showUnits = True

        pvname = self._inj_prefix.substitute(propty='TopUpBORFStandbyEnbl-Sel')
        self._sb_tuborfenb = PyDMStateButton(self, pvname)
        self._led_tuborfenb = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        pvname = self._inj_prefix.substitute(propty='TopUpBORFWarmUpTime-SP')
        self._sb_tuborftim = SiriusSpinbox(self, pvname)
        self._lb_tuborftim = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_tuborftim.showUnits = True

        lay = QGridLayout(self)
        lay.addWidget(title, 0, 0, 1, 5)
        lay.addWidget(QLabel('Enable State'), 1, 1, 1, 2)
        lay.addWidget(QLabel('Warm Up Time'), 1, 3, 1, 2)
        lay.addWidget(QLabel('AS PU Standby'), 2, 0)
        lay.addWidget(self._sb_tupuenb, 2, 1)
        lay.addWidget(self._led_tupuenb, 2, 2)
        lay.addWidget(self._sb_tuputim, 2, 3)
        lay.addWidget(self._lb_tuputim, 2, 4)
        lay.addWidget(QLabel('LI PU/RF Warm Up'), 3, 0)
        lay.addWidget(self._sb_tulienb, 3, 1)
        lay.addWidget(self._led_tulienb, 3, 2)
        lay.addWidget(self._sb_tulitim, 3, 3)
        lay.addWidget(self._lb_tulitim, 3, 4)
        lay.addWidget(QLabel('BO PS Standby'), 4, 0)
        lay.addWidget(self._sb_tubopsenb, 4, 1)
        lay.addWidget(self._led_tubopsenb, 4, 2)
        lay.addWidget(self._sb_tubopstim, 4, 3)
        lay.addWidget(self._lb_tubopstim, 4, 4)
        lay.addWidget(QLabel('BO RF Standby'), 5, 0)
        lay.addWidget(self._sb_tuborfenb, 5, 1)
        lay.addWidget(self._led_tuborfenb, 5, 2)
        lay.addWidget(self._sb_tuborftim, 5, 3)
        lay.addWidget(self._lb_tuborftim, 5, 4)

        self.setStyleSheet('QLabel{qproperty-alignment: AlignCenter;}')


class PUModeSettingsDialog(SiriusDialog):
    """PU Mode settings dialog."""

    def __init__(self, parent=None, device='', prefix=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._inj_dev = SiriusPVName(device)
        self._inj_prefix = device.substitute(prefix=prefix)
        self.setObjectName('ASApp')
        self.setWindowTitle('Injection Controls - PU Mode Settings')
        self._setupUi()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        title = QLabel(
            '<h4>PU Mode Settings</h4>', self,
            alignment=Qt.AlignCenter)

        pvname = self._inj_prefix.substitute(propty='PUModeDeltaPosAng-SP')
        self._sb_dltposang = SiriusSpinbox(self, pvname)
        self._lb_dltposang = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_dltposang.showUnits = True

        pvname = self._inj_prefix.substitute(propty='PUModeDpKckrDlyRef-SP')
        self._sb_pudlyref = SiriusSpinbox(self, pvname)
        self._lb_pudlyref = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_pudlyref.showUnits = True

        pvname = self._inj_prefix.substitute(propty='PUModeDpKckrKick-SP')
        self._sb_pukick = SiriusSpinbox(self, pvname)
        self._lb_pukick = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_pukick.showUnits = True

        lay = QGridLayout(self)
        lay.addWidget(title, 0, 0, 1, 5)
        lay.addWidget(QLabel('Delta PosAng'), 1, 0)
        lay.addWidget(self._sb_dltposang, 1, 1)
        lay.addWidget(self._lb_dltposang, 1, 2)
        lay.addWidget(QLabel('DpKckr Delay Ref.'), 2, 0)
        lay.addWidget(self._sb_pudlyref, 2, 1)
        lay.addWidget(self._lb_pudlyref, 2, 2)
        lay.addWidget(QLabel('DpKckr Kick'), 3, 0)
        lay.addWidget(self._sb_pukick, 3, 1)
        lay.addWidget(self._lb_pukick, 3, 2)

        self.setStyleSheet('QLabel{qproperty-alignment: AlignCenter;}')
