"""Efficiency Monitor."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QCheckBox, QGridLayout, \
    QApplication, QVBoxLayout

import qtawesome as qta

from pydm.widgets import PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriuspy.clientarch.time import Time
from siriushla.widgets import SiriusMainWindow, SiriusTimePlot
from siriushla.util import get_appropriate_color


class EfficiencyMonitor(SiriusMainWindow):
    """Efficiency monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        super().__init__(parent)
        self.setObjectName('ASApp')
        self.setWindowTitle('Efficiency Monitor')
        color = get_appropriate_color('AS')
        self.setWindowIcon(qta.icon('mdi.percent-outline', color=color))
        self._prefix = prefix
        self._eff_list = (
            # ('LI-SI Inj', 'AS-Glob:AP-CurrInfo:InjEff-Mon', 'magenta'),
            ('BO-SI Inj', 'SI-Glob:AP-CurrInfo:InjEff-Mon', 'blue'),
            ('TS', 'TS-Glob:AP-CurrInfo:TranspEff-Mon', 'black'),
            ('BO Ramp', 'BO-Glob:AP-CurrInfo:RampEff-Mon', 'green'),
            # ('LI-BO Inj', 'BO-Glob:AP-CurrInfo:InjEff-Mon', 'darkRed'),
            ('TB', 'TB-Glob:AP-CurrInfo:TranspEff-Mon', 'darkCyan'),
            ('LI', 'LI-Glob:AP-CurrInfo:TranspEff-Mon', 'red'),
        )
        self._app = QApplication.instance()
        font = self._app.font()
        font.setPointSize(32)
        self._app.setFont(font)
        self._setupUi()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.setFocusPolicy(Qt.StrongFocus)

        label = QLabel('<h3>Efficiency Monitor</h3>',
                       self, alignment=Qt.AlignCenter)

        # timeplot
        timespan = 30*60  # [s]
        self.timeplot = SiriusTimePlot(parent=self, background='w')
        self.timeplot.timeSpan = timespan
        self.timeplot.addAxis(
            plot_data_item=None, name='left', orientation='left')
        self.timeplot.autoRangeY = False
        self.timeplot.maxYRange = 150.0
        self.timeplot.minYRange = 0.0
        self.timeplot.showXGrid = True
        self.timeplot.showYGrid = True
        self.timeplot.setLabel(
            'left', text='Efficiency', units='%', color='gray')
        self.timeplot.setObjectName('timeplot')
        self.timeplot.setStyleSheet(
            '#timeplot{min-width:24em; min-height: 10em;}')
        t_end = Time.now()
        t_init = t_end - timespan

        self._channels = dict()
        self._curves = dict()
        self._cb_show = dict()
        self._pvs_labels = dict()

        lay_lbls = QVBoxLayout()
        lay_lbls.setSpacing(10)

        for i, data in enumerate(self._eff_list):
            text, pvn, color = data
            pvname = SiriusPVName(pvn).substitute(prefix=self._prefix)

            self.timeplot.addYChannel(
                pvname, name=pvname, color=color, lineWidth=2)
            curve = self.timeplot.curveAtIndex(-1)
            self._curves[pvn] = curve
            self.timeplot.fill_curve_with_archdata(
                self._curves[pvn], pvname,
                t_init=t_init.get_iso8601(), t_end=t_end.get_iso8601())

            cb = QCheckBox(text, self)
            cb.setChecked(True)
            cb.setStyleSheet('color:'+color+';')
            cb.stateChanged.connect(curve.setVisible)
            self._cb_show[pvn] = cb

            lb = PyDMLabel(self, pvname)
            lb.setStyleSheet("""
                QLabel{
                    font-weight: bold; min-width: 6em; max-width: 6em;
                    qproperty-alignment: AlignCenter;
                }""")
            lb.showUnits = True
            self._pvs_labels[pvn] = lb

            lay_lbls.addWidget(cb, alignment=Qt.AlignLeft)
            lay_lbls.addWidget(lb, alignment=Qt.AlignCenter)
            lay_lbls.addStretch()

        lay = QGridLayout(cw)
        lay.setSpacing(20)
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addWidget(self.timeplot, 1, 0)
        lay.addLayout(lay_lbls, 1, 1)
