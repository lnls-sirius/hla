"""Orbit Scores."""

from qtpy.QtCore import Qt, Signal, QThread
from qtpy.QtWidgets import QWidget, QGridLayout, QGroupBox, QVBoxLayout, \
    QDateTimeEdit, QLabel, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox, QFrame, QSpacerItem, QSizePolicy as QSzPlcy

import qtawesome as qta

from siriuspy.clientarch import Time
from siriuspy.machshift.orbscore import OrbitScore

from ..widgets import SiriusMainWindow, MatplotlibWidget, QDoubleSpinBoxPlus


class OrbitScoreWindow(SiriusMainWindow):
    """Orbit Score Window."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._orbscore = OrbitScore()
        self._orbscore.connector.timeout = 5*60

        self.setWindowIcon(qta.icon('fa.book', color='gray'))
        self.setWindowTitle('Orbit Scores')

        self._fs = '{:10.2f}'

        self._update_task = None

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus(True)

    def _setupUi(self):
        cwid = QWidget(self)
        self.setCentralWidget(cwid)

        title = QLabel('<h3>Orbit Scores</h3>', self,
                       alignment=Qt.AlignCenter)

        self._timesel_gbox = self._setupTimePeriodSelWidget()
        self._timesel_gbox.setObjectName('timesel_gbox')
        self._timesel_gbox.setStyleSheet(
            "#timesel_gbox{min-height: 8em; max-height: 8em;}")

        self._progress_list = QListWidget(self)
        self._progress_list.setObjectName('progress_list')
        self._progress_list.setStyleSheet(
            "#progress_list{min-height: 8em; max-height: 8em;}")

        self._orbscore_wid = self._setupScoresWidget()

        self._pb_showscore = QPushButton(
            qta.icon('mdi.chart-line'), 'Show Fit Data', self)
        self._pb_showscore.setEnabled(False)
        self._pb_showscore.clicked.connect(self._show_score_data)

        self._pb_showraw = QPushButton(
            qta.icon('mdi.chart-line'), 'Show Raw Data', self)
        self._pb_showraw.setEnabled(False)
        self._pb_showraw.clicked.connect(self._show_raw_data)

        lay = QGridLayout(cwid)
        lay.setVerticalSpacing(10)
        lay.setHorizontalSpacing(10)
        lay.setContentsMargins(18, 9, 18, 9)
        lay.addWidget(title, 0, 0, 1, 3)
        lay.addWidget(self._timesel_gbox, 1, 0)
        lay.addWidget(self._progress_list, 1, 1, 1, 2,
                      alignment=Qt.AlignBottom)
        lay.addWidget(self._orbscore_wid, 2, 0, 1, 3)
        lay.addWidget(self._pb_showscore, 3, 0, alignment=Qt.AlignLeft)
        lay.addWidget(self._pb_showraw, 3, 2, alignment=Qt.AlignRight)

        self._updateScoresWidget(setup=True)
        for wname, rname in self._widget2attr.items():
            wid = getattr(self, 'wid_'+wname)
            if isinstance(wid, SbData):
                wid.editingFinished.connect(self._updateOrbScoreParams)

    def _setupTimePeriodSelWidget(self):
        tstart = Time(2021, 10, 27, 8, 15)
        tstop = Time(2021, 10, 27, 20, 0)

        ld_tstart = QLabel('Time start: ')
        self.dt_start = QDateTimeEdit(tstart, self)
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setMinimumDate(Time(2020, 1, 1))
        self.dt_start.setDisplayFormat('dd/MM/yyyy hh:mm')

        ld_tstop = QLabel('Time stop: ')
        self.dt_stop = QDateTimeEdit(tstop, self)
        self.dt_stop.setCalendarPopup(True)
        self.dt_stop.setMinimumDate(Time(2020, 1, 1))
        self.dt_stop.setDisplayFormat('dd/MM/yyyy hh:mm')

        self.pb_search = QPushButton(qta.icon('fa5s.search'), 'Search', self)
        self.pb_search.clicked.connect(self._do_update)
        self.pb_search.setObjectName('pb_search')
        self.pb_search.setStyleSheet("""
            #pb_search{
                min-width:100px; max-width:100px;
                min-height:25px; max-height:25px;
                icon-size:20px;}
        """)

        wid = QGroupBox('Select shift interval: ', self)
        lay = QGridLayout(wid)
        lay.addWidget(ld_tstart, 0, 0)
        lay.addWidget(self.dt_start, 0, 1)
        lay.addWidget(ld_tstop, 1, 0)
        lay.addWidget(self.dt_stop, 1, 1)
        lay.addWidget(self.pb_search, 2, 1, alignment=Qt.AlignRight)
        return wid

    def _setupScoresWidget(self):
        self._widget2attr = {
            'thr_currt': 'thold_isstored',
            'deg_sdrft': 'slowdrift_polyfit_deg',
            'thr_sdrft': 'slowdrift_thold',
            'thr_mepos': 'meanpos_thold',
            'goa_totsd': 'slowdrift_tottime_goal',
            'goa_consd': 'slowdrift_conttime_goal',
            'goa_ampsd': 'slowdrift_ampli_goal',
            'goa_mepos': 'meanpos_goal',
            'wei_totsd': 'slowdrift_tottime_weight',
            'wei_consd': 'slowdrift_conttime_weight',
            'wei_ampsd': 'slowdrift_ampli_weight',
            'wei_mepos': 'meanpos_weight',
            'ach_totsd': 'slowdrift_tottime_achieved',
            'ach_consd': 'slowdrift_conttime_achieved',
            'ach_ampsd': 'slowdrift_ampli_achieved',
            'ach_mepos': 'meanpos_achieved',
            'sco_totsd': 'slowdrift_tottime_score',
            'sco_consd': 'slowdrift_conttime_score',
            'sco_ampsd': 'slowdrift_ampli_score',
            'sco_mepos': 'meanpos_score',
            'sco_total': 'total_score',
        }

        self.wid_thr_currt = SbData(dec=3, mini=0, maxi=350)
        self.wid_deg_sdrft = SbData(mini=0, maxi=100)
        self.wid_thr_sdrft = SbData(mini=0, maxi=1e7)
        self.wid_thr_mepos = SbData(mini=0, maxi=1e7)
        self.wid_wei_totsd = SbData(mini=0, maxi=100)
        self.wid_wei_consd = SbData(mini=0, maxi=100)
        self.wid_wei_ampsd = SbData(mini=0, maxi=100)
        self.wid_wei_mepos = SbData(mini=0, maxi=100)
        self.wid_goa_totsd = SbData(dec=2, mini=0, maxi=1)
        self.wid_goa_consd = SbData(dec=2, mini=0, maxi=1)
        self.wid_goa_ampsd = SbData(mini=0, maxi=1e7)
        self.wid_goa_mepos = SbData(mini=0, maxi=1e7)
        self.wid_ach_totsd = LbData('')
        self.wid_ach_consd = LbData('')
        self.wid_ach_ampsd = LbData('')
        self.wid_ach_mepos = LbData('')
        self.wid_sco_totsd = LbData('')
        self.wid_sco_consd = LbData('')
        self.wid_sco_ampsd = LbData('')
        self.wid_sco_mepos = LbData('')
        self.wid_sco_total = LbData('')

        for wname in self._widget2attr:
            wid = getattr(self, 'wid_'+wname)
            if isinstance(wid, SbData):
                wid.setObjectId(wname)

        play = QGridLayout()
        play.setVerticalSpacing(0)
        play.setHorizontalSpacing(0)
        play.setAlignment(Qt.AlignTop)
        play.addItem(
            QSpacerItem(10, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 0)
        play.addWidget(LbVHeader('Parameter'), 0, 1)
        play.addWidget(LbVHeader('Value'), 0, 2)
        play.addWidget(LbHHeader(
            'Stored beam threshold current (mA)'), 1, 1)
        play.addWidget(self.wid_thr_currt, 1, 2)
        play.addWidget(LbHHeader(
            'Slow Drift polynomial fit degree'), 2, 1)
        play.addWidget(self.wid_deg_sdrft, 2, 2)
        play.addWidget(LbHHeader(
            'Threshold for window around slow drift scores (count)'), 3, 1)
        play.addWidget(self.wid_thr_sdrft, 3, 2)
        play.addWidget(LbHHeader(
            'Threshold for mean position score (count)'), 4, 1)
        play.addWidget(self.wid_thr_mepos, 4, 2)
        play.addItem(
            QSpacerItem(10, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 3)

        slay = QGridLayout()
        slay.setVerticalSpacing(0)
        slay.setHorizontalSpacing(0)
        slay.setAlignment(Qt.AlignTop)
        slay.addItem(
            QSpacerItem(10, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 0)
        slay.addWidget(LbVHeader('Weight'), 0, 1)
        slay.addWidget(self.wid_wei_totsd, 1, 1)
        slay.addWidget(self.wid_wei_consd, 2, 1)
        slay.addWidget(self.wid_wei_ampsd, 3, 1)
        slay.addWidget(self.wid_wei_mepos, 4, 1)
        slay.addWidget(LbVHeader('Description'), 0, 2)
        slay.addWidget(LbHHeader(
            'Total time in a window around slow drift (%)'), 1, 2)
        slay.addWidget(LbHHeader(
            'Max.cont. time in a window around slow drift (%)'), 2, 2)
        slay.addWidget(LbHHeader(
            'Slow Drift Amplitude (counts)'), 3, 2)
        slay.addWidget(LbHHeader(
            'Mean Orbit Position (counts)'), 4, 2)
        slay.addWidget(LbVHeader('Goal'), 0, 3)
        slay.addWidget(self.wid_goa_totsd, 1, 3)
        slay.addWidget(self.wid_goa_consd, 2, 3)
        slay.addWidget(self.wid_goa_ampsd, 3, 3)
        slay.addWidget(self.wid_goa_mepos, 4, 3)
        slay.addWidget(LbVHeader('Achieved'), 0, 4)
        slay.addWidget(self.wid_ach_totsd, 1, 4)
        slay.addWidget(self.wid_ach_consd, 2, 4)
        slay.addWidget(self.wid_ach_ampsd, 3, 4)
        slay.addWidget(self.wid_ach_mepos, 4, 4)
        slay.addWidget(LbVHeader('Score'), 0, 5)
        slay.addWidget(self.wid_sco_totsd, 1, 5)
        slay.addWidget(self.wid_sco_consd, 2, 5)
        slay.addWidget(self.wid_sco_ampsd, 3, 5)
        slay.addWidget(self.wid_sco_mepos, 4, 5)
        slay.addItem(QSpacerItem(1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed), 5, 5)
        slay.addWidget(self.wid_sco_total, 6, 5)
        slay.addItem(
            QSpacerItem(10, 1, QSzPlcy.Expanding, QSzPlcy.Ignored), 0, 6)
        wid = QWidget(self)
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addStretch()
        lay.addLayout(play)
        lay.addStretch()
        lay.addLayout(slay)
        lay.addStretch()
        return wid

    def _updateScoresWidget(self, setup=False):
        for wname, rname in self._widget2attr.items():
            wid = getattr(self, 'wid_'+wname)
            item = getattr(self._orbscore, rname)
            if isinstance(wid, LbData):
                text = '' if item is None else self._fs.format(item)
                wid.setText(text)
            else:
                wid.setValue(item)
            if setup:
                wid.setToolTip(getattr(OrbitScore, rname).__doc__)

    def _updateOrbScoreParams(self):
        w_id = self.sender().id
        value = self.sender().value()
        rname = self._widget2attr[w_id]
        setattr(self._orbscore, rname, value)
        self._updateScoresWidget()

    def _do_update(self):
        if self.sender().text() == 'Abort':
            self._update_task.terminate()
            now = Time.now().strftime('%Y/%m/%d-%H:%M:%S')
            item = QListWidgetItem(now + '  Aborted.')
            self._progress_list.addItem(item)
            self._progress_list.scrollToBottom()
            self._setup_search_button()
        else:
            if self.dt_start.dateTime() >= self.dt_stop.dateTime() or \
                    self.dt_start.dateTime() > Time.now() or \
                    self.dt_stop.dateTime() > Time.now():
                QMessageBox.warning(
                    self, 'Ops...', 'Insert a valid time interval.')
                return

            self._orbscore.timestamp_start = \
                self.dt_start.dateTime().toSecsSinceEpoch()
            self._orbscore.timestamp_stop = \
                self.dt_stop.dateTime().toSecsSinceEpoch()

            self._progress_list.clear()
            self._pb_showscore.setEnabled(False)
            self._pb_showraw.setEnabled(False)
            self._setup_search_button()

            self._update_task = UpdateTask(self._orbscore)
            self._update_task.updated.connect(self._update_progress)
            self._update_task.start()

    def _update_progress(self, message):
        item = QListWidgetItem(message)
        self._progress_list.addItem(item)
        self._progress_list.scrollToBottom()

        if 'Collected' in message:
            self._setup_search_button()
            self._updateScoresWidget()
            self._pb_showscore.setEnabled(True)
            self._pb_showraw.setEnabled(True)

    def _setup_search_button(self):
        if self.pb_search.text() == 'Abort':
            self.pb_search.setIcon(qta.icon('fa5s.search'))
            self.pb_search.setText('Search')
        else:
            self.pb_search.setIcon(
                qta.icon('fa5s.spinner', animation=qta.Spin(self.pb_search)))
            self.pb_search.setText('Abort')

    def _show_score_data(self):
        fig = self._orbscore.plot_score_data()[0]
        wid = MatplotlibWidget(fig)
        wid.setWindowTitle(
            'Orbit Score - Fit/Score Data (' +
            str(self._orbscore.time_start) + ' -> ' +
            str(self._orbscore.time_stop) + ')')
        wid.show()

    def _show_raw_data(self):
        fig = self._orbscore.plot_raw_data()[0]
        wid = MatplotlibWidget(fig)
        wid.setWindowTitle(
            'Orbit Score - Raw Data (' +
            str(self._orbscore.time_start) + ' -> ' +
            str(self._orbscore.time_stop) + ')')
        wid.show()


class UpdateTask(QThread):
    """Update task."""

    updated = Signal(str)

    def __init__(self, orbscore, parent=None):
        """Init."""
        super().__init__(parent)
        self.orbscore = orbscore
        self.orbscore.logger = self
        self._quit_task = False

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Run task."""
        if not self._quit_task:
            self.orbscore.update()
            self.update('Collected data from archiver and machine schedule.')

    def update(self, message):
        """Send log."""
        now = Time.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message)


class SbData(QFrame):
    """Input spinbox."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__()
        self.setObjectName('sbdata')
        self.setStyleSheet("""
            #sbdata{
                border: 1px solid gray;
                min-height: 2em; max-height: 3em;
                min-width: 8em;
        }""")

        dec = kwargs.pop('dec') if 'dec' in kwargs else 0
        mini = kwargs.pop('mini') if 'mini' in kwargs else 0
        maxi = kwargs.pop('maxi') if 'maxi' in kwargs else 1e8
        self.sb = QDoubleSpinBoxPlus(*args, **kwargs)
        self.sb.setDecimals(dec)
        self.sb.setRange(mini, maxi)
        self.sb.setObjectName('sb')
        self.sb.setStyleSheet("""
            #sb{
                min-height: 1.8em; max-height: 2.8em;
                min-width: 8em;
                qproperty-alignment: 'AlignVCenter | AlignRight';
        }""")
        self.editingFinished = self.sb.editingFinished

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.sb, alignment=Qt.AlignTop)

    def value(self):
        return self.sb.value()

    def setValue(self, value):
        self.sb.setValue(value)

    def setObjectId(self, id):
        self.sb.id = id


class LbData(QLabel):
    """Data label."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.setObjectName('lbdata')
        self.setStyleSheet("""
            #lbdata{
                border: 1px solid gray;
                min-height: 2em; max-height: 3em;
                min-width: 8em;
                qproperty-alignment: 'AlignVCenter | AlignRight';
        }""")


class LbVHeader(QLabel):
    """Vertical Header label."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            LbVHeader{
                border: 1px solid gray;
                min-height: 2em; max-height: 3em;
                min-width: 6em;
                qproperty-alignment: 'AlignVCenter | AlignHCenter';
                font-weight: bold;
                background-color: darkGray;
        }""")


class LbHHeader(QLabel):
    """Horizontal Header label."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            LbHHeader{
                border: 1px solid gray;
                min-height: 2em; max-height: 3em;
                min-width: 6em;
                qproperty-alignment: 'AlignVCenter | AlignLeft';
                font-weight: bold;
                background-color: lightGray;
        }""")
