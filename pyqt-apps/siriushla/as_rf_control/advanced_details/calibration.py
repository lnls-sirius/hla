"""LLRF Calibration Systems advanced details."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QComboBox, QGridLayout, QHBoxLayout, \
    QLabel, QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, \
    QWidget

from ...widgets import SiriusDialog, SiriusLabel, SiriusLineEdit, \
    SiriusTimePlot
from ..util import SEC_2_CHANNELS


class CalibrationDetails(SiriusDialog):
    """LLRF Calibration Systems advanced details."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Calibration Systems Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['CalSys'][self.system]
        else:
            self.syst_dict = self.chs['CalSys']
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_signals = QWidget(self)
        wid_signals.setLayout(
            self._signalsLayout())
        dtls.addTab(wid_signals, 'Signals')

        wid_iq = QWidget(self)
        wid_iq.setLayout(self._graphLayout())
        dtls.addTab(wid_iq, 'Graph')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _signalsLayout(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        cb_units = QComboBox(self)
        cb_units.addItems(['W', 'dBm'])
        cb_units.setStyleSheet(
            'QComboBox{max-width: 4em; font-weight: bold;}')
        cb_units.currentTextChanged.connect(self._handle_labels_units)

        lay.addWidget(QLabel('<h4>Label</h4>', alignment=Qt.AlignCenter),
            0, 1, 1, 2)
        lay.addItem(QSpacerItem(12, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 3)
        lay.addWidget(QLabel('<h4>UnCal</h4>', alignment=Qt.AlignCenter), 0, 4)
        lay.addItem(QSpacerItem(12, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 5)
        lay.addWidget(QLabel('<h4>Offset</h4>', alignment=Qt.AlignCenter),
            0, 6, 1, 2)
        lay.addItem(QSpacerItem(12, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 8)
        lay.addWidget(QLabel('<h4>Cal</h4>', alignment=Qt.AlignCenter), 0, 9)
        lay.addWidget(cb_units, 0, 10)

        self.cals_dbm = []
        self.cals_w = []
        for i in range(1, 17):
            lb_ch = QLabel(f'Ch{i}', alignment=Qt.AlignCenter)
            lb_ch.setStyleSheet(f'color:{self.syst_dict[f"Ch{i}"]["Color"]};')

            lb_label = SiriusLabel(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Label'])
            lb_label.setStyleSheet("min-width:8em;")

            lb_uncal = SiriusLabel(
                self, self.prefix+self.syst_dict[f'Ch{i}']['UnCal'])
            lb_uncal.showUnits = True
            lb_ofs = SiriusLabel(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Ofs'])
            lb_ofs.showUnits = True

            lb_cal_dbm = SiriusLabel(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Cal']['dBm'])
            lb_cal_dbm.showUnits = True
            lb_cal_w = SiriusLabel(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Cal']['W'])
            lb_cal_w.showUnits = True
            lb_cal_dbm.setVisible(False)
            lb_cal_w.setVisible(True)

            lay.addWidget(lb_ch, i, 0)
            lay.addWidget(SiriusLineEdit(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Label']), i, 1)
            lay.addWidget(lb_label, i, 2)
            lay.addWidget(lb_uncal, i, 4)
            lay.addWidget(SiriusLineEdit(
                self, self.prefix+self.syst_dict[f'Ch{i}']['Ofs']), i, 6)
            lay.addWidget(lb_ofs, i, 7)
            lay.addWidget(lb_cal_dbm, i, 9, 1, 2)
            lay.addWidget(lb_cal_w, i, 9, 1, 2)

            self.cals_dbm.append(lb_cal_dbm)
            self.cals_w.append(lb_cal_w)

        return lay

    def _graphLayout(self):
        lay_table = QGridLayout()
        lay_table.setAlignment(Qt.AlignTop)
        lay_table.setSpacing(9)

        self.cb_units = QComboBox(self)
        self.cb_units.addItems(['W', 'dBm'])
        self.cb_units.setStyleSheet(
            'QComboBox{max-width: 4em; font-weight: bold;}')
        self.cb_units.currentTextChanged.connect(
            self._handle_curves_units)
        lay_table.addWidget(
            QLabel('<h4>Channel</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay_table.addWidget(self.cb_units, 0, 2)

        self.graph = SiriusTimePlot(self)
        self.graph.autoRangeX = True
        self.graph.autoRangeY = True
        self.graph.backgroundColor = QColor(255, 255, 255)
        self.graph.showXGrid = True
        self.graph.showYGrid = True
        self.graph.timeSpan = 1800
        self.graph.maxRedrawRate = 1
        self.graph.setObjectName('graph')
        self.graph.setStyleSheet(
            '#graph{min-width: 21em; min-height: 18em;}')

        self.curves = dict()
        idx = 0
        for name, dic in self.syst_dict.items():
            wch, dbch = dic['Cal']['W'], dic['Cal']['dBm']
            color = dic['Color']
            row = idx+1

            # Table
            cbx = QCheckBox(self)
            cbx.setChecked(True)
            cbx.setObjectName(name)
            cbx.setStyleSheet('color:'+color+'; max-width: 1.2em;')
            cbx.stateChanged.connect(self._handle_curves_visibility)

            lb_ch = QLabel(name, self)
            lb_ch.setStyleSheet(
                'min-height: 1.5em; color:'+color+'; max-width: 8em;'
                'qproperty-alignment: AlignCenter;')
            lay_table.addWidget(cbx, row, 0)
            lay_table.addWidget(lb_ch, row, 1, 1, 2)

            # Graph
            self.graph.addYChannel(
                y_channel=self.prefix+dbch, name=name+' dBm', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' dBm'] = self.graph.curveAtIndex(2*idx)
            self.graph.addYChannel(
                y_channel=self.prefix+wch, name=name+' W', color=color,
                lineStyle=Qt.SolidLine, lineWidth=1)
            self.curves[name+' W'] = self.graph.curveAtIndex(2*idx+1)

            idx += 1
        self.graph.setLabel('left', '')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addLayout(lay_table)
        lay.addWidget(self.graph)

        return lay

    def _handle_labels_units(self, text):
        for lb in self.cals_dbm:
            lb.setVisible(text == 'dBm')
        for lb in self.cals_w:
            lb.setVisible(text == 'W')

    def _handle_curves_units(self, text):
        for name in self.syst_dict:
            cbx = self.findChild(QCheckBox, name)
            visi = cbx.isChecked()
            curvew = self.curves[name + ' W']
            curvew.setVisible(text == 'W' and visi)
            curvedbm = self.curves[name + ' dBm']
            curvedbm.setVisible(text == 'dBm' and visi)

    def _handle_curves_visibility(self, state):
        name = self.sender().objectName()
        if name in self.syst_dict:
            name += ' ' + self.cb_units.currentText()
        curve = self.curves[name]
        curve.setVisible(state)
