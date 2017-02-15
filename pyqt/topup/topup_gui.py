#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import epics
import datetime
import time
import collections
import numpy
import lnls
import os
from PyQt5 import QtWidgets, QtCore
import hlaplot.datetime_plot


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.ip_widget = IPWindow()
        self.ip_widget.button.clicked.connect(self.set_ip)
        self.central_widget.addWidget(self.ip_widget)
        self.setWindowTitle('Top-up Injection')
        self.setGeometry(300, 100, 0, 0)


    def set_ip(self):
        os.environ["EPICS_CA_ADDR_LIST"] = self.ip_widget.ip.text()
        os.environ["EPICS_CA_AUTO_ADDR_LIST"] = "no"
        mywindow_widget = MyWindow()
        self.central_widget.addWidget(mywindow_widget)
        self.central_widget.setCurrentWidget(mywindow_widget)
        self.resize(600, 900)


class IPWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        label = QtWidgets.QLabel("Virtual Accelerator IP Address:")
        self.ip = QtWidgets.QLineEdit("10.0.21.255")
        self.button = QtWidgets.QPushButton('Start')
        self.button.setFixedSize(80, 80)
        self.button.setAutoDefault(True)

        hlayout = QtWidgets.QHBoxLayout()
        vlayout1 = QtWidgets.QVBoxLayout()
        vlayout2 = QtWidgets.QVBoxLayout()
        vlayout1.addWidget(label)
        vlayout1.addWidget(self.ip)
        vlayout2.addWidget(self.button)
        hlayout.addLayout(vlayout1)
        hlayout.addSpacing(20)
        hlayout.addLayout(vlayout2)
        self.setLayout(hlayout)
        self.setTabOrder(self.ip, self.button)


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.set_default_parameters_values()
        self.set_pvs()

        # Add title
        title = QtWidgets.QLabel("Top-up Injection")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font: bold 15pt")
        mlayout  = QtWidgets.QVBoxLayout()
        mlayout.addWidget(title)
        mlayout.addSpacing(30)

        # Add subtitle
        parameters_label = QtWidgets.QLabel("Top-up Parameters")
        parameters_label.setStyleSheet("font: bold")
        vlayout1 = QtWidgets.QVBoxLayout()
        vlayout1.addWidget(parameters_label)

        # Add input parameters
        self.max_current = self.add_parameter("Maximum Current:", "%s"%self.max_current_value, vlayout1,  "mA")
        self.max_decay   = self.add_parameter("Maximum Current Decay:", "%s"%self.max_decay_value, vlayout1, " %")
        self.frequency   = self.add_parameter("Frequency:", "%s"%self.frequency_value, vlayout1, "Hz")
        self.add_operation_mode_buttons(vlayout1)

        # Add button
        self.button = QtWidgets.QPushButton("Start Top-up Injection")
        self.button.setCheckable(True)
        self.button.setFixedWidth(200)
        self.button.toggled.connect(self.button_toggled)
        self.button.setMaximumSize(200, 200)
        vlayout2 = QtWidgets.QVBoxLayout()
        vlayout2.addWidget(self.button)

        # Add layouts to main layout
        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addLayout(vlayout1)
        hlayout1.addSpacing(50)
        hlayout1.addLayout(vlayout2)
        mlayout.addLayout(hlayout1)
        mlayout.addSpacing(50)

        # Add current text update
        current_label = QtWidgets.QLabel("Storage Ring Current:")
        current_label.setStyleSheet("font: bold 12pt")
        self.current = QtWidgets.QLabel("PV Disconnect")
        hlayout2 = QtWidgets.QHBoxLayout()
        hlayout2.addWidget(current_label)
        hlayout2.addWidget(self.current)
        hlayout2.addStretch(100)
        mlayout.addLayout(hlayout2)

        self.update_label()
        if self.single_bunch_mode.isChecked():
            self.set_uniform_filling_patern(single_bunch=1)
        else:
            self.set_uniform_filling_patern(single_bunch=0)

        # Timer threads
        self.topup_timer = lnls.Timer(self.time_interval, self.check_inject)
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plots)
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.update_label)
        self.current_timer.setInterval(1000.0)
        self.current_timer.start()

        # DateTimePlot
        self.plot_datetime = hlaplot.datetime_plot.DateTimePlot()
        mlayout.addWidget(self.plot_datetime)
        self.plot_datetime.x_label = 'Time'
        self.plot_datetime.y_label = 'Current (mA)'
        self.plot_datetime.y_autoscale = False
        self.plot_datetime.y_axis = (0.0, 380.0)
        self.plot_datetime.x_ticks_label_format = '%H:%M:%S'
        self.plot_datetime.x_tick_label_rotation = 0
        self.plot_datetime.datetime_coord_format = '%H:%M:%S'

        delta0 = datetime.timedelta(seconds=0)
        delta1 = datetime.timedelta(seconds=0)
        self.plot_datetime.x_axis_extra_spacing = (delta0, delta1)
        self.plot_datetime.y_axis_extra_spacing = 0.2
        self.plot_datetime.set_ticker('linear', 5)
        self.plot_datetime.interval = datetime.timedelta(seconds=60)
        self.plot_datetime.show_interval = True
        self.plot_datetime.add_line('line', 1000)
        self.plot_datetime.set_spacing(bottom=0.15, left=0.15)
        self.plot_datetime.line('line').color = 'SeaGreen'

        t0 = datetime.datetime.now() - datetime.timedelta(seconds=360)
        t = [t0 + datetime.timedelta(seconds=i) for i in range(360)]
        y1 = numpy.zeros(len(t))

        self.plot_datetime.line('line').x = t
        self.plot_datetime.line('line').y = y1
        self.plot_datetime.fill('line')
        self.update_times = collections.deque(maxlen=100)
        self.last_update = datetime.datetime.now()
        self.plot_timer.start(100)

        #Filling patern
        args = {}
        args['interval_min'] = 0
        args['interval_max'] = self.harmonic_number
        self.plot_filling = hlaplot.position_plot.PositionPlot(**args)
        mlayout.addWidget(self.plot_filling)
        self.plot_filling.x_label = 'Bunch'
        self.plot_filling.y_label = 'Filling (mA)'
        self.plot_filling.y_autoscale = False
        self.plot_filling.y_axis = (0.0, 0.6)
        self.plot_filling.add_line('line')

        x = range(self.harmonic_number)
        y = numpy.zeros(len(x))

        self.plot_filling.y_axis_extra_spacing = 0.2
        self.plot_filling.line('line').x = x
        self.plot_filling.line('line').y = y
        self.plot_filling.line('line').color = 'RoyalBlue'
        self.plot_filling.fill('line')
        self.plot_filling.update_plot()
        self.plot_filling.set_spacing(bottom=0.15, left=0.15)

        # Add dump button
        self.dump_button = QtWidgets.QPushButton("Dump")
        self.dump_button.setFixedWidth(60)
        self.dump_button.setMaximumSize(60, 60)
        self.dump_button.clicked.connect(self.dump)
        blayout = QtWidgets.QHBoxLayout()
        blayout.addStretch(500)
        blayout.addWidget(self.dump_button)
        mlayout.addLayout(blayout)

        self.setLayout(mlayout)

    def set_default_parameters_values(self):
        self.max_current_value = 350 # [mA]
        self.max_decay_value   = 0.5 # [%]
        self.frequency_value   = 2.0 # [Hz]
        self.harmonic_number   = 864
        self.multibunch_size   = 75
        self.time_interval     = 2.0 # [s]
        self.is_injecting      = False
        self.stop              = False
        self.i                 = 0

    def set_pvs(self):
        self.current_pv  = epics.PV('SIDI-CURRENT')
        self.bcurrent_pv = epics.PV('SIDI-BCURRENT')
        self.cycle_pv    = epics.PV('VA-LITI-CYCLE')
        self.mode_pv     = epics.PV('VA-LIFK-MODE')
        self.bunch_pv    = epics.PV('VA-LITI-INJECTION-BUNCH')
        self.rf_pv       = epics.PV('VA-SIRF-VOLTAGE')
        self.mode_pv.connect(0.1)
        self.bunch_pv.connect(0.1)

    def set_uniform_filling_patern(self, single_bunch=0):
        bunch = self.bunch_pv.get()
        idx = int(bunch) if bunch is not None else 0
        if single_bunch:
            self.bunches_indices = [(idx+i)%self.harmonic_number for i in range(0,self.harmonic_number)]
        else:
            self.bunches_indices = [(idx+i)%self.harmonic_number for i in \
                                    range(0,self.harmonic_number*self.multibunch_size, self.multibunch_size)]

    def add_parameter(self, label, text, layout, units=None):
        label = QtWidgets.QLabel(label)
        wid = QtWidgets.QLineEdit(text)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(wid)
        if units is not None:
            units_label = QtWidgets.QLabel(units)
            hlayout.addWidget(units_label)
        layout.addLayout(hlayout)
        return wid

    def add_operation_mode_buttons(self, layout):
        mode_label = QtWidgets.QLabel("Operation Mode:")
        self.mode_group = QtWidgets.QButtonGroup()
        self.single_bunch_mode = QtWidgets.QRadioButton("Single-bunch")
        self.multi_bunch_mode = QtWidgets.QRadioButton("Multi-bunch")
        self.single_bunch_mode.clicked.connect(self.single_bunch_button_clicked)
        self.multi_bunch_mode.clicked.connect(self.multi_bunch_button_clicked)
        self.mode_group.addButton(self.single_bunch_mode)
        self.mode_group.addButton(self.multi_bunch_mode)
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()
        hlayout.addWidget(mode_label)
        vlayout.addWidget(self.single_bunch_mode)
        vlayout.addWidget(self.multi_bunch_mode)
        hlayout.addLayout(vlayout)
        hlayout.addSpacing(50)
        layout.addLayout(hlayout)

    def single_bunch_button_clicked(self):
        if self.mode_pv.connected:
            self.mode_pv.put(1)
            self.set_uniform_filling_patern(single_bunch=1)

    def multi_bunch_button_clicked(self):
        if self.mode_pv.connected:
            self.mode_pv.put(0)
            self.set_uniform_filling_patern(single_bunch=0)

    def dump(self):
        if self.rf_pv.connected:
            self.stop = True
            if self.topup_timer.is_running:
                self.topup_timer.stop()
            self.button.setText("Start Top-up Injection")
            self.button.setChecked(0)

            rf = self.rf_pv.get()
            self.rf_pv.put(rf/20)
            time.sleep(0.1)
            self.rf_pv.put(rf)

            self.max_current.setReadOnly(False)
            self.max_decay.setReadOnly(False)
            self.frequency.setReadOnly(False)

    def button_toggled(self):
        if self.button.isChecked():
            if len(self.max_current.text())!= 0:
                self.max_current_value = float(self.max_current.text())
            if len(self.max_decay.text())!= 0:
                self.max_decay_value = float(self.max_decay.text())
            if len(self.frequency.text())!= 0:
                self.frequency_value = float(self.frequency.text())
            self.min_current_value = self.max_current_value * (1.0 - self.max_decay_value/100.0)
            self.cycle_interval = 1.0/self.frequency_value
            self.stop = False
            self.max_current.setReadOnly(True)
            self.max_decay.setReadOnly(True)
            self.frequency.setReadOnly(True)
            if self.cycle_pv.connected and self.current_pv.connected:
                self.topup_timer.start()
                self.button.setText("Stop Top-up Injection")
            else:
                self.button.setText("  PV Disconnected    ")
        else:
            self.stop = True
            self.max_current.setReadOnly(False)
            self.max_decay.setReadOnly(False)
            self.frequency.setReadOnly(False)

            if self.topup_timer.is_running:
                self.topup_timer.stop()
            self.button.setText("Start Top-up Injection")

    def update_plots(self):
        # update datetime plot
        t = datetime.datetime.now()
        if self.current_pv.connected:
            y1 = self.current_pv.get()
        else:
            y1 = 0.0
        self.plot_datetime.line('line').add_xy(t, y1)
        self.plot_datetime.fill('line')
        self.plot_datetime.update_plot()

        delta = datetime.datetime.now() - self.last_update
        self.update_times.append(delta)
        sum_seconds = 0
        for t in self.update_times:
            sum_seconds += t.seconds + t.microseconds / 1e6
        fps = len(self.update_times) / sum_seconds
        self.last_update = datetime.datetime.now()

        # update filling plot
        if self.bcurrent_pv.connected:
            y = self.bcurrent_pv.get()
            self.plot_filling.line('line').y = y
            self.plot_filling.fill('line')
            self.plot_filling.update_plot()

    def update_label(self):
        if self.mode_pv.connected:
            self.single_bunch_mode.setEnabled(1)
            self.multi_bunch_mode.setEnabled(1)
            value = self.mode_pv.get()
            if value == 1:
                self.single_bunch_mode.setChecked(1)
            else:
                self.multi_bunch_mode.setChecked(1)
        else:
            self.single_bunch_mode.setDisabled(1)
            self.multi_bunch_mode.setDisabled(1)
        if self.current_pv.connected:
            value = self.current_pv.get()
            self.current.setText("%3.5f mA"%value)
        else:
            self.current.setText("PV Disconnected")

    def check_inject(self):
        if self.is_injecting: return
        if not self.current_pv.connected:return
        while self.current_pv.get() < self.min_current_value and not self.stop:
            self.is_injecting = True
            while self.current_pv.get() < self.max_current_value and not self.stop:
                self.cycle()
        self.is_injecting = False

    def cycle(self):
        """Cycle injection"""
        if self.cycle_pv.connected:
            t0 = time.time()
            idx = self.i % len(self.bunches_indices)
            self.bunch_pv.put(self.bunches_indices[idx])
            self.i += 1
            self.cycle_pv.put(1)
            t1 = time.time()
            while t1 < t0 + self.cycle_interval:
                time.sleep(self.cycle_interval-(t1-t0))
                t1 = time.time()

def exec_(app):
    result = app.exec_()
    epics.ca.finalize_libca()
    return result

if __name__ == '__main__':
    epics.ca.initialize_libca()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(exec_(app))
