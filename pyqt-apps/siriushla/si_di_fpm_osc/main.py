"""DCCT Monitor Windows."""

import numpy as np
import qtawesome as qta
from pyqtgraph import InfiniteLine, mkPen
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget
from siriushla import util
from siriushla.widgets import SiriusConnectionSignal, SiriusLabel, \
    SiriusMainWindow, SiriusSpinbox, SiriusWaveformPlot
from siriushla.widgets.windows import create_window_from_widget
from siriuspy.namesys import SiriusPVName


class FPMOscMain(SiriusMainWindow):
    """DCCT Main Window."""
    FPM_PV_PREFIX = 'SI-Glob:DI-FPMOsc'

    def __init__(self, parent=None, prefix=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = SiriusPVName(FPMOscMain.FPM_PV_PREFIX)
        self.setObjectName(self.device.sec + 'App')
        self.setWindowTitle(self.device)
        self.setWindowIcon(
            qta.icon(
                'mdi.basket-fill',
                color=util.get_appropriate_color(self.device.sec)
            )
        )
        self._setup_ui()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setup_ui(self):
        cwid = QWidget()
        self.setCentralWidget(cwid)
        clay = QGridLayout(cwid)

        self.title = QLabel(
            '<h3> Filling Pattern Monitor ('+self.device+')</h3>',
            alignment=Qt.AlignCenter
        )

        graph = SiriusWaveformPlot(parent=self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 13em; min-width: 20em;}')
        graph.maxRedrawRate = 2
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        graph.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        graph.setLabel('left', text='Current', units='mA')
        graph.setLabel('bottom', text='Bunch Index', units='')
        graph.plotItem.legend.setOffset((-1, -1))
        graph.plotItem.legend.setLabelTextColor('k')
        graph.plotItem.legend.layout.setContentsMargins(5, 0, 0, 0)
        graph.plotItem.legend.layout.setVerticalSpacing(-10)
        graph.plotItem.legend.setBrush(QColor(255, 255, 255, 190))

        opts = dict(
            y_channel=self.device.substitute(propty='FillPattern-Mon'),
            x_channel='',
            name='Measured',
            color=QColor(0, 0, 0),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=1,
            symbol='o',
            symbolSize=7
        )
        graph.addChannel(**opts)
        cdta = graph.curveAtIndex(-1)
        cdta.setSymbolBrush((0, 0, 0))

        opts = dict(
            y_channel=self.device.substitute(propty='FillPatternRef-Mon'),
            x_channel='',
            name='Reference',
            color=QColor(0, 0, 255),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol=None,
            symbolSize=5
        )
        graph.addChannel(**opts)

        self.graph = graph

        self.lab_fid = QLabel("Fiducial Offset:", cwid)
        self.lab_fid.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spb_fid = SiriusSpinbox(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="FiducialOffset-SP"
            )
        )
        self.lrb_fid = SiriusLabel(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="FiducialOffset-RB"
            )

        )

        self.lab_tim = QLabel("Update Interval:", cwid)
        self.lab_tim.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spb_tim = SiriusSpinbox(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="UpdateTime-SP"
            )
        )
        self.lrb_tim = SiriusLabel(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="UpdateTime-RB"
            )
        )
        self.lrb_tim.showUnits = True

        self.lab_cur = QLabel("Total Current:", cwid)
        self.lab_cur.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lrb_cur = SiriusLabel(
            parent=cwid,
            init_channel='SI-Glob:AP-CurrInfo:Current-Mon'
        )
        self.lrb_cur.showUnits = True

        self.lab_eqv = QLabel("Uni. Fill Equiv. Current:", cwid)
        self.lab_eqv.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lrb_eqv = SiriusLabel(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="UniFillEqCurrent-Mon"
            )
        )
        self.lrb_eqv.showUnits = True

        self.lab_err = QLabel("Fill Pattern Error", cwid)
        self.lab_err.setAlignment(Qt.AlignCenter)
        self.lab_std = QLabel("STD:", cwid)
        self.lab_std.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lrb_std = SiriusLabel(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="ErrorRelStd-Mon"
            )
        )
        self.lrb_std.showUnits = True

        self.lab_kld = QLabel("KL Div.:", cwid)
        self.lab_kld.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lrb_kld = SiriusLabel(
            parent=cwid,
            init_channel=self.device.substitute(
                propty="ErrorKLDiv-Mon"
            )
        )

        lay = QGridLayout()
        lay.addWidget(self.lab_cur, 0, 1)
        lay.addWidget(self.lrb_cur, 0, 2)
        lay.addWidget(self.lab_eqv, 1, 1)
        lay.addWidget(self.lrb_eqv, 1, 2)
        lay.addWidget(self.lab_err, 0, 4, 1, 6)
        lay.addWidget(self.lab_std, 1, 5)
        lay.addWidget(self.lrb_std, 1, 6)
        lay.addWidget(self.lab_kld, 1, 8)
        lay.addWidget(self.lrb_kld, 1, 9)
        lay.setColumnMinimumWidth(6, 5)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(3, 2)
        lay.setColumnStretch(4, 1)
        lay.setColumnStretch(10, 1)
        lay.setColumnStretch(11, 2)

        self.lab_det = QLabel("Details:", cwid)
        self.pbt_det = QPushButton('', cwid)
        self.pbt_det.setIcon(qta.icon('fa5s.ellipsis-v'))
        self.pbt_det.setObjectName('sts')
        self.pbt_det.setStyleSheet(
            '#sts{min-width:18px; max-width:18px; icon-size:20px;}')

        details_win = create_window_from_widget(
            Details, title='FPM Detailed View')

        util.connect_window(
            self.pbt_det,
            details_win,
            parent=self,
            prefix=self.prefix,
            device=self.device,
        )
        clay.addWidget(self.title, 0, 0, 1, 12)
        clay.addWidget(self.lab_fid, 2, 1)
        clay.addWidget(self.spb_fid, 2, 2)
        clay.addWidget(self.lrb_fid, 2, 3)
        clay.addWidget(self.lab_tim, 2, 5)
        clay.addWidget(self.spb_tim, 2, 6)
        clay.addWidget(self.lrb_tim, 2, 7)
        clay.addWidget(self.lab_det, 2, 9)
        clay.addWidget(self.pbt_det, 2, 10)
        clay.addLayout(lay, 4, 0, 1, 12)
        clay.addWidget(self.graph, 6, 0, 1, 12)
        clay.setColumnStretch(0, 2)
        clay.setColumnStretch(4, 2)
        clay.setColumnStretch(8, 2)
        clay.setColumnStretch(11, 2)
        clay.setRowMinimumHeight(1, 10)
        clay.setRowMinimumHeight(3, 10)
        clay.setRowMinimumHeight(5, 2)
        clay.setRowStretch(6, 2)
        # clay.set


class Details(QWidget):
    """."""

    def __init__(self, parent=None, prefix='', device=''):
        """."""
        self.device = device
        self.prefix = prefix
        super().__init__(parent=parent)
        self.setObjectName(self.device.sec + 'App')
        self.setWindowTitle(self.device)
        self.setWindowIcon(
            qta.icon(
                'mdi.basket-fill',
                color=util.get_appropriate_color(self.device.sec)
            )
        )
        self._setup_ui()

    def _setup_ui(self):
        lay = QGridLayout(self)

        self.title = QLabel(
            '<h3> FPM Detailed View</h3>',
            self,
            alignment=Qt.AlignCenter
        )

        graph = SiriusWaveformPlot(parent=self)
        graph.setObjectName('graph')
        graph.setStyleSheet('#graph {min-height: 15em; min-width: 30em;}')
        graph.maxRedrawRate = 2
        graph.mouseEnabledX = True
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setBackgroundColor(QColor(255, 255, 255))
        graph.setShowLegend(True)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setMinXRange(0.0)
        graph.setMaxXRange(1.0)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.plotItem.getAxis('bottom').setStyle(tickTextOffset=15)
        graph.plotItem.getAxis('left').setStyle(tickTextOffset=5)
        graph.setLabel('left', text='Current', units='mA')
        graph.setLabel('bottom', text='Time', units='ns')
        graph.plotItem.legend.setOffset((-1, -1))
        graph.plotItem.legend.setLabelTextColor('k')
        graph.plotItem.legend.layout.setContentsMargins(5, 0, 0, 0)
        graph.plotItem.legend.layout.setVerticalSpacing(-10)
        graph.plotItem.legend.setBrush(QColor(255, 255, 255, 190))

        dev = self.device
        opts = dict(
            y_channel=dev.substitute(propty='Raw-Mon'),
            x_channel=dev.substitute(propty='RawTime-Mon'),
            name='Raw Data',
            color=QColor(0, 0, 255),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol=None,
            symbolSize=10
        )
        graph.addChannel(**opts)

        opts = dict(
            y_channel=dev.substitute(propty='RawAmp-Mon'),
            x_channel=dev.substitute(propty='RawTime-Mon'),
            name='Amplitude',
            color=QColor(255, 0, 0),
            redraw_mode=2,
            lineStyle=1,
            lineWidth=2,
            symbol=None,
            symbolSize=10
        )
        graph.addChannel(**opts)

        opts = dict(
            y_channel=dev.substitute(propty='FillPattern-Mon'),
            x_channel=dev.substitute(propty='Time-Mon'),
            name='Fill Pattern',
            color=QColor(0, 0, 0),
            redraw_mode=2,
            lineStyle=0,
            lineWidth=2,
            symbol='o',
            symbolSize=None
        )
        graph.addChannel(**opts)
        cdta = graph.curveAtIndex(-1)
        cdta.setSymbolBrush((0, 0, 0))

        pen = mkPen(opts['color'], width=opts['lineWidth'])
        pen.setStyle(2)
        self.curve_bun0 = InfiniteLine(pos=0.0, pen=pen, angle=90)
        graph.addItem(self.curve_bun0)
        self.curve_bun0.opts = {'pen': pen}
        graph.plotItem.legend.addItem(self.curve_bun0, 'Bunch 0')

        self.dtx = SiriusConnectionSignal(
            dev.substitute(propty='Time-Mon')
        )
        self.dtx.new_value_signal[np.ndarray].connect(self._update_bunch_0)

        self.graph = graph

        self.lab_tim = QLabel("Time Offset:", self)
        self.lab_tim.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lrb_tim = SiriusLabel(
            parent=self,
            init_channel=self.device.substitute(
                propty="TimeOffset-Mon"
            )
        )
        self.lrb_tim.showUnits = True

        lay.addWidget(self.title, 0, 0, 1, 3)
        lay.addWidget(self.lab_tim, 1, 1)
        lay.addWidget(self.lrb_tim, 1, 2)
        lay.addWidget(self.graph, 2, 0, 1, 3)
        lay.setRowMinimumHeight(1, 10)
        lay.setRowStretch(2, 2)
        lay.setColumnStretch(0, 2)

    def _update_bunch_0(self, data):
        self.curve_bun0.setValue(data[0])
