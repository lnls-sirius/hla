"""Rad Monitor."""

import numpy as np

from matplotlib import cm

from qtpy.QtCore import Qt, QEvent, QTimer
from qtpy.QtGui import QColor, QPalette
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, QGridLayout, \
    QApplication, QVBoxLayout, QHBoxLayout, QSizePolicy as QSzPol

import qtawesome as qta

from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.clientarch.time import Time
from ..widgets import SiriusAlarmFrame
from ..util import get_appropriate_color
from .custom_widgets import MyTimePlot


class RadTotDoseMonitor(QWidget):
    """RAD Total Dose Rate Monitor."""

    REF_TOT_DOSE = 0.5  # µSv/h

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        super().__init__(parent)
        self._prefix = prefix

        # define aux objects
        self._channels = dict()
        self._curves = dict()
        self._cb_show = dict()
        self._pvs_labels = dict()
        self._desc_labels = dict()

        # configure window
        self.setObjectName('ASApp')
        self.setWindowTitle('RAD: Total Dose Monitor')
        color = get_appropriate_color('AS')
        self.setWindowIcon(qta.icon('fa5s.radiation', color=color))

        # define data
        self._sensor_list = (
            ('Thermo12', '(SI-01, hall eixo 16)'),
            ('ELSE', '(SI-01, hall eixo 17)'),
            ('Thermo8', '(SI-01, hall eixo 18)'),
            ('Thermo10', '(SI-01, chicane 1)'),
            ('Berthold', '(corr. de serviço, eixo 19)'),
            ('Thermo9', '(SI-02, hall eixo 20)'),
            ('Thermo13', '(SI-06, hall eixo 31)'),
            ('Thermo7', '(SI-08-IA-08, eixo 37)'),
            ('Thermo16', '(SI-08, hall eixo 38)'),
            ('Thermo2', '(SI-09-IA-09, eixo 40)'),
            ('Thermo1', '(SI-10, hall eixo 43)'),
            ('Thermo15', '(SI-12, hall eixo 50)'),
            ('Thermo14', '(SI-14, hall eixo 55)'),
            ('Thermo4', '(SI-14-IA-14, eixo 57)'),
            ('Thermo6', '(SI-15, hall eixo 59)'),
            ('Thermo5', '(SI-17, hall eixo 04)'),
            ('Thermo3', '(SI-19, hall eixo 10)'),
            ('Thermo11', '(SI-20, hall eixo 14)'),
        )
        self._colors = cm.jet(np.linspace(0, 1, len(self._sensor_list)))*255

        # define app font size
        self.app = QApplication.instance()
        font = self.app.font()
        font.setPointSize(44)
        self.app.setFont(font)

        # setup window
        self._setupUi()

        # define focus policy
        self.setFocusPolicy(Qt.StrongFocus)

        # set initial size
        if self.app.primaryScreen().geometry().width() >= 1920:
            self.resize(1920, 1080)

    def _setupUi(self):
        # timeplot
        self.title_plot = QLabel(
            'Total Dose Rate (γ + n) [µSv/h]', self, alignment=Qt.AlignCenter)
        self.title_plot.setStyleSheet(
            'QLabel{font-size: 52pt; font-weight: bold;}')

        timespan = 30*60  # [s]
        self.timeplot = MyTimePlot(parent=self, background='w')
        self.timeplot.timeSpan = timespan
        self.timeplot.bufferSize = 4*60*60*10
        self.timeplot.autoRangeY = True
        self.timeplot.minYRange = 0.0
        self.timeplot.showXGrid = True
        self.timeplot.showYGrid = True
        self.timeplot.maxRedrawRate = 2
        color = QColor(30, 30, 30)
        self.timeplot.plotItem.getAxis('bottom').setPen(color)
        self.timeplot.plotItem.getAxis('bottom').setGrid(255)
        self.timeplot.plotItem.getAxis('bottom').setTextPen(color)
        self.timeplot.plotItem.getAxis('left').setPen(color)
        self.timeplot.plotItem.getAxis('left').setGrid(255)
        self.timeplot.plotItem.getAxis('left').setTextPen(color)
        self.timeplot.setLabel('left', text='Dose Rate [µSv/h]')
        self.timeplot.setObjectName('timeplot')
        self.timeplot.setStyleSheet(
            '#timeplot{min-width:12em; min-height: 10em;}')
        t_end = Time.now()
        t_init = t_end - timespan

        widplot = QWidget()
        widplot.setSizePolicy(QSzPol.Expanding, QSzPol.Expanding)
        layplot = QGridLayout(widplot)
        layplot.setHorizontalSpacing(10)
        layplot.setVerticalSpacing(10)
        layplot.addWidget(self.title_plot, 0, 0)
        layplot.addWidget(self.timeplot, 1, 0)

        # panel
        self.title_grid = QLabel(
            'Integrated Dose in 4h [µSv]', self, alignment=Qt.AlignCenter)
        self.title_grid.setStyleSheet(
            'QLabel{font-size: 52pt; font-weight: bold;}')

        widgrid = QWidget()
        widgrid.setSizePolicy(QSzPol.Minimum, QSzPol.Expanding)
        laygrid = QGridLayout(widgrid)
        laygrid.setHorizontalSpacing(10)
        laygrid.setVerticalSpacing(10)
        colnum = 3
        laygrid.addWidget(self.title_grid, 0, 0, 1, colnum)

        for i, data in enumerate(self._sensor_list):
            pvn, local = data
            color = self._colors[i]
            pvname = self._prefix + ('-' if self._prefix else '')
            pvname += 'RAD:' + pvn + ':TotalDoseRate'
            row, col = i // colnum + 1, i % colnum

            coloro = QColor(color) if isinstance(color, str) \
                else QColor(*color)
            self.timeplot.addYChannel(
                pvname, name=pvname, color=coloro, lineWidth=6)
            curve = self.timeplot.curveAtIndex(-1)
            self._curves[pvn] = curve
            self.timeplot.fill_curve_with_archdata(
                self._curves[pvn], pvname,
                t_init=t_init.get_iso8601(), t_end=t_end.get_iso8601())

            cb = QCheckBox(self)
            cb.setChecked(True)
            cb.stateChanged.connect(curve.setVisible)
            pal = cb.palette()
            pal.setColor(QPalette.Base, coloro)
            pal.setColor(QPalette.Text, Qt.white)
            cb.setPalette(pal)
            self._cb_show[pvn] = cb

            lb = PyDMLabel(self, pvname + ':Dose')
            lb.alarmSensitiveBorder = False
            lb.setStyleSheet('QLabel{font-size: 52pt;}')
            lb.showUnits = True
            self._pvs_labels[pvn] = lb

            widfr = QWidget()
            widfrlay = QHBoxLayout(widfr)
            widfrlay.setContentsMargins(0, 0, 0, 0)
            widfrlay.addWidget(cb)
            widfrlay.addWidget(lb)
            frame = SiriusAlarmFrame(self, pvname + ':Dose')
            frame.add_widget(widfr)

            desc = QLabel(pvn + ' ' + local, self, alignment=Qt.AlignCenter)
            desc.setStyleSheet(
                'QLabel{background-color:black; color:white;font-size:26pt;}')
            self._desc_labels[pvn] = desc

            wid = QWidget()
            wid.setObjectName('wid')
            wid.setStyleSheet(
                '#wid{border: 1px solid black; '
                'min-width: 7.5em; max-width: 7.5em;}')
            widlay = QVBoxLayout(wid)
            widlay.setSpacing(0)
            widlay.setContentsMargins(1, 1, 1, 1)
            widlay.addWidget(frame)
            widlay.addWidget(desc)

            laygrid.addWidget(wid, row, col)

        laygrid.setColumnStretch(0, 1)
        laygrid.setColumnStretch(1, 1)
        laygrid.setColumnStretch(2, 1)

        self.timeplot.addYChannel(
            'Reference', color='black', lineWidth=6, lineStyle=Qt.DashLine)
        self.refline = self.timeplot.curveAtIndex(-1)
        basecurve = self.timeplot.curveAtIndex(0)
        timebuffer = basecurve.data_buffer[0]
        valuebuffer = [RadTotDoseMonitor.REF_TOT_DOSE]*timebuffer.size
        self.timeplot.fill_curve_buffer(
            self.refline, timebuffer, valuebuffer)

        lay = QGridLayout(self)
        lay.setSpacing(20)
        lay.addWidget(widplot, 0, 0)
        lay.addWidget(widgrid, 0, 1)

        self.setStyleSheet("""
            PyDMLabel{
                qproperty-alignment: AlignCenter; font-weight: bold;
            }
            QCheckBox::indicator {
                width: 0.7em;
                height: 0.7em;
            }""")

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_graph_ref)
        self._timer.setInterval(5000)
        self._timer.start()

    def changeEvent(self, event):
        if event.type() == QEvent.FontChange and self._pvs_labels:
            fontsize = self.app.font().pointSize()

            # title
            self.title_plot.setStyleSheet(
                'QLabel{font-size: '+str(fontsize + 8) +
                'pt; font-weight: bold;}')
            self.title_grid.setStyleSheet(
                'QLabel{font-size: '+str(fontsize + 8) +
                'pt; font-weight: bold;}')

            # labels
            for lb in self._pvs_labels.values():
                lb.setStyleSheet(
                    'QLabel{font-size: '+str(fontsize + 8) +
                    'pt; min-width: 7em;}')
            for desc in self._desc_labels.values():
                desc.setStyleSheet(
                    'QLabel{background-color:black; color:white;'
                    'font-size:'+str(fontsize - 18)+'pt;}')

            self.ensurePolished()

    def _update_graph_ref(self):
        self.refline.receiveNewValue(RadTotDoseMonitor.REF_TOT_DOSE)
        self.refline.redrawCurve()