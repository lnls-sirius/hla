"""Booster Ramp Control HLA: Ramp Parameters Module."""

from functools import partial as _part

from threading import Thread as _Thread

import numpy as np
import math as _math

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, QSpacerItem, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QCheckBox, \
    QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy as QSzPlcy, \
    QHeaderView, QUndoCommand, QAbstractItemView, QMenu, QMessageBox
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE
from siriuspy.search import MASearch as _MASearch
from siriuspy.ramp import ramp, exceptions
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.ramp.conn import ConnSOFB as _ConnSOFB

from siriushla.widgets import SiriusFigureCanvas
from siriushla.bo_ap_ramp.auxiliar_classes import \
    InsertNormalizedConfig as _InsertNormConfig, \
    DeleteNormalizedConfig as _DeleteNormConfig, \
    DuplicateNormConfig as _DuplicateNormConfig, \
    SpinBoxDelegate as _SpinBoxDelegate, \
    CustomTableWidgetItem as _CustomTableWidgetItem, \
    ChooseMagnetsToPlot as _ChooseMagnetsToPlot, \
    MyDoubleSpinBox as _MyDoubleSpinBox, \
    MyTableWidget as _MyTableWidget
from siriushla.bo_ap_ramp.bonormalized_edit import BONormEdit as _BONormEdit


_flag_stack_next_command = True
_flag_stacking = False


class ConfigParameters(QGroupBox):
    """Widget to set and monitor ramp parametes."""

    def __init__(self, parent=None, prefix='',
                 ramp_config=None, undo_stack=None,
                 tunecorr_configname='', chromcorr_configname=''):
        """Initialize object."""
        super().__init__('Ramping Parameters: ', parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self._setupUi()

    def _setupUi(self):
        my_lay = QHBoxLayout(self)
        my_lay.setContentsMargins(0, 0, 0, 0)
        my_lay.setSpacing(0)
        self.dip_ramp = DipoleRamp(
            self, self.prefix, self.ramp_config, self._undo_stack)
        self.mult_ramp = MultipolesRamp(
            self, self.prefix, self.ramp_config, self._undo_stack,
            self._tunecorr_configname, self._chromcorr_configname)
        self.rf_ramp = RFRamp(
            self, self.prefix, self.ramp_config, self._undo_stack)
        my_lay.addWidget(self.dip_ramp)
        my_lay.addWidget(self.mult_ramp)
        my_lay.addWidget(self.rf_ramp)
        my_lay.setStretch(0, 30)
        my_lay.setStretch(1, 30)
        my_lay.setStretch(2, 30)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.setTitle('Ramping Parameters: ' + self.ramp_config.name)
        self.dip_ramp.handleLoadRampConfig(self.ramp_config)
        self.mult_ramp.handleLoadRampConfig(self.ramp_config)
        self.rf_ramp.handleLoadRampConfig(self.ramp_config)

    def updateOpticsAdjustSettings(self, tune_cname, chrom_cname):
        """Update settings."""
        self._tunecorr_configname = tune_cname
        self._chromcorr_configname = chrom_cname
        self.mult_ramp.updateOpticsAdjustSettings(tune_cname, chrom_cname)

    @Slot(str)
    def getPlotUnits(self, units):
        """Change units used in plot."""
        self.dip_ramp.plot_unit = units
        self.dip_ramp.updateGraph(update_axis=True)
        self.mult_ramp.plot_unit = units
        self.mult_ramp.updateGraph(update_axis=True)


class DipoleRamp(QWidget):
    """Widget to set and monitor dipole ramp."""

    updateDipoleRampSignal = Signal()
    applyChanges2MachineSignal = Signal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self.plot_unit = 'Strengths'
        self._setupUi()
        self.setObjectName('DipoleRampWidget')

    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setAlignment(Qt.AlignTop)
        self.graphview = QWidget()
        self.set_psdelay_and_nrpoints = QFormLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupPSDelayAndWfmNrPoints()
        self._setupTable()

        lay_v = QVBoxLayout()
        self.l_rampupv = QLabel('RmpU 0 [GeV/s]', self)
        self.l_rampupv.setStyleSheet("""
            min-width:10.5em;max-width:10.5em;
            qproperty-alignment: AlignRight;""")
        self.l_rampdownv = QLabel('RmpD 0 [GeV/s]', self)
        self.l_rampdownv.setStyleSheet("""
            min-width:10.5em;max-width:10.5em;
            qproperty-alignment: AlignRight;""")
        lay_v.addWidget(self.l_rampupv)
        lay_v.addWidget(self.l_rampdownv)

        # self.label_anom = QLabel('', self)
        # self.label_anom.setStyleSheet("""
        #     min-height:1.55em;max-height:1.55em;""")
        # self.pb_anom = QPushButton('?', self)
        # self.pb_anom.setVisible(False)
        # self.pb_anom.setStyleSheet("""
        #     background-color:red;min-width:1.55em;max-width:1.55em;""")
        # self.pb_anom.clicked.connect(self._showAnomaliesPopup)
        # lay_anom = QHBoxLayout()
        # lay_anom.addWidget(self.label_anom)
        # lay_anom.addWidget(self.pb_anom)

        self.label_exclim = QLabel('', self)
        self.label_exclim.setStyleSheet("""
            min-height:1.55em;max-height:1.55em;""")
        self.pb_exclim = QPushButton('?', self)
        self.pb_exclim.setVisible(False)
        self.pb_exclim.setStyleSheet("""
            background-color:red;min-width:1.55em;max-width:1.55em;""")
        self.pb_exclim.clicked.connect(self._showExcLimPopup)
        lay_exclim = QHBoxLayout()
        lay_exclim.addWidget(self.label_exclim)
        lay_exclim.addWidget(self.pb_exclim)

        self.bt_apply2machine = QPushButton('Apply Changes to Machine', self)
        self.bt_apply2machine.clicked.connect(
            self.applyChanges2MachineSignal.emit)

        label = QLabel('<h4>Dipole Ramp</h4>', self, alignment=Qt.AlignCenter)
        label.setStyleSheet("""
            min-height:1.55em; max-height:1.55em;
            min-width:30em; max-width:30em;""")
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graphview, 1, 0, 1, 2)
        glay.addLayout(self.set_psdelay_and_nrpoints, 2, 0,
                       alignment=Qt.AlignLeft)
        glay.addLayout(lay_v, 2, 1, alignment=Qt.AlignRight)
        glay.addWidget(self.table, 3, 0, 1, 2)
        glay.addLayout(lay_exclim, 4, 0, 1, 2, alignment=Qt.AlignCenter)
        # glay.addLayout(lay_anom, 4, 0, 1, 2, alignment=Qt.AlignCenter)
        glay.addWidget(self.bt_apply2machine, 6, 0, 1, 2,
                       alignment=Qt.AlignRight)

    def _setupGraph(self):
        self.graph = SiriusFigureCanvas(Figure())
        self.graph.setObjectName('DipoleGraph')
        self.graph.setStyleSheet("""
            #DipoleGraph{min-width:30em;min-height:18em;max-height:18em;}""")
        self.graph.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.graph.figure.set_tight_layout({'pad': .0})
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.line, = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], marker='o', c='#787878')
        self.m_ej, = self.ax.plot([0], [0], marker='o', c='#787878')

        self.toolbar = NavigationToolbar(self.graph, self)
        self.toolbar.setObjectName('toolbar')
        self.toolbar.setStyleSheet("""
            #toolbar{min-height:2em; max-height:2em;}""")

        lay = QVBoxLayout()
        lay.addWidget(self.graph)
        lay.addWidget(self.toolbar)
        self.graphview.setLayout(lay)

    def _setupPSDelayAndWfmNrPoints(self):
        label_psdelay = QLabel('PS Delay [ms]:', self,
                               alignment=Qt.AlignVCenter)
        self.sb_psdelay = _MyDoubleSpinBox(self)
        self.sb_psdelay.setMinimum(0)
        self.sb_psdelay.setMaximum(490)
        self.sb_psdelay.setDecimals(6)
        self.sb_psdelay.setSingleStep(0.000008)
        self.sb_psdelay.editingFinished.connect(self._handleChangePSDelay)

        label_nrpoints = QLabel('# of points:', self,
                                alignment=Qt.AlignVCenter)
        self.sb_nrpoints = _MyDoubleSpinBox(self)
        self.sb_nrpoints.setMinimum(1)
        self.sb_nrpoints.setMaximum(MAX_WFMSIZE)
        self.sb_nrpoints.setDecimals(0)
        self.sb_nrpoints.setSingleStep(1)
        self.sb_nrpoints.editingFinished.connect(self._handleChangeNrPoints)

        self.set_psdelay_and_nrpoints.addRow(label_psdelay, self.sb_psdelay)
        self.set_psdelay_and_nrpoints.addRow(label_nrpoints, self.sb_nrpoints)

    def _setupTable(self):
        self.table_map = {
            'rows': {0: 'Start',
                     1: 'RampUp1-Start',
                     2: 'Injection',
                     3: 'RampUp2-Start',
                     4: 'Ejection',
                     5: 'RampDown-Start',
                     6: 'RampDown-Stop',
                     7: 'Stop'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: 'E [GeV]',
                        3: 'Index'}}
        self.table.setObjectName('DipoleTable')
        self.table.setStyleSheet("""
            #DipoleTable{
                min-width: 30em;
                min-height: 16.2em; max-height: 16.2em;
            }
            QHeaderView::section {
                background-color: #1F64FF;
            }
            QTableWidget {
                background-color: #D3E1FF;
                gridline-color: #003065;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #1F64FF;
            }""")
        self.table.setRowCount(max(self.table_map['rows'].keys())+1)
        self.table.setColumnCount(max(self.table_map['columns'].keys())+1)
        self.table.horizontalHeader().setStyleSheet("""
            min-height:1.55em; max-height:1.55em;""")
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())
        self.table.setSizePolicy(QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)

        for row, vlabel in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            np_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            if vlabel in ['Injection', 'Ejection']:
                label_item.setBackground(QBrush(QColor(220, 220, 220)))
                e_item.setBackground(QBrush(QColor(220, 220, 220)))
                np_item.setBackground(QBrush(QColor(220, 220, 220)))

            if vlabel in ['Start', ]:
                t_item.setFlags(Qt.ItemIsEnabled)
                e_item.setBackground(QBrush(QColor("white")))
            elif vlabel in ['Injection', 'Ejection', 'Stop']:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setFlags(Qt.ItemIsEnabled)
            else:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setBackground(QBrush(QColor("white")))

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, e_item)
            self.table.setItem(row, 3, np_item)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(int, int)
    def _handleCellChanged(self, row, column):
        if self.ramp_config is None:
            return

        try:
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            if self.table_map['rows'][row] == 'Start':
                old_value = self.ramp_config.ps_ramp_start_energy
                self.ramp_config.ps_ramp_start_energy = new_value

            elif self.table_map['rows'][row] == 'RampUp1-Start':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampup1_start_time
                    self.ramp_config.ps_ramp_rampup1_start_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampup1_start_energy
                    self.ramp_config.ps_ramp_rampup1_start_energy = new_value

            elif self.table_map['rows'][row] == 'Injection':
                old_value = self.ramp_config.ti_params_injection_time
                self.ramp_config.ti_params_injection_time = new_value

            elif self.table_map['rows'][row] == 'RampUp2-Start':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampup2_start_time
                    self.ramp_config.ps_ramp_rampup2_start_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampup2_start_energy
                    self.ramp_config.ps_ramp_rampup2_start_energy = new_value

            elif self.table_map['rows'][row] == 'Ejection':
                old_value = self.ramp_config.ti_params_ejection_time
                self.ramp_config.ti_params_ejection_time = new_value

            elif self.table_map['rows'][row] == 'RampDown-Start':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampdown_start_time
                    self.ramp_config.ps_ramp_rampdown_start_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampdown_start_energy
                    self.ramp_config.ps_ramp_rampdown_start_energy = new_value

            elif self.table_map['rows'][row] == 'RampDown-Stop':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampdown_stop_time
                    self.ramp_config.ps_ramp_rampdown_stop_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampdown_stop_energy
                    self.ramp_config.ps_ramp_rampdown_stop_energy = new_value

            elif self.table_map['rows'][row] == 'Stop':
                old_value = self.ramp_config.ps_ramp_duration
                self.ramp_config.ps_ramp_duration = new_value

        except exceptions.RampInvalidDipoleWfmParms as e:
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            self._verifyWarnings()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _UndoRedoTableCell(
                    self.table, row, column, old_value, new_value,
                    'set dipole table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @Slot()
    def _handleChangePSDelay(self):
        """Handle change ps delay."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ti_params_ps_ramp_delay
        new_value = self.sb_psdelay.value()
        if new_value == old_value:
            # Avoid several updates on Enter or spinbox focusOutEvent.
            # It is necessary due to several emits of editingFinished signal.
            return

        try:
            self.ramp_config.ti_params_ps_ramp_delay = new_value
        except exceptions.RampInvalidDipoleWfmParms as e:
            self.updatePSDelay()
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _UndoRedoSpinbox(
                    self.sb_psdelay, old_value, new_value,
                    'set PS ramp delay to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @Slot()
    def _handleChangeNrPoints(self):
        """Handle change waveform number of points."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ps_ramp_wfm_nrpoints
        new_value = int(self.sb_nrpoints.value())
        if new_value == old_value:
            # Avoid several updates on Enter or spinbox focusOutEvent.
            # It is necessary due to several emits of editingFinished signal.
            return

        try:
            self.ramp_config.ps_ramp_wfm_nrpoints = new_value
        except exceptions.RampInvalidDipoleWfmParms as e:
            self.updateWfmNrPoints()
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _UndoRedoSpinbox(
                    self.sb_nrpoints, old_value, new_value,
                    'set dipole ramp number of points to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def _verifyWarnings(self):
        # if len(self.ramp_config.ps_waveform_anomalies) > 0:
        #     self.label_anom.setText('<h6>Caution: there are anomalies '
        #                             'in the waveforms.</h6>')
        #     self.pb_anom.setVisible(True)
        # else:
        #     self.label_anom.setText('')
        #     self.pb_anom.setVisible(False)

        if 'BO-Fam:MA-B' in self.ramp_config.ps_waveform_manames_exclimits:
            self.label_exclim.setText('<h6>Waveform is exceeding current '
                                      'limits.</h6>')
            self.pb_exclim.setVisible(True)
        else:
            self.label_exclim.setText('')
            self.pb_exclim.setVisible(False)

    def _showAnomaliesPopup(self):
        text = 'Caution to the following anomalies: \n'
        # for anom in self.ramp_config.ps_waveform_anomalies:
        #     text += anom + '\n'
        QMessageBox.warning(self, 'Caution', text, QMessageBox.Ok)

    def _showExcLimPopup(self):
        manames_exclimits = self.ramp_config.ps_waveform_manames_exclimits
        if 'BO-Fam:MA-B' in manames_exclimits:
            text = 'The waveform of the following magnets\n' \
                   'are exceeding current limits:\n' \
                   '    - BO-Fam:MA-B'
        QMessageBox.warning(self, 'Warning', text, QMessageBox.Ok)

    def updateGraph(self, update_axis=False):
        """Update and redraw graph when ramp_config is loaded."""
        if self.ramp_config is None:
            return

        xdata = self.ramp_config.ps_waveform_get_times()
        if self.plot_unit == 'Strengths':
            self.ax.set_ylabel('E [GeV]')
            ydata = self.ramp_config.ps_waveform_get_strengths('BO-Fam:MA-B')
        elif self.plot_unit == 'Currents':
            self.ax.set_ylabel('Current [A]')
            ydata = self.ramp_config.ps_waveform_get_currents('BO-Fam:MA-B')
        self.line.set_xdata(xdata)
        self.line.set_ydata(ydata)
        if update_axis:
            self.ax.set_xlim(min(xdata), max(xdata))
            self.ax.set_ylim(min(ydata)*0.95, max(ydata)*1.05)

        if self.plot_unit == 'Strengths':
            func = self.ramp_config.ps_waveform_interp_strengths
        else:
            func = self.ramp_config.ps_waveform_interp_currents

        markers_time = self.ramp_config.ps_ramp_times
        self.markers.set_xdata(markers_time)
        self.markers.set_ydata(func('BO-Fam:MA-B', markers_time))

        inj_marker_time = self.ramp_config.ti_params_injection_time
        self.m_inj.set_xdata(inj_marker_time)
        self.m_inj.set_ydata(func('BO-Fam:MA-B', inj_marker_time))

        ej_marker_time = self.ramp_config.ti_params_ejection_time
        self.m_ej.set_xdata(ej_marker_time)
        self.m_ej.set_ydata(func('BO-Fam:MA-B', ej_marker_time))

        self.graph.figure.canvas.draw()
        self.graph.figure.canvas.flush_events()

    def updatePSDelay(self):
        """Update PS delay when ramp_config is loaded."""
        self.sb_nrpoints.setValue(self.ramp_config.ti_params_ps_ramp_delay)

    def updateWfmNrPoints(self):
        """Update waveform number of points when ramp_config is loaded."""
        self.sb_nrpoints.setValue(self.ramp_config.ps_ramp_wfm_nrpoints)

    def updateTable(self):
        """Update and rebuild table when ramp_config is loaded."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for row, label in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)  # time column
            e_item = self.table.item(row, 2)  # energy column
            if label == 'Start':
                time = 0.0
                energy = self.ramp_config.ps_ramp_start_energy
            elif label == 'RampUp1-Start':
                time = self.ramp_config.ps_ramp_rampup1_start_time
                energy = self.ramp_config.ps_ramp_rampup1_start_energy
            elif label == 'Injection':
                time = self.ramp_config.ti_params_injection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label == 'RampUp2-Stop':
                time = self.ramp_config.ps_ramp_rampup2_start_time
                energy = self.ramp_config.ps_ramp_rampup2_start_energy
            elif label == 'Ejection':
                time = self.ramp_config.ti_params_ejection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label == 'RampDown-Start':
                time = self.ramp_config.ps_ramp_rampdown_start_time
                energy = self.ramp_config.ps_ramp_rampdown_start_energy
            elif label == 'RampDown-Stop':
                time = self.ramp_config.ps_ramp_rampdown_stop_time
                energy = self.ramp_config.ps_ramp_rampdown_stop_energy
            elif label == 'Stop':
                time = self.ramp_config.ps_ramp_duration
                energy = self.ramp_config.ps_ramp_start_energy
            t_item.setData(Qt.DisplayRole, '{0:.3f}'.format(time))
            e_item.setData(Qt.DisplayRole, '{0:.4f}'.format(energy))

        for row in self.table_map['rows'].keys():
            D = self.ramp_config.ps_ramp_duration
            N = self.ramp_config.ps_ramp_wfm_nrpoints
            T = float(self.table.item(row, 1).data(Qt.DisplayRole))
            value = round(T*N/D)
            item = self.table.item(row, 3)  # index column
            item.setData(Qt.DisplayRole, str(value))

        self.l_rampupv.setText('RmpU {: .3f} [GeV/s]'.format(
                               self.ramp_config.ps_ramp_rampup2_slope))
        self.l_rampdownv.setText('RmpD {: .3f} [GeV/s]'.format(
                                 self.ramp_config.ps_ramp_rampdown_slope))

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.updateGraph(update_axis=True)
        self.updatePSDelay()
        self.updateWfmNrPoints()
        self.updateTable()
        self._verifyWarnings()


class MultipolesRamp(QWidget):
    """Widget to set and monitor multipoles ramp."""

    updateMultipoleRampSignal = Signal()
    updateOptAdjSettingsSignal = Signal(str, str)
    applyChanges2MachineSignal = Signal()

    def __init__(self, parent=None, prefix='',
                 ramp_config=None, undo_stack=None,
                 tunecorr_configname='', chromcorr_configname=''):
        """Initialize object."""
        super().__init__(parent)
        self.setObjectName('BOApp')
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack

        self.normalized_configs = list()
        self.bonorm_edit_dict = dict()

        self._magnets_to_plot = []
        self.plot_unit = 'Strengths'

        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self._conn_sofb = _ConnSOFB(self.prefix)

        self._manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})
        self._manames.remove('BO-Fam:MA-B')
        self._aux_magnets = dict()
        t = _Thread(target=self._createMagnets, daemon=True)
        t.start()

        self._setupUi()
        self.setObjectName('MultipolesRampWidget')

    @property
    def manames(self):
        return self._manames

    def _createMagnets(self):
        for ma in self.manames:
            self._aux_magnets[ma] = _Magnet(ma)
        self._aux_magnets['BO-Fam:MA-B'] = _Magnet('BO-Fam:MA-B')

    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setAlignment(Qt.AlignTop)
        self.graphview = QWidget()
        self.table = _MyTableWidget(self, self._showNormConfigMenu)
        self.bt_insert = QPushButton('Insert Normalized Config', self)
        self.bt_delete = QPushButton('Delete Normalized Config', self)

        self._setupGraph()
        self._setupTable()
        self.bt_insert.clicked.connect(self._showInsertNormConfigPopup)
        self.bt_delete.clicked.connect(self._showDeleteNormConfigPopup)

        self.label_exclim = QLabel('', self)
        self.pb_exclim = QPushButton('?', self)
        self.pb_exclim.setVisible(False)
        self.pb_exclim.setStyleSheet("""
            background-color: red;
            min-width:1.55em; max-width:1.55em;""")
        self.pb_exclim.clicked.connect(self._showExcLimPopup)
        lay_exclim = QHBoxLayout()
        lay_exclim.addItem(
            QSpacerItem(2, 2, QSzPlcy.Expanding, QSzPlcy.Ignored))
        lay_exclim.addWidget(self.label_exclim)
        lay_exclim.addWidget(self.pb_exclim)
        lay_exclim.addItem(
            QSpacerItem(2, 2, QSzPlcy.Expanding, QSzPlcy.Ignored))

        self.bt_apply2machine = QPushButton('Apply Changes to Machine', self)
        self.bt_apply2machine.clicked.connect(
            self.applyChanges2MachineSignal.emit)

        label = QLabel('<h4>Multipoles Ramp</h4>', self)
        label.setStyleSheet("""
            min-height: 1.55em; max-height: 1.55em;""")
        glay.addWidget(label, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        glay.addWidget(self.graphview, 1, 0, 1, 2)
        glay.addWidget(self.bt_insert, 2, 0)
        glay.addWidget(self.bt_delete, 2, 1)
        glay.addWidget(self.table, 3, 0, 1, 2)
        glay.addLayout(lay_exclim, 4, 0, 1, 2)
        glay.addWidget(self.bt_apply2machine, 5, 0, 1, 2,
                       alignment=Qt.AlignRight)

    def _setupGraph(self):
        self.graph = SiriusFigureCanvas(Figure())
        self.graph.setObjectName('MultipolesGraph')
        self.graph.setStyleSheet("""
            #MultipolesGraph{
                min-width:30em;
                min-height:18em;max-height:18em;
            }""")
        self.graph.setSizePolicy(QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)
        self.graph.figure.set_tight_layout({'pad': .0})
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.lines = dict()
        for maname in self.manames:
            self.lines[maname], = self.ax.plot([0], [0], '-b')
        self.m_inj, = self.ax.plot([0], [0], ls='', marker='o', c='#787878')
        self.m_ej, = self.ax.plot([0], [0], ls='', marker='o', c='#787878')

        self.toolbar = NavigationToolbar(self.graph, self)
        self.toolbar.setObjectName('toolbar')
        self.toolbar.setStyleSheet("""
            #toolbar{min-height:2em; max-height:2em;}""")

        hlay_pb = QHBoxLayout()
        self.pb_maname = QPushButton('Choose magnets to plot... ', self)
        self.pb_maname.clicked.connect(self._showChooseMagnetToPlot)
        hlay_pb.addItem(
            QSpacerItem(20, 20, QSzPlcy.Expanding, QSzPlcy.Ignored))
        hlay_pb.addWidget(self.pb_maname)
        hlay_pb.addItem(
            QSpacerItem(20, 20, QSzPlcy.Expanding, QSzPlcy.Ignored))

        lay = QGridLayout()
        lay.addWidget(self.graph, 0, 0, 1, 2)
        lay.addWidget(self.toolbar, 1, 0)
        lay.addLayout(hlay_pb, 2, 0, 1, 2)
        self.graphview.setLayout(lay)

    def _setupTable(self):
        self.table_map = {
            'rows': {0: 'Injection',
                     len(self.normalized_configs)+1: 'Ejection'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: 'E [GeV]',
                        3: 'Index'}}
        idx = 1
        normalized_config_rows = list()
        for config in self.normalized_configs:
            self.table_map['rows'][idx] = config[1]
            normalized_config_rows.append(idx)
            idx += 1

        self.table.setObjectName('MultipoleTable')
        self.table.setStyleSheet("""
            #MultipoleTable{
                min-width: 30em;
                min-height: 22.5em;
            }
            QHeaderView::section {
                background-color: #FF7C52;
            }
            QTableWidget {
                background-color: #FFDDD2;
                gridline-color: #BD0000;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #FF7C52;
            }""")
        self.table.setSizePolicy(QSzPlcy.MinimumExpanding,
                                 QSzPlcy.MinimumExpanding)
        self.table.verticalHeader().setStyleSheet("""
            min-width:1.55em; max-width:1.55em;""")
        self.table.horizontalHeader().setStyleSheet("""
            min-height:1.55em; max-height:1.55em;""")
        self.table.setRowCount(2+len(self.normalized_configs))
        self.table.setColumnCount(max(self.table_map['columns'].keys())+1)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setMaximumSectionSize(320)
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.Interactive)
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())

        for row, vlabel in self.table_map['rows'].items():
            label_item = _CustomTableWidgetItem(vlabel)
            t_item = _CustomTableWidgetItem('0')
            e_item = _CustomTableWidgetItem('0')
            np_item = _CustomTableWidgetItem('0')

            np_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            if vlabel in ['Injection', 'Ejection']:
                label_item.setFlags(Qt.ItemIsEnabled)
                label_item.setBackground(QBrush(QColor(220, 220, 220)))
                t_item.setFlags(Qt.ItemIsEnabled)
                t_item.setBackground(QBrush(QColor(220, 220, 220)))
                np_item.setBackground(QBrush(QColor(220, 220, 220)))
                e_item.setBackground(QBrush(QColor(220, 220, 220)))
            else:
                label_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                label_item.setBackground(QBrush(QColor("white")))
                t_item.setBackground(QBrush(QColor("white")))

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, e_item)
            self.table.setItem(row, 3, np_item)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.table.cellChanged.connect(self._handleCellChanged)

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)

    def _getNormalizedConfigs(self):
        if self.ramp_config is None:
            return
        self.normalized_configs = self.ramp_config.ps_normalized_configs

    def _sortTable(self):
        self.table.sortByColumn(1, Qt.AscendingOrder)
        for row in range(self.table.rowCount()):
            self.table_map['rows'][row] = self.table.item(row, 0).text()

    def _handleCellChanged(self, row, column):
        nconfig_name = self.table.item(row, 0).data(Qt.DisplayRole)
        try:
            old_value = [t for t, n in self.normalized_configs
                         if n == nconfig_name]
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            self.ramp_config.ps_normalized_configs_change_time(
                nconfig_name, new_value)
        except exceptions.RampInvalidNormConfig as e:
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateMultipoleRampSignal.emit()
            self._verifyWarnings()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _UndoRedoTableCell(
                    self.table, row, column, old_value[0], new_value,
                    'set multipole table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

            if nconfig_name in self.bonorm_edit_dict.keys():
                energy = float(self.table.item(row, 2).data(Qt.DisplayRole))
                w = self.bonorm_edit_dict[nconfig_name]
                w.updateEnergy(energy)

    def _showInsertNormConfigPopup(self):
        self._insertConfigPopup = _InsertNormConfig(self, self.ramp_config)
        self._insertConfigPopup.insertConfig.connect(
            self._handleInsertNormConfig)
        self._insertConfigPopup.open()

    def _showDuplicateNormConfigPopup(self, nconfig_name):
        data = self.ramp_config[nconfig_name].value
        self._duplicConfigPopup = _DuplicateNormConfig(self, data)
        self._duplicConfigPopup.insertConfig.connect(
            self._handleInsertNormConfig)
        self._duplicConfigPopup.open()

    @Slot(list)
    def _handleInsertNormConfig(self, config):
        try:
            self.ramp_config.ps_normalized_configs_insert(
                time=config[0], name=config[1], nconfig=config[2])
        except exceptions.RampError as e:
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.handleLoadRampConfig()
            self.updateMultipoleRampSignal.emit()

    def _showDeleteNormConfigPopup(self, selected_row=None):
        self._deleteConfigPopup = _DeleteNormConfig(
            self, self.table_map, selected_row)
        self._deleteConfigPopup.deleteConfig.connect(
            self._handleDeleteNormConfig)
        self._deleteConfigPopup.open()

    @Slot(str)
    def _handleDeleteNormConfig(self, config):
        self.ramp_config.ps_normalized_configs_delete(config)
        self.handleLoadRampConfig()
        self.updateMultipoleRampSignal.emit()

    def _showChooseMagnetToPlot(self):
        self._chooseMagnetsPopup = _ChooseMagnetsToPlot(
            self, self.manames, self._magnets_to_plot)
        self._chooseMagnetsPopup.choosePlotSignal.connect(
            self._handleChooseMagnetToPlot)
        self._chooseMagnetsPopup.open()

    @Slot(list)
    def _handleChooseMagnetToPlot(self, maname_list):
        self._magnets_to_plot = maname_list
        self.updateGraph(update_axis=True)

    def _showNormConfigMenu(self, pos):
        if self.ramp_config is None:
            return

        item = self.table.itemAt(pos)
        if not item:
            return
        row = item.row()
        nconfig_name = self.table_map['rows'][row]
        if nconfig_name in ['Injection', 'Ejection']:
            return
        energy = float(self.table.item(row, 2).data(Qt.DisplayRole))

        menu = QMenu()
        edit_act = menu.addAction('Edit')
        edit_act.triggered.connect(
            _part(self._showEditNormConfigWindow, nconfig_name, energy))

        duplic_act = menu.addAction('Duplicate')
        duplic_act.triggered.connect(
            _part(self._showDuplicateNormConfigPopup, nconfig_name))

        delete_act = menu.addAction('Delete')
        delete_act.triggered.connect(
            _part(self._showDeleteNormConfigPopup, row))

        menu.exec_(self.table.mapToGlobal(pos))

    def _showEditNormConfigWindow(self, nconfig_name, energy):
        for maname in self.manames:
            if maname not in self._aux_magnets.keys():
                QMessageBox.warning(
                    self, 'Wait...',
                    'Loading magnets data... \n'
                    'Wait a moment and try again.', QMessageBox.Ok)
                return

        if nconfig_name in self.bonorm_edit_dict.keys():
            w = self.bonorm_edit_dict[nconfig_name]
        else:
            w = _BONormEdit(parent=self, prefix=self.prefix,
                            norm_config=self.ramp_config[nconfig_name],
                            energy=energy, magnets=self._aux_magnets,
                            conn_sofb=self._conn_sofb,
                            tunecorr_configname=self._tunecorr_configname,
                            chromcorr_configname=self._chromcorr_configname)
            w.normConfigChanged.connect(self.handleNormConfigsChanged)
            self.updateOptAdjSettingsSignal.connect(w.updateSettings)
            self.bonorm_edit_dict[nconfig_name] = w
        if w.isHidden():
            w.show()
        elif w.isMinimized():
            w.showNormal()
        w.activateWindow()

    def _verifyWarnings(self):
        manames_exclimits = self.ramp_config.ps_waveform_manames_exclimits
        if 'BO-Fam:MA-B' in manames_exclimits:
            manames_exclimits.remove('BO-Fam:MA-B')
        if len(manames_exclimits) > 0:
            self.label_exclim.setText('<h6>There are waveforms exceeding '
                                      'current limits.</h6>')
            self.pb_exclim.setVisible(True)
        else:
            self.label_exclim.setText('')
            self.pb_exclim.setVisible(False)

    def _showExcLimPopup(self):
        manames_exclimits = self.ramp_config.ps_waveform_manames_exclimits
        if 'BO-Fam:MA-B' in manames_exclimits:
            manames_exclimits.remove('BO-Fam:MA-B')
        text = 'The waveform of the following magnets\n' \
               'are exceeding current limits:\n'
        for maname in manames_exclimits:
            text += '    - ' + maname + '\n'
        QMessageBox.warning(self, 'Warning', text, QMessageBox.Ok)

    def updateGraph(self, update_axis=False):
        """Update and redraw graph."""
        if self.ramp_config is None:
            return
        if not self.ramp_config.ps_normalized_configs:
            for maname in self.manames:
                self.lines[maname].set_linewidth(0)
                self.m_inj.set_xdata([])
                self.m_inj.set_ydata([])
                self.m_ej.set_xdata([])
                self.m_ej.set_ydata([])
        else:
            xdata = self.ramp_config.ps_waveform_get_times()
            for maname in self._magnets_to_plot:
                if self.plot_unit == 'Strengths':
                    ydata = self.ramp_config.ps_waveform_get_strengths(maname)
                elif self.plot_unit == 'Currents':
                    ydata = self.ramp_config.ps_waveform_get_currents(maname)
                self.lines[maname].set_xdata(xdata)
                self.lines[maname].set_ydata(ydata)

            ydata = list()
            for maname in self.manames:
                if maname in self._magnets_to_plot:
                    self.lines[maname].set_linewidth(1.5)
                    ydata.append(self.lines[maname].get_ydata())
                else:
                    self.lines[maname].set_linewidth(0)

            if update_axis:
                self.ax.set_xlim(min(xdata), max(xdata))
                ydata = np.array(ydata)
                if len(ydata) > 0:
                    if ydata.min() == ydata.max():
                        self.ax.set_ylim(ydata.min()-0.2, ydata.max()+0.2)
                    elif ydata.min() < 0:
                        self.ax.set_ylim(ydata.min()*1.05, ydata.max()*1.05)
                    else:
                        self.ax.set_ylim(ydata.min()*0.95, ydata.max()*1.05)

            if self.plot_unit == 'Strengths':
                ylabel = None
                for maname in self._magnets_to_plot:
                    if 'MA-Q' not in maname:
                        break
                else:
                    ylabel = 'KL [1/m]'
                for maname in self._magnets_to_plot:
                    if 'MA-S' not in maname:
                        break
                else:
                    ylabel = 'SL [1/m$^2$]'
                for maname in self._magnets_to_plot:
                    if 'MA-C' not in maname:
                        break
                else:
                    ylabel = 'Kick [urad]'

                if ylabel:
                    self.ax.set_ylabel(ylabel)
                else:
                    self.ax.set_ylabel('Int. Strengths')
            else:
                self.ax.set_ylabel('Currents [A]')

            inj_marker_time = self.ramp_config.ti_params_injection_time
            self.m_inj.set_xdata(inj_marker_time)
            ej_marker_time = self.ramp_config.ti_params_ejection_time
            self.m_ej.set_xdata(ej_marker_time)

            inj_marker_value = list()
            ej_marker_value = list()
            if self.plot_unit == 'Strengths':
                func = self.ramp_config.ps_waveform_interp_strengths
            else:
                func = self.ramp_config.ps_waveform_interp_currents
            for maname in self._magnets_to_plot:
                inj_marker_value.append(func(maname, inj_marker_time))
                ej_marker_value.append(func(maname, ej_marker_time))
            self.m_inj.set_ydata(inj_marker_value)
            self.m_ej.set_ydata(ej_marker_value)

        self.graph.figure.canvas.draw()
        self.graph.figure.canvas.flush_events()

    def updateTable(self):
        """Update and rebuild table."""
        if self.ramp_config is None:
            return

        self.table.cellChanged.disconnect(self._handleCellChanged)

        config_dict = dict()
        self._getNormalizedConfigs()
        for config in self.normalized_configs:
            config_dict[config[0]] = config[1]

        for row, label in self.table_map['rows'].items():
            label_item = self.table.item(row, 0)  # name column
            t_item = self.table.item(row, 1)  # time column
            e_item = self.table.item(row, 2)  # energy column

            if label == 'Injection':
                time = self.ramp_config.ti_params_injection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label == 'Ejection':
                time = self.ramp_config.ti_params_ejection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label in config_dict.values():
                label_item.setData(Qt.DisplayRole, str(label))
                time = [t for t, n in config_dict.items() if n == label]
                time = time[0]
                energy = self.ramp_config.ps_waveform_interp_energy(time)
                del config_dict[time]
            t_item.setData(Qt.DisplayRole, '{0:.3f}'.format(time))
            e_item.setData(Qt.DisplayRole, '{0:.4f}'.format(energy))

        for row in self.table_map['rows'].keys():
            D = self.ramp_config.ps_ramp_duration
            N = self.ramp_config.ps_ramp_wfm_nrpoints
            T = float(self.table.item(row, 1).data(Qt.DisplayRole))
            value = round(T*N/D)
            item = self.table.item(row, 3)  # index column
            item.setData(Qt.DisplayRole, str(value))
        self._sortTable()

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config=None):
        """Update all widgets in loading BoosterRamp config."""
        if ramp_config is not None:
            self.ramp_config = ramp_config
            self.bonorm_edit_dict = dict()
        self._getNormalizedConfigs()
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateGraph(update_axis=True)
        self._verifyWarnings()

    @Slot(ramp.BoosterNormalized, str)
    def handleNormConfigsChanged(self, nconfig=None, old_nconfig_name=''):
        """Reload normalized configs on change and update graph."""
        if old_nconfig_name:
            row = [idx for idx, oldname in self.table_map['rows'].items()
                   if oldname == old_nconfig_name]
            time = float(self.table.item(row[0], 1).data(Qt.DisplayRole))
            self.ramp_config.ps_normalized_configs_delete(old_nconfig_name)
            self.ramp_config.ps_normalized_configs_insert(
                time=time, name=nconfig.name, nconfig=nconfig.value)
        else:
            self.ramp_config[nconfig.name] = nconfig

        self.bonorm_edit_dict = dict()
        self.handleLoadRampConfig()
        self.updateMultipoleRampSignal.emit()
        self.applyChanges2MachineSignal.emit()

    def updateOpticsAdjustSettings(self, tuneconfig_name, chromconfig_name):
        self._tunecorr_configname = tuneconfig_name
        self._chromcorr_configname = chromconfig_name
        self.updateOptAdjSettingsSignal.emit(tuneconfig_name, chromconfig_name)


class RFRamp(QWidget):
    """Widget to set and monitor RF ramp."""

    updateRFRampSignal = Signal()
    applyChanges2MachineSignal = Signal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()
        self.setObjectName('RFRampWidget')

    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setAlignment(Qt.AlignTop)
        self.graphview = QWidget()
        self.set_rfdelay = QFormLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupRFDelay()
        self._setupTable()

        vlay_v = QVBoxLayout()
        self.l_rampupv = QLabel('RmpU 0 [kV/s]')
        self.l_rampupv.setStyleSheet("""
            min-width:10.5em;max-width:10.5em;
            min-height:1.29em;max-height:1.29em;
            qproperty-alignment: AlignRight;""")
        self.l_rampdownv = QLabel('RmpD 0 [kV/s]')
        self.l_rampdownv.setStyleSheet("""
            min-width:10.5em;max-width:10.5em;
            min-height:1.29em;max-height:1.29em;
            qproperty-alignment: AlignRight;""")
        vlay_v.addWidget(self.l_rampupv)
        vlay_v.addWidget(self.l_rampdownv)

        self.bt_apply2machine = QPushButton('Apply Changes to Machine', self)
        self.bt_apply2machine.clicked.connect(
            self.applyChanges2MachineSignal.emit)

        label = QLabel('<h4>RF Ramp</h4>', self)
        label.setStyleSheet("""
            min-height:1.55em; max-height: 1.55em;
            qproperty-alignment: AlignCenter;""")
        glay.addWidget(label, 0, 0, 1, 3, alignment=Qt.AlignCenter)
        glay.addWidget(self.graphview, 1, 0, 1, 3)
        glay.addLayout(self.set_rfdelay, 2, 0)
        glay.addLayout(vlay_v, 2, 2)
        glay.addWidget(self.table, 3, 0, 1, 3)
        glay.addWidget(self.bt_apply2machine, 4, 0, 1, 3,
                       alignment=Qt.AlignRight)

    def _setupGraph(self):
        self.cb_show_syncphase = QCheckBox('Show Φs', self)
        self.cb_show_syncphase.setChecked(1)
        self.cb_show_syncphase.stateChanged.connect(
            self._handleShowSyncPhase)

        self.graph = SiriusFigureCanvas(Figure())
        self.graph.setObjectName('RFGraph')
        self.graph.setStyleSheet("""
            #RFGraph{
                min-width:30em;
                min-height:18em;max-height:18em;}""")
        self.graph.setSizePolicy(QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)
        self.graph.figure.set_tight_layout({'pad': .0})

        self.ax1 = self.graph.figure.subplots()
        self.ax1.grid()
        self.ax1.set_xlabel('t [ms]')
        self.ax1.set_ylabel('|Vgap| [kV]')
        self.line1, = self.ax1.plot([0], [0], '-b')
        self.m_inj, = self.ax1.plot([0], [0], marker='o', c='#787878')
        self.m_ej, = self.ax1.plot([0], [0], marker='o', c='#787878')

        self.ax2 = self.ax1.twinx()
        self.ax2.grid()
        self.ax2.set_ylabel('Φs [°]')
        self.line2, = self.ax2.plot([0], [0], '-g')

        self.toolbar = NavigationToolbar(self.graph, self)
        self.toolbar.setObjectName('toolbar')
        self.toolbar.setStyleSheet("""
            #toolbar{min-height:2em; max-height:2em;}""")

        lay = QVBoxLayout()
        lay.addWidget(self.graph)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.cb_show_syncphase, alignment=Qt.AlignRight)
        self.graphview.setLayout(lay)

    def _setupRFDelay(self):
        label_rfdelay = QLabel('RF delay [ms]:', self,
                               alignment=Qt.AlignVCenter)
        self.sb_rfdelay = _MyDoubleSpinBox(self)
        self.sb_rfdelay.setMinimum(0)
        self.sb_rfdelay.setMaximum(410)
        self.sb_rfdelay.setDecimals(6)
        self.sb_rfdelay.setSingleStep(0.000008)
        self.sb_rfdelay.editingFinished.connect(self._handleChangeRFDelay)
        self.set_rfdelay.addRow(label_rfdelay, self.sb_rfdelay)

    def _setupTable(self):
        self.table_map = {
            'rows': {0: 'Start',
                     1: 'RampUp-Start',
                     2: 'RampUp-Stop',
                     3: 'RampDown-Start',
                     4: 'RampDown-Stop'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: '|Vgap| [kV]',
                        3: '∠Vgap [°]',
                        4: 'E [GeV]'}}
        #                 5: 'Φs [°]'}}
        self.table.setObjectName('RFTable')
        self.table.setStyleSheet(
            """
            #RFTable{
                min-width: 30em;
                min-height: 10.69em; max-height: 10.69em;
            }
            QHeaderView::section {
                background-color: #4A5E28;
            }
            QTableWidget {
                background-color: #EAFFC0;
                gridline-color: #1D3000;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #4A5E28;
            }
            """)
        self.table.setRowCount(max(self.table_map['rows'].keys())+1)
        self.table.setColumnCount(max(self.table_map['columns'].keys())+1)
        self.table.horizontalHeader().setStyleSheet("""
            min-height:1.55em; max-height:1.55em;""")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())
        self.table.setSizePolicy(QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)

        for row, vlabel in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            Ph_item = QTableWidgetItem('0')
            Vgap_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            phsinc_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            phsinc_item.setFlags(Qt.ItemIsEnabled)
            if vlabel == 'Start':
                t_item.setFlags(Qt.ItemIsEnabled)
                Ph_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setBackground(QBrush(QColor("white")))
            elif vlabel == 'RampUp-Stop':
                t_item.setBackground(QBrush(QColor("white")))
                Ph_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setBackground(QBrush(QColor("white")))
            else:
                t_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, Vgap_item)
            self.table.setItem(row, 3, Ph_item)
            self.table.setItem(row, 4, e_item)
            self.table.setItem(row, 5, phsinc_item)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(int, int)
    def _handleCellChanged(self, row, column):
        if self.ramp_config is None:
            return

        try:
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            if self.table_map['rows'][row] == 'Start':
                if self.table_map['columns'][column] == '|Vgap| [kV]':
                    old_value = self.ramp_config.rf_ramp_bottom_voltage
                    self.ramp_config.rf_ramp_bottom_voltage = new_value
                elif self.table_map['columns'][column] == '∠Vgap [°]':
                    old_value = self.ramp_config.rf_ramp_bottom_phase
                    self.ramp_config.rf_ramp_bottom_phase = new_value

            elif self.table_map['rows'][row] == 'RampUp-Start':
                old_value = self.ramp_config.rf_ramp_rampup_start_time
                self.ramp_config.rf_ramp_rampup_start_time = new_value

            elif self.table_map['rows'][row] == 'RampUp-Stop':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.rf_ramp_rampup_stop_time
                    self.ramp_config.rf_ramp_rampup_stop_time = new_value
                elif self.table_map['columns'][column] == '|Vgap| [kV]':
                    old_value = self.ramp_config.rf_ramp_top_voltage
                    self.ramp_config.rf_ramp_top_voltage = new_value
                elif self.table_map['columns'][column] == '∠Vgap [°]':
                    old_value = self.ramp_config.rf_ramp_top_phase
                    self.ramp_config.rf_ramp_top_phase = new_value

            elif self.table_map['rows'][row] == 'RampDown-Start':
                old_value = self.ramp_config.rf_ramp_rampdown_start_time
                self.ramp_config.rf_ramp_rampdown_start_time = new_value

            elif self.table_map['rows'][row] == 'RampDown-Stop':
                old_value = self.ramp_config.rf_ramp_rampdown_stop_time
                self.ramp_config.rf_ramp_rampdown_stop_time = new_value

        except exceptions.RampInvalidRFParms as e:
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _UndoRedoTableCell(
                    self.table, row, column, old_value, new_value,
                    'set RF table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @Slot()
    def _handleChangeRFDelay(self):
        """Handle change rf delay."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ti_params_rf_ramp_delay
        new_value = self.sb_rfdelay.value()
        if new_value == old_value:
            # Avoid several updates on Enter or spinbox focusOutEvent.
            # It is necessary due to several emits of editingFinished signal.
            return

        try:
            self.ramp_config.ti_params_ps_ramp_delay = new_value
        except exceptions.RampInvalidRFParms as e:
            self.updateRFDelay()
            QMessageBox.critical(self, 'Error', str(e), QMessageBox.Ok)
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _UndoRedoSpinbox(
                    self.sb_rfdelay, old_value, new_value,
                    'set RF ramp delay to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def _calc_syncphase(self, t):
        times = [t] if isinstance(t, (int, float)) else t
        energies = self.ramp_config.ps_waveform_interp_energy(times)
        U0_nom = 0.00452e3  # eV
        E_nom = 0.150  # GeV
        U0 = [U0_nom*(E/E_nom)**4 for E in energies]
        V = 1e3 * self.ramp_config.rf_ramp_interp_voltages(times)  # V
        ph = list()
        for i in range(len(times)):
            try:
                ph.append(_math.asin(U0[i]/(V[i])))
            except Exception:
                ph.append(_math.pi/2)
        ph = [_math.degrees(phase) for phase in ph]
        ph = ph[0] if isinstance(t, (int, float)) else ph
        return ph

    @Slot(int)
    def _handleShowSyncPhase(self, show):
        width = 1.5 if show else 0
        self.ax2.set_visible(show)
        self.line2.set_linewidth(width)
        self.updateGraph()

    def updateGraph(self, update_axis=False):
        """Update and redraw graph."""
        if self.ramp_config is None:
            return

        xdata = list()
        xdata.append(0)
        for i in self.ramp_config.rf_ramp_times:
            xdata.append(i)
        xdata.append(490)
        self.line1.set_xdata(xdata)

        ydata = list()
        ydata.append(self.ramp_config.rf_ramp_voltages[0])
        for i in self.ramp_config.rf_ramp_voltages:
            ydata.append(i)
        ydata.append(self.ramp_config.rf_ramp_voltages[0])
        self.line1.set_ydata(ydata)

        inj_marker_time = self.ramp_config.ti_params_injection_time
        self.m_inj.set_xdata(inj_marker_time)
        self.m_inj.set_ydata(self.ramp_config.rf_ramp_interp_voltages(
            inj_marker_time))

        ej_marker_time = self.ramp_config.ti_params_ejection_time
        self.m_ej.set_xdata(ej_marker_time)
        self.m_ej.set_ydata(self.ramp_config.rf_ramp_interp_voltages(
            ej_marker_time))

        ph_times = self.ramp_config.ps_waveform_get_times()
        ph = self._calc_syncphase(ph_times)
        self.line2.set_xdata(ph_times)
        self.line2.set_ydata(ph)

        if update_axis:
            self.ax1.set_xlim(min(xdata), max(xdata))
            self.ax1.set_ylim(min(ydata)*0.95, max(ydata)*1.05)
            self.ax2.set_ylim(min(ph)*0.95, max(ph)*1.05)

        self.graph.figure.canvas.draw()
        self.graph.figure.canvas.flush_events()

    def updateRFDelay(self):
        """Update rf delay when ramp_config is loaded."""
        self.sb_rfdelay.setValue(self.ramp_config.ti_params_rf_ramp_delay)

    def updateTable(self):
        """Update and rebuild table."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for row, label in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)  # time column
            Vgap_item = self.table.item(row, 2)  # voltage amp column
            Ph_item = self.table.item(row, 3)  # voltage phase column
            if label == 'Start':
                time = self.ramp_config.ti_params_rf_ramp_delay
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            elif label == 'RampUp-Start':
                time = self.ramp_config.rf_ramp_rampup_start_time
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            elif label == 'RampUp-Stop':
                time = self.ramp_config.rf_ramp_rampup_stop_time
                vgap = self.ramp_config.rf_ramp_top_voltage
                ph = self.ramp_config.rf_ramp_top_phase
            elif label == 'RampDown-Start':
                time = self.ramp_config.rf_ramp_rampdown_start_time
                vgap = self.ramp_config.rf_ramp_top_voltage
                ph = self.ramp_config.rf_ramp_top_phase
            elif label == 'RampDown-Stop':
                time = self.ramp_config.rf_ramp_rampdown_stop_time
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            t_item.setData(Qt.DisplayRole, '{0:.3f}'.format(time))
            Vgap_item.setData(Qt.DisplayRole, '{0:.3f}'.format(vgap))
            Ph_item.setData(Qt.DisplayRole, '{0:.3f}'.format(ph))

        for column, label in self.table_map['columns'].items():
            for row in self.table_map['rows'].keys():
                if label == 'E [GeV]':
                    t_item = self.table.item(row, 1)
                    time = float(t_item.data(Qt.DisplayRole))
                    energy = self.ramp_config.ps_waveform_interp_energy(time)
                    e_item = self.table.item(row, column)
                    e_item.setData(Qt.DisplayRole, '{0:.4f}'.format(energy))
                # elif label == 'Φs [°]':
                #     t_item = self.table.item(row, 1)
                #     time = float(t_item.data(Qt.DisplayRole))
                #     value = self._calc_syncphase(time)
                #     item = self.table.item(row, column)
                #     item.setData(Qt.DisplayRole, '{0:.3f}'.format(value))

        rampupv = ((self.ramp_config.rf_ramp_top_voltage -
                   self.ramp_config.rf_ramp_bottom_voltage) /
                   self.ramp_config.rf_ramp_rampup_duration)
        self.l_rampupv.setText('RmpU {: .3f} [kV/s]'.format(1000*rampupv))

        rampdownv = ((self.ramp_config.rf_ramp_bottom_voltage -
                      self.ramp_config.rf_ramp_top_voltage) /
                     self.ramp_config.rf_ramp_rampdown_duration)
        self.l_rampdownv.setText('RmpD {: .3f} [kV/s]'.format(1000*rampdownv))

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        self.updateGraph(update_axis=True)
        self.updateRFDelay()
        self.updateTable()


class _UndoRedoTableCell(QUndoCommand):
    """Class to define command change table cell."""

    def __init__(self, table, row, column, old_data, new_data, description):
        super().__init__(description)
        self.table = table
        self.row = row
        self.column = column
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        global _flag_stack_next_command
        _flag_stack_next_command = False
        self.table.item(self.row, self.column).setData(
            Qt.DisplayRole, str(self.old_data))

    def redo(self):
        global _flag_stack_next_command, _flag_stacking
        if not _flag_stacking:
            _flag_stack_next_command = False
            self.table.item(self.row, self.column).setData(
                Qt.DisplayRole, str(self.new_data))
        else:
            _flag_stacking = False


class _UndoRedoSpinbox(QUndoCommand):
    """Class to define command change ramp number of points."""

    def __init__(self, spinbox, old_data, new_data, description):
        super().__init__(description)
        self.spinbox = spinbox
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        global _flag_stack_next_command
        _flag_stack_next_command = False
        self.spinbox.setValue(self.old_data)
        self.spinbox.editingFinished.emit()

    def redo(self):
        global _flag_stack_next_command, _flag_stacking
        if not _flag_stacking:
            _flag_stack_next_command = False
            self.spinbox.setValue(self.new_data)
            self.spinbox.editingFinished.emit()
        else:
            _flag_stacking = False
