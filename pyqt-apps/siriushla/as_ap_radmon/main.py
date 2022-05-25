"""Rad Monitor."""

from functools import partial as _part
import numpy as np

from qtpy.QtCore import Qt, QEvent, QTimer
from qtpy.QtGui import QColor, QPalette
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, QGridLayout, \
    QApplication, QVBoxLayout, QSizePolicy as QSzPol, QMenu

import qtawesome as qta

from pydm.widgets import PyDMLabel
from pydm.connection_inspector import ConnectionInspector

from siriuspy.envars import VACA_PREFIX
from siriuspy.clientarch.time import Time
from ..widgets import SiriusAlarmFrame, SiriusTimePlot
from ..util import get_appropriate_color


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
            ('Thermo3', '(SI-17, hall eixo 04)'),
            ('Thermo5', '(SI-19, hall eixo 10)'),
            ('Thermo11', '(SI-20, hall eixo 14)'),
        )
        cmap = {
            'x': np.linspace(0, 1, 12),
            'r': [1.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.8, 0.2, 0.5, 1.0, 1.0, 1.0],
            'g': [0.0, 0.0, 0.0, 0.4, 1.0, 0.2, 0.8, 0.2, 0.0, 0.0, 0.5, 1.0],
            'b': [1.0, 0.6, 0.3, 1.0, 1.0, 0.0, 0.8, 0.2, 0.0, 0.0, 0.0, 0.0],
        }
        xeval = np.linspace(0, 1, len(self._sensor_list))
        reval = np.interp(xeval, cmap['x'], cmap['r'])*255
        geval = np.interp(xeval, cmap['x'], cmap['g'])*255
        beval = np.interp(xeval, cmap['x'], cmap['b'])*255
        self._colors = [(r, g, b) for r, g, b in zip(reval, geval, beval)]

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
        self.timeplot = SiriusTimePlot(
            parent=self, background='w', show_tooltip=True)
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
        self.timeplot.bufferReset.connect(self._fill_refline)
        self.timeplot.timeSpanChanged.connect(self._fill_refline)
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
        widgrid.setSizePolicy(QSzPol.Maximum, QSzPol.Expanding)
        self.pannel = widgrid
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

            cbx = QCheckBox(self)
            cbx.setChecked(True)
            cbx.stateChanged.connect(curve.setVisible)
            cbx.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
            pal = cbx.palette()
            pal.setColor(QPalette.Base, coloro)
            pal.setColor(QPalette.Text, Qt.white)
            cbx.setPalette(pal)
            self._cb_show[pvn] = cbx

            lbl = PyDMLabel(self, pvname + ':Dose')
            lbl.alarmSensitiveBorder = False
            lbl.setStyleSheet('QLabel{font-size: 52pt;}')
            lbl.showUnits = True
            self._pvs_labels[pvn] = lbl

            frame = SiriusAlarmFrame(self, pvname + ':Dose')
            frame.add_widget(cbx)
            frame.add_widget(lbl)

            desc = QLabel(pvn + ' ' + local, self, alignment=Qt.AlignCenter)
            desc.setSizePolicy(QSzPol.Preferred, QSzPol.Maximum)
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
        self._fill_refline()

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
        self._timer.setInterval(2000)
        self._timer.start()

    # ---------- events ----------

    def changeEvent(self, event):
        """Implement change event to get font size changes."""
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
            for lbl in self._pvs_labels.values():
                lbl.setStyleSheet(
                    'QLabel{font-size: '+str(fontsize + 8) +
                    'pt; min-width: 7em;}')
            for desc in self._desc_labels.values():
                desc.setStyleSheet(
                    'QLabel{background-color:black; color:white;'
                    'font-size:'+str(fontsize - 18)+'pt;}')

            self.ensurePolished()

    def contextMenuEvent(self, event):
        """Implement context menu to add auxiliary actions."""
        pos = self.mapToGlobal(event.pos())
        if not self.pannel.underMouse():
            return
        menu = QMenu(self)
        show = menu.addAction('Show all curves')
        show.triggered.connect(_part(self._set_checkbox_state, True))
        hide = menu.addAction('Hide all curves')
        hide.triggered.connect(_part(self._set_checkbox_state, False))
        conn = menu.addAction('Show Connections...')
        conn.triggered.connect(self._show_connections)
        menu.popup(pos)

    # ---------- private methods ----------

    def _fill_refline(self):
        basecurve = self.timeplot.curveAtIndex(0)
        timebuffer = basecurve.data_buffer[0]
        firstvalid = (timebuffer != 0).argmax()
        if timebuffer[firstvalid] == 0:
            timebuffer = np.array([Time.now().timestamp(), ])
        else:
            timebuffer = timebuffer[firstvalid:]
        valuebuffer = [RadTotDoseMonitor.REF_TOT_DOSE]*timebuffer.size
        self.timeplot.fill_curve_buffer(
            self.refline, timebuffer, valuebuffer)

    def _update_graph_ref(self):
        self.refline.receiveNewValue(RadTotDoseMonitor.REF_TOT_DOSE)
        self.refline.redrawCurve()

    def _show_connections(self, checked):
        """Show connections action."""
        _ = checked
        conn = ConnectionInspector(self)
        conn.show()

    def _set_checkbox_state(self, state):
        for cbx in self._cb_show.values():
            cbx.setChecked(state)
