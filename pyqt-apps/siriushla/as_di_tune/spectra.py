import os
from datetime import datetime
import time
from functools import partial as _part
import numpy as np

from qtpy.QtGui import QColor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, \
    QComboBox, QCheckBox, QLabel, QPushButton, QMenu, QSpacerItem, \
    QSizePolicy as QSzPlcy, QFileDialog
import qtawesome as qta
from pydm.widgets import PyDMWaveformPlot

from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.widgets import SiriusConnectionSignal
from .util import marker_color


class TuneSpectraView(PyDMWaveformPlot):
    """Tune Spectra View."""

    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section

        self.autoRangeX = True
        self.autoRangeY = True
        self.showXGrid = True
        self.showYGrid = True
        self.axisColor = QColor(0, 0, 0)
        self.backgroundColor = QColor(255, 255, 255)
        self.showLegend = False
        self.plotItem.showButtons()
        leftAxis = self.getAxis('left')
        leftAxis.setStyle(autoExpandTextSpace=False, tickTextWidth=25)

        self.x_channel = 'Tune'

        self.addChannel(
            y_channel='FAKE:SpectrumH', name='Tune H',
            redraw_mode=2, color='blue', lineWidth=2, lineStyle=Qt.SolidLine)
        self.curveH = self.curveAtIndex(0)
        self.curveH.x_channels = {
            'Tune': SiriusConnectionSignal(_PVName(
                self.section+'-Glob:DI-Tune-H:TuneFracArray-Mon').substitute(
                    prefix=self.prefix)),
            'Freq': SiriusConnectionSignal(_PVName(
                self.section+'-Glob:DI-Tune-H:FreqArray-Mon').substitute(
                    prefix=self.prefix))
        }
        self.curveH.setVisible(True)

        self.addChannel(
            y_channel='FAKE:SpectrumV', name='Tune V',
            redraw_mode=2, color='red', lineWidth=2, lineStyle=Qt.SolidLine)
        self.curveV = self.curveAtIndex(1)
        self.curveV.x_channels = {
            'Tune': SiriusConnectionSignal(_PVName(
                self.section+'-Glob:DI-Tune-V:TuneFracArray-Mon').substitute(
                    prefix=self.prefix)),
            'Freq': SiriusConnectionSignal(_PVName(
                self.section+'-Glob:DI-Tune-V:FreqArray-Mon').substitute(
                    prefix=self.prefix))
        }
        self.curveV.setVisible(True)

        if self.section == 'SI':
            self.maxRedrawRate = 5
            self.curveH_y_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-TuneProc-H:Trace-Mon').substitute(
                    prefix=self.prefix))
            self.curveH_y_channel.new_value_signal[np.ndarray].connect(
                self.receiveDataH)
            self.curveV_y_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-TuneProc-V:Trace-Mon').substitute(
                    prefix=self.prefix))
            self.curveV_y_channel.new_value_signal[np.ndarray].connect(
                self.receiveDataV)
            self.freqrevH_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-H:FreqRev-Mon').substitute(
                    prefix=self.prefix))
            self.freqrevV_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-V:FreqRev-Mon').substitute(
                    prefix=self.prefix))
            self.freqrevnH_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-H:FreqRevN-Mon').substitute(
                    prefix=self.prefix))
            self.freqrevnV_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-V:FreqRevN-Mon').substitute(
                    prefix=self.prefix))
            self.revnH_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-H:RevN-RB').substitute(
                    prefix=self.prefix))
            self.revnV_channel = SiriusConnectionSignal(_PVName(
                'SI-Glob:DI-Tune-V:RevN-RB').substitute(
                    prefix=self.prefix))

            self.markers = dict()
            ci = 2
            for ax in ['H', 'V']:
                self.markers[ax] = dict()
                for mtyp in ['', 'D']:
                    for i in range(1, 5):
                        si = str(i)
                        mark_dict = dict()
                        ch_enbl = SiriusConnectionSignal(_PVName(
                            'SI-Glob:DI-TuneProc-'+ax+':Enbl'+mtyp +
                            'Mark'+si+'-Sts').substitute(prefix=self.prefix))
                        ch_enbl.orientation = ax
                        ch_enbl.idx = si
                        ch_enbl.new_value_signal[int].connect(
                            self._update_markers_enable)
                        mark_dict['Enbl'] = ch_enbl

                        ch_x = SiriusConnectionSignal(_PVName(
                            'SI-Glob:DI-TuneProc-'+ax+':'+mtyp+'MarkX'+si +
                            'Disp-Mon').substitute(prefix=self.prefix))
                        ch_x.orientation = ax
                        ch_x.idx = si
                        ch_x.axis = 'X'
                        ch_x.new_value_signal[float].connect(
                            self._update_markers_value)
                        mark_dict['X'] = ch_x

                        ch_y = SiriusConnectionSignal(_PVName(
                            'SI-Glob:DI-TuneProc-'+ax+':'+mtyp+'MarkY'+si +
                            ('' if mtyp == '' else 'Disp')+'-Mon').substitute(
                                prefix=self.prefix))
                        ch_y.orientation = ax
                        ch_y.idx = si
                        ch_y.axis = 'Y'
                        ch_y.new_value_signal[float].connect(
                            self._update_markers_value)
                        mark_dict['Y'] = ch_y

                        self.addChannel(
                            y_channel='FAKE:'+mtyp+'MarkY',
                            x_channel='FAKE:'+mtyp+'MarkX',
                            name=mtyp+'Mark '+si, redraw_mode=2,
                            color=marker_color[mtyp+'Mark'][ax][si],
                            lineWidth=2, lineStyle=1,
                            symbol='o', symbolSize=10)
                        mark_dict['curve'] = self.curveAtIndex(ci)
                        ci += 1
                        self.markers[ax][mtyp+'Mark'+si] = mark_dict

    def toggleXChannel(self):
        """Toggle X channel between FreqArray and TuneFracArray."""
        self.x_channel = 'Tune' if 'Tune' in self.sender().currentText() \
            else 'Freq'
        if self.section == 'SI':
            for ori, markers in self.markers.items():
                for name, data in markers.items():
                    if data['Enbl'].connected:
                        curve = getattr(self, 'curve'+ori)
                        show = curve.isVisible() and data['Enbl'].value
                        self._update_marker_value(
                            data['X'].value, ori, name, 'X')
                        self._update_marker_value(
                            data['Y'].value, ori, name, 'Y')
                    else:
                        show = False
                    data['curve'].setVisible(show)

    def showTuneH(self, show):
        """Whether to show or not curve of Tune H."""
        self.curveH.setVisible(show)
        if self.section == 'SI':
            for name, data in self.markers['H'].items():
                if data['Enbl'].connected:
                    show = bool(show) and data['Enbl'].value
                else:
                    show = False
                data['curve'].setVisible(show)

    def showTuneV(self, show):
        """Whether to show or not curve of Tune V."""
        self.curveV.setVisible(show)
        if self.section == 'SI':
            for name, data in self.markers['V'].items():
                if data['Enbl'].connected:
                    show = bool(show) and data['Enbl'].value
                else:
                    show = False
                data['curve'].setVisible(show)

    def receiveDataH(self, data):
        """Update curve H."""
        self.curveH.receiveXWaveform(
            self.curveH.x_channels[self.x_channel].value)
        self.curveH.receiveYWaveform(data)

    def receiveDataV(self, data):
        """Update curve V."""
        self.curveV.receiveXWaveform(
            self.curveV.x_channels[self.x_channel].value)
        self.curveV.receiveYWaveform(data)

    def _update_markers_enable(self, value):
        address = self.sender().address
        mtyp = 'DMark' if 'DMark' in address else 'Mark'
        idx = self.sender().idx
        ori = self.sender().orientation
        curve = getattr(self, 'curve'+ori)
        show = (value and curve.isVisible())
        self.markers[ori][mtyp+idx]['curve'].setVisible(show)

    def _update_markers_value(self, value):
        address = self.sender().address
        mtyp = 'DMark' if 'DMark' in address else 'Mark'
        idx = self.sender().idx
        ori = self.sender().orientation
        axis = self.sender().axis
        self._update_marker_value(value, ori, mtyp+idx, axis)

    def _update_marker_value(self, value, ori, name, axis):
        func = getattr(self.markers[ori][name]['curve'],
                       'receive'+axis+'Waveform')
        if self.x_channel == 'Tune' and axis == 'X':
            fr_ch = getattr(self, 'freqrev'+ori+'_channel')
            fr = fr_ch.value
            fh_ch = getattr(self, 'freqrevn'+ori+'_channel')
            fh = fh_ch.value
            h_ch = getattr(self, 'revn'+ori+'_channel')
            h = h_ch.value
            if not fr or not h or not fh:
                self.markers[ori][name]['curve'].setVisible(False)
                return
            else:
                if getattr(self, 'curve'+ori).isVisible() and\
                        self.markers[ori][name]['Enbl'].value:
                    self.markers[ori][name]['curve'].setVisible(True)
            value = (value*1e6 - fh*1e3)/fr + h
        func(np.array([value, ]))


class TuneSpectraControls(QWidget):
    """Tune Spectra Controls."""

    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.section = section
        self._setupUi()

    def _setupUi(self):
        self.spectra = TuneSpectraView(self, self.prefix, self.section)

        lb_show_trace = QLabel('Show')
        self.cb_show_x = QCheckBox('H', self)
        self.cb_show_x.setStyleSheet('color: blue;')
        self.cb_show_x.setChecked(True)
        self.cb_show_x.stateChanged.connect(self.spectra.showTuneH)
        self.cb_show_y = QCheckBox('V', self)
        self.cb_show_y.setStyleSheet('color: red;')
        self.cb_show_y.setChecked(True)
        self.cb_show_y.stateChanged.connect(self.spectra.showTuneV)

        self.cb_choose_x = QComboBox(self)
        self.cb_choose_x.addItem('Tune Frac.')
        self.cb_choose_x.addItem('Frequency')
        self.cb_choose_x.currentIndexChanged.connect(
            self.spectra.toggleXChannel)
        self.cb_choose_x.currentIndexChanged.connect(
            self._toggle_registers_axis)

        # Registers
        self.registers = {i: None for i in range(4)}
        self.spectra.curveReg = [None, None, None, None]
        self.cb_reg = {i: QCheckBox(self) for i in range(4)}
        self.bt_reg = {i: QPushButton('Register '+str(i), self)
                       for i in range(4)}
        self.lb_reg = {i: QLabel('Empty') for i in range(4)}
        self.bt_save = {i: QPushButton(qta.icon('fa5s.save'), '', self)
                        for i in range(4)}
        self.colors = ['cyan', 'darkGreen', 'magenta', 'darkRed']
        self.registers_widget = QWidget()
        glay_reg = QGridLayout(self.registers_widget)
        shift = 2 if self.section == 'BO' else 18
        for i in range(4):
            # checks
            self.spectra.addChannel(
                y_channel='FAKE:Register'+str(i), name='Register '+str(i),
                redraw_mode=2, color=self.colors[i],
                lineWidth=2, lineStyle=Qt.SolidLine)
            self.spectra.curveReg[i] = self.spectra.curveAtIndex(i+shift)
            self.spectra.curveReg[i].setVisible(False)
            self.cb_reg[i].setStyleSheet(
                'min-width:1.2em; max-width:1.2em;'
                'min-height:1.29em; color:'+self.colors[i]+';')
            self.cb_reg[i].stateChanged.connect(_part(self._show_curve, i))
            glay_reg.addWidget(self.cb_reg[i], i, 0, alignment=Qt.AlignLeft)
            # buttons
            self.bt_reg[i].setStyleSheet('min-width:5em; max-width:5em;')
            self.bt_reg[i].setMenu(QMenu())
            self.bt_reg[i].menu().addAction(
                'Save Tune H', _part(self._registerData, i, 'H'))
            self.bt_reg[i].menu().addAction(
                'Save Tune V', _part(self._registerData, i, 'V'))
            self.bt_reg[i].menu().addAction(
                'Clear', _part(self._clear_register, i))
            glay_reg.addWidget(self.bt_reg[i], i, 1, alignment=Qt.AlignLeft)
            # label
            self.lb_reg[i].setMouseTracking(True)
            self.lb_reg[i].setTextInteractionFlags(Qt.TextEditorInteraction)
            self.lb_reg[i].setStyleSheet(
                'min-height:1.29em; min-width: 20em; max-width: 20em;')
            glay_reg.addWidget(self.lb_reg[i], i, 2, alignment=Qt.AlignLeft)
            glay_reg.addItem(
                QSpacerItem(i, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), i, 3)
            # save button
            self.bt_save[i].clicked.connect(_part(self._export_data, i))
            glay_reg.addWidget(self.bt_save[i], i, 4, alignment=Qt.AlignRight)

        self.pb_showregs = QPushButton('^', self)
        self.pb_showregs.setObjectName('showregs')
        self.pb_showregs.setToolTip('Hide registers')
        self.pb_showregs.setStyleSheet(
            '#showregs{min-width:1em;max-width:1em;}')
        self.pb_showregs.released.connect(self._handle_registers_vis)

        hbox_ctrls = QHBoxLayout()
        hbox_ctrls.setContentsMargins(0, 0, 0, 0)
        hbox_ctrls.setSpacing(6)
        hbox_ctrls.addWidget(lb_show_trace, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.cb_show_x, alignment=Qt.AlignLeft)
        hbox_ctrls.addWidget(self.cb_show_y, alignment=Qt.AlignLeft)
        hbox_ctrls.addStretch()
        hbox_ctrls.addWidget(QLabel('X Axis: '), alignment=Qt.AlignRight)
        hbox_ctrls.addWidget(self.cb_choose_x, alignment=Qt.AlignRight)
        hbox_ctrls.addItem(QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored))
        hbox_ctrls.addWidget(self.pb_showregs, alignment=Qt.AlignLeft)

        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(10, 6, 6, 6)
        lay.addWidget(self.spectra)
        lay.addLayout(hbox_ctrls)
        lay.addWidget(self.registers_widget)

    def _registerData(self, idx, tune):
        curve = self.spectra.curveH if tune == 'H' else self.spectra.curveV
        latest_freq = curve.x_channels['Freq'].value
        latest_tune = curve.x_channels['Tune'].value
        self.registers[idx] = [latest_tune, latest_freq, curve.latest_y]
        self.lb_reg[idx].setText(
            'Tune '+tune+' at '+time.strftime(
                '%d/%m/%Y %H:%M:%S', time.localtime(time.time())))
        self._show_curve(idx, self.cb_reg[idx].checkState())

    def _clear_register(self, idx):
        self._show_curve(idx, False)
        self.lb_reg[idx].setText('Empty')
        self.registers[idx] = None

    def _show_curve(self, i, show):
        if not self.registers[i]:
            self.spectra.curveReg[i].receiveXWaveform([])
            self.spectra.curveReg[i].receiveYWaveform([])
            self.spectra.curveReg[i].redrawCurve()
            return
        if show:
            self.spectra.curveReg[i].receiveXWaveform(
                self.registers[i][self.cb_choose_x.currentIndex()])
            self.spectra.curveReg[i].receiveYWaveform(self.registers[i][2])
            self.spectra.curveReg[i].redrawCurve()
            self.spectra.curveReg[i].setVisible(True)
        else:
            self.spectra.curveReg[i].setVisible(False)

    def _toggle_registers_axis(self, idx):
        for i in range(4):
            if self.registers[i] is None:
                continue
            self.spectra.curveReg[i].receiveXWaveform(self.registers[i][idx])
            self.spectra.curveReg[i].receiveYWaveform(self.registers[i][2])
            self.spectra.curveReg[i].redrawCurve()

    def _export_data(self, idx):
        if not self.registers[idx]:
            return

        home = os.path.expanduser('~')
        folder_month = datetime.now().strftime('%Y-%m')
        folder_day = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(
            home, 'mounts', 'screens-iocs', folder_month, folder_day)
        if not os.path.exists(path):
            os.makedirs(path)
        fn, _ = QFileDialog.getSaveFileName(self, 'Save as...', path, '*.txt')
        if not fn:
            return False
        if not fn.endswith('.txt'):
            fn += '.txt'

        data = np.array([self.registers[idx][0], self.registers[idx][1]]).T
        np.savetxt(fn, data)

    def _handle_registers_vis(self):
        vis = self.registers_widget.isVisible()
        text = 'v' if vis else '^'
        ttip = 'Show' if vis else 'Hide'
        self.pb_showregs.setText(text)
        self.pb_showregs.setToolTip(ttip+' registers')
        self.registers_widget.setVisible(not vis)
        self.spectra.adjustSize()
        self.adjustSize()
