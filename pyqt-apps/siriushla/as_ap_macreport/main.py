"""Machine reports."""

import numpy as _np

from qtpy.QtCore import Qt, Signal, QThread
from qtpy.QtWidgets import QWidget, QGridLayout, QGroupBox, QTabWidget, \
    QDateTimeEdit, QLabel, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox, QSpacerItem, QSizePolicy as QSzPlcy

import qtawesome as qta

from siriuspy.clientarch import Time
from siriuspy.machshift.macreport import MacReport

from ..widgets import SiriusMainWindow, MatplotlibWidget, SiriusDialog


class MacReportWindow(SiriusMainWindow):
    """Machine Report Window."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._macreport = MacReport()
        self._macreport.connector.timeout = 5*60

        self.setWindowIcon(qta.icon('fa5s.book', color='gray'))
        self.setWindowTitle('Machine Reports')

        self._fsi = '{:8d}'
        self._fs1 = '{:8.3f}'
        self._fs2 = '{:8.3f} ± {:8.3f}'
        self._fst1 = '{:02d}h{:02d}'
        self._fst2 = '{:02d}h{:02d} ± {:02d}h{:02d}'

        self._update_task = None

        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus(True)

    def _setupUi(self):
        cwid = QWidget(self)
        self.setCentralWidget(cwid)

        title = QLabel('<h3>Machine Reports</h3>', self,
                       alignment=Qt.AlignCenter)

        self._timesel_gbox = self._setupTimePeriodSelWidget()
        self._timesel_gbox.setObjectName('timesel_gbox')
        self._timesel_gbox.setStyleSheet(
            "#timesel_gbox{min-height: 8em; max-height: 8em;}")

        self._progress_list = QListWidget(self)
        self._progress_list.setObjectName('progress_list')
        self._progress_list.setStyleSheet(
            "#progress_list{min-height: 8em; max-height: 8em;}")

        self._reports_wid = QTabWidget(cwid)
        self._reports_wid.setObjectName('ASTab')
        self._reports_wid.addTab(
            self._setupUserShiftStatsWidget(), 'User Shift Stats')
        self._reports_wid.addTab(
            self._setupLightSourceUsageStats(), 'Light Source Usage Stats')
        self._reports_wid.addTab(
            self._setupStoredCurrentStats(), 'Stored Current Stats')

        self._pb_showraw = QPushButton(
            qta.icon('mdi.chart-line'), 'Show Raw Data', self)
        self._pb_showraw.setEnabled(False)
        self._pb_showraw.clicked.connect(self._show_raw_data)

        self._pb_showpvsd = QPushButton(
            qta.icon('mdi.chart-line'),
            'Show Progrmd.vs.Delivered Hours', self)
        self._pb_showpvsd.setEnabled(False)
        self._pb_showpvsd.clicked.connect(self._show_progmd_vs_delivd)

        lay = QGridLayout(cwid)
        lay.setVerticalSpacing(10)
        lay.setHorizontalSpacing(10)
        lay.setContentsMargins(18, 9, 18, 9)
        lay.addWidget(title, 0, 0, 1, 3)
        lay.addWidget(self._timesel_gbox, 1, 0)
        lay.addWidget(self._progress_list, 1, 1, 1, 2,
                      alignment=Qt.AlignBottom)
        lay.addWidget(self._reports_wid, 2, 0, 1, 3)
        lay.addWidget(self._pb_showpvsd, 4, 0, alignment=Qt.AlignLeft)
        lay.addWidget(self._pb_showraw, 4, 2, alignment=Qt.AlignRight)

        self._updateUserShiftStats(setup=True)
        self._updateStoredCurrentStats(setup=True)
        self._updateLightSourceUsageStats(setup=True)

    def _setupTimePeriodSelWidget(self):
        tnow = Time.now()

        ld_tstart = QLabel('Time start: ')
        self.dt_start = QDateTimeEdit(tnow-10*60, self)
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setMinimumDate(Time(2020, 1, 1))
        self.dt_start.setDisplayFormat('dd/MM/yyyy hh:mm')

        ld_tstop = QLabel('Time stop: ')
        self.dt_stop = QDateTimeEdit(tnow, self)
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

        wid = QGroupBox('Select interval: ', self)
        lay = QGridLayout(wid)
        lay.addWidget(ld_tstart, 0, 0)
        lay.addWidget(self.dt_start, 0, 1)
        lay.addWidget(ld_tstop, 1, 0)
        lay.addWidget(self.dt_stop, 1, 1)
        lay.addWidget(self.pb_search, 2, 1, alignment=Qt.AlignRight)
        return wid

    def _setupUserShiftStatsWidget(self):
        self.lb_uspt = LbData('')
        self.lb_usdt = LbData('')
        self.lb_ustt = LbData('')
        self.lb_uset = LbData('')
        self.lb_uspc = LbData('')
        self.lb_cav = LbData('')
        self.lb_cbav = LbData('')
        self.lb_ceav = LbData('')
        self.lb_tft = LbData('')
        self.lb_bdc = LbData('')
        self.lb_mttr = LbData('')
        self.lb_mtbf = LbData('')
        self.lb_reli = LbData('')
        self.lb_tsbt = LbData('')
        self.lb_tubt = LbData('')
        self.lb_mtbu = LbData('')
        self.lb_rsbt = LbData('')
        self.lb_itav = LbData('')

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.setVerticalSpacing(0)
        lay.setHorizontalSpacing(0)
        lay.setAlignment(Qt.AlignTop)
        lay.addItem(QSpacerItem(120, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 0)
        lay.addWidget(LbHHeader('Programmed Time (h)'), 0, 1)
        lay.addWidget(self.lb_uspt, 0, 2)
        lay.addWidget(LbHHeader('Delivered Time (h)'), 1, 1)
        lay.addWidget(self.lb_usdt, 1, 2)
        lay.addWidget(LbHHeader('Total Time (h)'), 2, 1)
        lay.addWidget(self.lb_ustt, 2, 2)
        lay.addWidget(LbHHeader('Extra Time (h)'), 3, 1)
        lay.addWidget(self.lb_uset, 3, 2)
        lay.addWidget(LbHHeader('# Programmed Shifts'), 4, 1)
        lay.addWidget(self.lb_uspc, 4, 2)
        lay.addWidget(LbHHeader('Current (avg ± std) (mA)'), 5, 1)
        lay.addWidget(self.lb_cav, 5, 2)
        lay.addWidget(LbHHeader(
            'Current at the Beg. of the Shift (avg ± std) (mA)'), 6, 1)
        lay.addWidget(self.lb_cbav, 6, 2)
        lay.addWidget(LbHHeader(
            'Current at the End of the Shift (avg ± std) (mA)'), 7, 1)
        lay.addWidget(self.lb_ceav, 7, 2)
        lay.addWidget(LbHHeader('Total Failures Time (h)'), 8, 1)
        lay.addWidget(self.lb_tft, 8, 2)
        lay.addWidget(LbHHeader('# Beam Dumps'), 9, 1)
        lay.addWidget(self.lb_bdc, 9, 2)
        lay.addWidget(LbHHeader('Time To Recover (avg ± std) (h)'), 10, 1)
        lay.addWidget(self.lb_mttr, 10, 2)
        lay.addWidget(LbHHeader('Time Between Failures (avg) (h)'), 11, 1)
        lay.addWidget(self.lb_mtbf, 11, 2)
        lay.addWidget(LbHHeader('Beam Reliability (%)'), 12, 1)
        lay.addWidget(self.lb_reli, 12, 2)
        lay.addWidget(LbHHeader('Total stable beam time (h)'), 13, 1)
        lay.addWidget(self.lb_tsbt, 13, 2)
        lay.addWidget(LbHHeader('Total unstable beam time (h)'), 14, 1)
        lay.addWidget(self.lb_tubt, 14, 2)
        lay.addWidget(LbHHeader(
            'Time between unstable beams (avg) (h)'), 15, 1)
        lay.addWidget(self.lb_mtbu, 15, 2)
        lay.addWidget(LbHHeader('Relative stable beam time (%)'), 16, 1)
        lay.addWidget(self.lb_rsbt, 16, 2)
        lay.addWidget(LbHHeader('Injection time (avg ± std) (h)'), 17, 1)
        lay.addWidget(self.lb_itav, 17, 2)
        lay.addItem(QSpacerItem(120, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 3)
        return wid

    def _updateUserShiftStats(self, setup=False):
        w2r = {
            'uspt': ['usershift_progmd_time', ],
            'usdt': ['usershift_delivd_time', ],
            'ustt': ['usershift_total_time', ],
            'uset': ['usershift_extra_time', ],
            'uspc': ['usershift_progmd_count', ],
            'cav': ['usershift_current_average',
                    'usershift_current_stddev'],
            'cbav': ['usershift_current_beg_average',
                     'usershift_current_beg_stddev'],
            'ceav': ['usershift_current_end_average',
                     'usershift_current_end_stddev'],
            'tft': ['usershift_total_failures_time', ],
            'bdc': ['usershift_beam_dump_count', ],
            'mttr': ['usershift_time_to_recover_average',
                     'usershift_time_to_recover_stddev'],
            'mtbf': ['usershift_time_between_failures_average', ],
            'reli': ['usershift_beam_reliability', ],
            'tsbt': ['usershift_total_stable_beam_time', ],
            'tubt': ['usershift_total_unstable_beam_time', ],
            'mtbu': ['usershift_time_between_unstable_beams_average'],
            'rsbt': ['usershift_relative_stable_beam_time'],
            'itav': ['usershift_injection_time_average',
                     'usershift_injection_time_stddev']}

        for wname, rname in w2r.items():
            wid = getattr(self, 'lb_'+wname)
            items = [getattr(self._macreport, n) for n in rname]
            if 'time' in rname[0] and 'relative' not in rname[0]:
                if len(items) == 2:
                    if items[0] not in [None, _np.inf]:
                        hour1 = int(items[0])
                        minu1 = int((items[0] - hour1)*60)
                        hour2 = int(items[1])
                        minu2 = int((items[1] - hour2)*60)
                        items = [hour1, minu1, hour2, minu2]
                        str2fmt = self._fst2
                    else:
                        str2fmt = self._fs1
                elif items[0] not in [None, _np.inf]:
                    hour = int(items[0])
                    minu = int((items[0] - hour)*60)
                    items = [hour, minu]
                    str2fmt = self._fst1
                else:
                    str2fmt = self._fs1
            else:
                str2fmt = getattr(
                    self, '_fsi' if 'count' in rname[0]
                    else '_fs'+str(len(rname)))
            text = '' if any([i is None for i in items]) \
                else str2fmt.format(*items)
            wid.setText(text)
            if setup:
                wid.setToolTip(getattr(MacReport, rname[0]).__doc__)

    def _setupStoredCurrentStats(self):
        self.lb_user_mb_avg = LbData('')
        self.lb_user_mb_intvl = LbData('')
        self.lb_user_sb_avg = LbData('')
        self.lb_user_sb_intvl = LbData('')
        self.lb_user_tt_avg = LbData('')
        self.lb_user_tt_intvl = LbData('')
        self.lb_commi_mb_avg = LbData('')
        self.lb_commi_mb_intvl = LbData('')
        self.lb_commi_sb_avg = LbData('')
        self.lb_commi_sb_intvl = LbData('')
        self.lb_commi_tt_avg = LbData('')
        self.lb_commi_tt_intvl = LbData('')
        self.lb_condi_mb_avg = LbData('')
        self.lb_condi_mb_intvl = LbData('')
        self.lb_condi_sb_avg = LbData('')
        self.lb_condi_sb_intvl = LbData('')
        self.lb_condi_tt_avg = LbData('')
        self.lb_condi_tt_intvl = LbData('')
        self.lb_mstdy_mb_avg = LbData('')
        self.lb_mstdy_mb_intvl = LbData('')
        self.lb_mstdy_sb_avg = LbData('')
        self.lb_mstdy_sb_intvl = LbData('')
        self.lb_mstdy_tt_avg = LbData('')
        self.lb_mstdy_tt_intvl = LbData('')
        self.lb_stord_mb_avg = LbData('')
        self.lb_stord_mb_intvl = LbData('')
        self.lb_stord_sb_avg = LbData('')
        self.lb_stord_sb_intvl = LbData('')
        self.lb_stord_tt_avg = LbData('')
        self.lb_stord_tt_intvl = LbData('')

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.setVerticalSpacing(0)
        lay.setHorizontalSpacing(0)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(LbHHeader(
            'Current (avg ± std) (mA) (MB)'), 1, 0)
        lay.addWidget(LbHHeader('Time in MB mode (h)'), 2, 0)
        lay.addWidget(LbHHeader(
            'Current (avg ± std) (mA) (SB)'), 3, 0)
        lay.addWidget(LbHHeader('Time in SB mode (h)'), 4, 0)
        lay.addWidget(LbHHeader(
            'Current (avg ± std) (mA) (SB+MB)'), 5, 0)
        lay.addWidget(LbHHeader('Total Time (h) (SB+MB)'), 6, 0)
        lay.addWidget(LbVHeader('Users'), 0, 1)
        lay.addWidget(self.lb_user_mb_avg, 1, 1)
        lay.addWidget(self.lb_user_mb_intvl, 2, 1)
        lay.addWidget(self.lb_user_sb_avg, 3, 1)
        lay.addWidget(self.lb_user_sb_intvl, 4, 1)
        lay.addWidget(self.lb_user_tt_avg, 5, 1)
        lay.addWidget(self.lb_user_tt_intvl, 6, 1)
        lay.addWidget(LbVHeader('Commissioning'), 0, 2)
        lay.addWidget(self.lb_commi_mb_avg, 1, 2)
        lay.addWidget(self.lb_commi_mb_intvl, 2, 2)
        lay.addWidget(self.lb_commi_sb_avg, 3, 2)
        lay.addWidget(self.lb_commi_sb_intvl, 4, 2)
        lay.addWidget(self.lb_commi_tt_avg, 5, 2)
        lay.addWidget(self.lb_commi_tt_intvl, 6, 2)
        lay.addWidget(LbVHeader('Conditioning'), 0, 3)
        lay.addWidget(self.lb_condi_mb_avg, 1, 3)
        lay.addWidget(self.lb_condi_mb_intvl, 2, 3)
        lay.addWidget(self.lb_condi_sb_avg, 3, 3)
        lay.addWidget(self.lb_condi_sb_intvl, 4, 3)
        lay.addWidget(self.lb_condi_tt_avg, 5, 3)
        lay.addWidget(self.lb_condi_tt_intvl, 6, 3)
        lay.addWidget(LbVHeader('Machine Study'), 0, 4)
        lay.addWidget(self.lb_mstdy_mb_avg, 1, 4)
        lay.addWidget(self.lb_mstdy_mb_intvl, 2, 4)
        lay.addWidget(self.lb_mstdy_sb_avg, 3, 4)
        lay.addWidget(self.lb_mstdy_sb_intvl, 4, 4)
        lay.addWidget(self.lb_mstdy_tt_avg, 5, 4)
        lay.addWidget(self.lb_mstdy_tt_intvl, 6, 4)
        lay.addWidget(LbVHeader('All Stored Beam'), 0, 5)
        lay.addWidget(self.lb_stord_mb_avg, 1, 5)
        lay.addWidget(self.lb_stord_mb_intvl, 2, 5)
        lay.addWidget(self.lb_stord_sb_avg, 3, 5)
        lay.addWidget(self.lb_stord_sb_intvl, 4, 5)
        lay.addWidget(self.lb_stord_tt_avg, 5, 5)
        lay.addWidget(self.lb_stord_tt_intvl, 6, 5)
        return wid

    def _updateStoredCurrentStats(self, setup=False):
        shifttype = {
            'mstdy': 'machinestudy',
            'commi': 'commissioning',
            'condi': 'conditioning',
            'stord': 'ebeam',
            'user': 'users'}
        fillmode = {
            'mb': 'multibunch',
            'sb': 'singlebunch',
            'tt': 'total'}
        stats = {
            'avg': ['average', 'stddev'],
            'intvl': ['time', ]}

        for wsht, rsht in shifttype.items():
            for wfm, rfm in fillmode.items():
                for wstt, rstt in stats.items():
                    wid = getattr(self, 'lb_'+wsht+'_'+wfm+'_'+wstt)
                    pname = 'current_'+rsht+'_'+rfm+'_'
                    items = [getattr(self._macreport, pname+i)
                             for i in rstt]
                    if 'time' in rstt[0] and items[0] is not None:
                        hour = int(items[0])
                        minu = int((items[0] - hour)*60)
                        items = [hour, minu]
                    str2fmt = getattr(
                        self, '_fst1' if ('time' in rstt[0])
                        else '_fs'+str(len(rstt)))
                    text = '' if any([i is None for i in items]) \
                        else str2fmt.format(*items)
                    wid.setText(text)
                    if setup:
                        wid.setToolTip(
                            getattr(MacReport, pname + rstt[0]).__doc__)

    def _setupLightSourceUsageStats(self):
        self.lb_mstdy_fail_intvl = LbData('')
        self.lb_mstdy_fail_pcntl = LbData('')
        self.lb_mstdy_oper_intvl = LbData('')
        self.lb_mstdy_oper_pcntl = LbData('')
        self.lb_mstdy_total_intvl = LbData('')
        self.lb_mstdy_total_pcntl = LbData('')
        self.lb_commi_fail_intvl = LbData('')
        self.lb_commi_fail_pcntl = LbData('')
        self.lb_commi_oper_intvl = LbData('')
        self.lb_commi_oper_pcntl = LbData('')
        self.lb_commi_total_intvl = LbData('')
        self.lb_commi_total_pcntl = LbData('')
        self.lb_condi_fail_intvl = LbData('')
        self.lb_condi_fail_pcntl = LbData('')
        self.lb_condi_oper_intvl = LbData('')
        self.lb_condi_oper_pcntl = LbData('')
        self.lb_condi_total_intvl = LbData('')
        self.lb_condi_total_pcntl = LbData('')
        self.lb_maint_fail_intvl = LbData('')
        self.lb_maint_fail_pcntl = LbData('')
        self.lb_maint_oper_intvl = LbData('')
        self.lb_maint_oper_pcntl = LbData('')
        self.lb_maint_total_intvl = LbData('')
        self.lb_maint_total_pcntl = LbData('')
        self.lb_user_fail_intvl = LbData('')
        self.lb_user_fail_pcntl = LbData('')
        self.lb_user_oper_intvl = LbData('')
        self.lb_user_oper_pcntl = LbData('')
        self.lb_user_total_intvl = LbData('')
        self.lb_user_total_pcntl = LbData('')
        self.lb_total_intvl = LbHHeader('Total Usage Time (h): - ')

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.setVerticalSpacing(0)
        lay.setHorizontalSpacing(0)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(LbHHeader('Operational Time (h)'), 1, 0)
        lay.addWidget(LbHHeader('Operational Percentage (%)'), 2, 0)
        lay.addWidget(LbHHeader('Failures Time (h)'), 3, 0)
        lay.addWidget(LbHHeader('Failures Percentage (%)'), 4, 0)
        lay.addWidget(LbHHeader('Shift Time (h)'), 5, 0)
        lay.addWidget(LbHHeader('Shift Percentage (%)'), 6, 0)
        lay.addWidget(self.lb_total_intvl, 7, 0, 1, 6)
        lay.addWidget(LbVHeader('Users'), 0, 1)
        lay.addWidget(self.lb_user_oper_intvl, 1, 1)
        lay.addWidget(self.lb_user_oper_pcntl, 2, 1)
        lay.addWidget(self.lb_user_fail_intvl, 3, 1)
        lay.addWidget(self.lb_user_fail_pcntl, 4, 1)
        lay.addWidget(self.lb_user_total_intvl, 5, 1)
        lay.addWidget(self.lb_user_total_pcntl, 6, 1)
        lay.addWidget(LbVHeader('Commissioning'), 0, 2)
        lay.addWidget(self.lb_commi_oper_intvl, 1, 2)
        lay.addWidget(self.lb_commi_oper_pcntl, 2, 2)
        lay.addWidget(self.lb_commi_fail_intvl, 3, 2)
        lay.addWidget(self.lb_commi_fail_pcntl, 4, 2)
        lay.addWidget(self.lb_commi_total_intvl, 5, 2)
        lay.addWidget(self.lb_commi_total_pcntl, 6, 2)
        lay.addWidget(LbVHeader('Conditioning'), 0, 3)
        lay.addWidget(self.lb_condi_oper_intvl, 1, 3)
        lay.addWidget(self.lb_condi_oper_pcntl, 2, 3)
        lay.addWidget(self.lb_condi_fail_intvl, 3, 3)
        lay.addWidget(self.lb_condi_fail_pcntl, 4, 3)
        lay.addWidget(self.lb_condi_total_intvl, 5, 3)
        lay.addWidget(self.lb_condi_total_pcntl, 6, 3)
        lay.addWidget(LbVHeader('Machine Study'), 0, 4)
        lay.addWidget(self.lb_mstdy_oper_intvl, 1, 4)
        lay.addWidget(self.lb_mstdy_oper_pcntl, 2, 4)
        lay.addWidget(self.lb_mstdy_fail_intvl, 3, 4)
        lay.addWidget(self.lb_mstdy_fail_pcntl, 4, 4)
        lay.addWidget(self.lb_mstdy_total_intvl, 5, 4)
        lay.addWidget(self.lb_mstdy_total_pcntl, 6, 4)
        lay.addWidget(LbVHeader('Maintenance'), 0, 5)
        lay.addWidget(self.lb_maint_oper_intvl, 1, 5)
        lay.addWidget(self.lb_maint_oper_pcntl, 2, 5)
        lay.addWidget(self.lb_maint_fail_intvl, 3, 5)
        lay.addWidget(self.lb_maint_fail_pcntl, 4, 5)
        lay.addWidget(self.lb_maint_total_intvl, 5, 5)
        lay.addWidget(self.lb_maint_total_pcntl, 6, 5)
        return wid

    def _updateLightSourceUsageStats(self, setup=False):
        shifttype = {
            'mstdy': 'machinestudy',
            'commi': 'commissioning',
            'condi': 'conditioning',
            'maint': 'maintenance',
            'user': 'users'}
        intervaltype = {
            'fail': '_failures',
            'oper': '_operational',
            'total': ''}
        for wst, rst in shifttype.items():
            for wit, rit in intervaltype.items():
                widt = getattr(self, 'lb_'+wst+'_'+wit+'_intvl')
                tname = 'lsusage_'+rst+rit+'_time'
                tval = getattr(self._macreport, tname)
                if tval is None:
                    text = ''
                else:
                    hour = int(tval)
                    minu = int((tval - hour)*60)
                    text = self._fst1.format(hour, minu)
                widt.setText(text)
                if setup:
                    widt.setToolTip(getattr(MacReport, tname).__doc__)

                widp = getattr(self, 'lb_'+wst+'_'+wit+'_pcntl')
                pname = 'lsusage_'+rst+rit
                pval = getattr(self._macreport, pname)
                text = '' if pval is None else self._fs1.format(pval)
                widp.setText(text)
                if setup:
                    widp.setToolTip(getattr(MacReport, pname).__doc__)

        text = 'Total Usage Time (h): '
        if self._macreport.lsusage_total_time is not None:
            val = self._macreport.lsusage_total_time
            hour = int(val)
            minu = int((val - hour)*60)
            text += self._fst1.format(hour, minu)
        self.lb_total_intvl.setText(text)

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

            self._macreport.timestamp_start = \
                self.dt_start.dateTime().toSecsSinceEpoch()
            self._macreport.timestamp_stop = \
                self.dt_stop.dateTime().toSecsSinceEpoch()

            self._progress_list.clear()
            self._pb_showraw.setEnabled(False)
            self._pb_showpvsd.setEnabled(False)
            self._setup_search_button()

            self._update_task = UpdateTask(self._macreport)
            self._update_task.updated.connect(self._update_progress)
            self._update_task.start()

    def _update_progress(self, message):
        item = QListWidgetItem(message)
        self._progress_list.addItem(item)
        self._progress_list.scrollToBottom()

        if 'Collected' in message:
            self._setup_search_button()
            self._updateUserShiftStats()
            self._updateStoredCurrentStats()
            self._updateLightSourceUsageStats()
            self._pb_showraw.setEnabled(True)
            self._pb_showpvsd.setEnabled(True)

    def _setup_search_button(self):
        if self.pb_search.text() == 'Abort':
            self.pb_search.setIcon(qta.icon('fa5s.search'))
            self.pb_search.setText('Search')
        else:
            self.pb_search.setIcon(
                qta.icon('fa5s.spinner', animation=qta.Spin(self.pb_search)))
            self.pb_search.setText('Abort')

    def _show_raw_data(self):
        dialog = SiriusDialog()
        dialog.setWindowTitle(
            'Machine Reports - Raw Data (' +
            str(self._macreport.time_start) + ' -> ' +
            str(self._macreport.time_stop) + ')')
        dialog.setWindowIcon(self.windowIcon())
        fig = self._macreport.plot_raw_data()
        wid = MatplotlibWidget(fig)
        lay = QGridLayout(dialog)
        lay.addWidget(wid)
        dialog.exec_()

    def _show_progmd_vs_delivd(self):
        dialog = SiriusDialog()
        dialog.setWindowTitle(
            'Machine Reports - Programmed vs. Delivered Hours (' +
            str(self._macreport.time_start) + ' -> ' +
            str(self._macreport.time_stop) + ')')
        fig = self._macreport.plot_progmd_vs_delivd_hours()
        wid = MatplotlibWidget(fig)
        lay = QGridLayout(dialog)
        lay.addWidget(wid)
        dialog.exec_()


class UpdateTask(QThread):
    """Update task."""

    updated = Signal(str)

    def __init__(self, macreport, parent=None):
        """Init."""
        super().__init__(parent)
        self.macreport = macreport
        self.macreport.logger = self
        self._quit_task = False

    def exit_task(self):
        """Set flag to quit thread."""
        self._quit_task = True

    def run(self):
        """Run task."""
        if not self._quit_task:
            self.macreport.update()
            self.update('Collected data from archiver and machine schedule.')

    def update(self, message):
        """Send log."""
        now = Time.now().strftime('%Y/%m/%d-%H:%M:%S')
        self.updated.emit(now+'  '+message)


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
