"""RaBPM monitor window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, \
    QHBoxLayout, QSpacerItem, QSizePolicy as QSzPlcy

import qtawesome as qta

from siriuspy.namesys import SiriusPVName
from siriuspy.search import LLTimeSearch
from siriuspy.devices.afc_acq_core import AMCCtrlAcqBase

from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, QLed
from .util import SEC_2_SLOT
from .custom_widgets import BPMMonLed, RFFEMonLed, PBPMMonLed, \
    EVRMonLed, FOFBCtrlMonLed, FRUMonLed


class RaBPMMonitor(SiriusMainWindow):
    """RaBPM monitor."""

    PBPM_MAXCOUNT_PERSEC = 4
    PBPM_ID_MAXCOUNT_PERSEC = 2

    def __init__(self, parent, prefix=''):
        super().__init__(parent)
        self.prefix = prefix

        self.setWindowIcon(
            qta.icon('mdi.developer-board', color=get_appropriate_color('AS')))
        self.setWindowTitle('RaBPM Monitor')
        self.setObjectName('ASApp')

        self.amc_devices = AMCCtrlAcqBase.DEVICES
        self.crates_mapping = LLTimeSearch.get_crates_mapping()
        self.sec2slot = SEC_2_SLOT
        self.sec2group = dict()
        for sec, slots in self.sec2slot.items():
            groups = dict()
            for sidx, slot in enumerate(slots):
                if not slot:
                    continue
                if slot[0] not in groups:
                    groups[slot[0]] = dict()
                    groups[slot[0]]['slots'] = list()
                    groups[slot[0]]['row'] = sidx
                groups[slot[0]]['slots'].append(slot[1])
            self.sec2group[sec] = groups

        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h3>RaBPM Monitor</h3>', self, alignment=Qt.AlignCenter)
        self.title.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        self.monitor = self._setupMonitorWidget()

        self.legend = self._setupLegendWidget()

        cwid = QWidget()
        layout = QVBoxLayout(cwid)
        layout.addWidget(self.title)
        layout.addWidget(self.monitor)
        layout.addItem(QSpacerItem(1, 15, QSzPlcy.Preferred, QSzPlcy.Fixed))
        layout.addWidget(self.legend)
        self.setCentralWidget(cwid)

    def _setupMonitorWidget(self):
        monitor = QWidget()
        grid = QGridLayout(monitor)
        grid.setVerticalSpacing(1)
        grid.setHorizontalSpacing(1)

        # # headers
        # create labels with subsector description
        for sec, row in {'SI': 0, 'BO': 21}.items():
            txt = sec + ' Subsector' + ('' if sec == 'SI' else ' (N)')
            label = QLabel(f'<h4>{txt}</h4>', self, alignment=Qt.AlignCenter)
            label.setObjectName('sec')
            label.setStyleSheet('#sec{border: 1px solid gray;}')
            grid.addWidget(label, row, 0)

        for sec in self.sec2group:
            # labels size for headers
            minw = '6' if sec == 'IA' else '4'
            # columns of IA and TL headers
            col = 0 if sec == 'IA' else 23
            # header layout, whether to right or left reading
            colgroup = int(not sec == 'IA')
            coldescs = int(sec == 'IA')

            # create headers
            for group, data in self.sec2group[sec].items():
                # do not show timing header for TL
                if sec == 'TL' and group == 'Timing':
                    continue

                # group label
                lbl = QLabel(
                    group.replace(' ', '\n'), self, alignment=Qt.AlignCenter)
                lbl.setObjectName('cont')

                # subgroup labels
                dsc = QWidget()
                dsc.setObjectName('cont')
                dlay = QVBoxLayout(dsc)
                dlay.setContentsMargins(0, 0, 0, 0)
                descs = data['slots']
                for dtxt in descs:
                    dlay.addWidget(
                        QLabel(dtxt.replace(' ', '\n'), self,
                               alignment=Qt.AlignCenter))

                # group header widgets
                wid = QWidget()
                wid.setStyleSheet(  # add borders here
                    'QLabel{font-weight: bold;}'
                    '#cont{min-width:'+minw+'em; border:1px solid gray;}')
                gbox = QGridLayout(wid)
                gbox.setContentsMargins(0, 0, 0, 0)
                gbox.setSpacing(1)
                gbox.addWidget(lbl, 0, colgroup, len(descs), 1)
                gbox.addWidget(dsc, 0, coldescs, len(descs), 1)
                grid.addWidget(wid, data['row'] + 1, col, len(descs), 1)

        # # led grid
        bobpm_n = 1
        for afc, devs in self.crates_mapping.items():
            amc = self.amc_devices
            sub = int(afc.sub[:2]) - 1
            amc_sub = amc[sub]
            
            # get devices
            afc = SiriusPVName(afc)
            devices = [afc] + [SiriusPVName(d) for d in devs]
            amcdevs = [SiriusPVName(a) for a in amc_sub]
        
            # determine sector, rabpm name and grid column
            sec = 'IA' if afc.sub[-2:] != 'TL' else 'TL'
            rabpm = afc.sub[:2] if sec == 'IA' else 'TL'
            col = 21 if sec == 'TL' else int(rabpm)

            # add SI subsector header
            label = QLabel(
                '<h4>'+rabpm+'</h4>', self, alignment=Qt.AlignCenter)
            label.setObjectName('siheader')
            label.setStyleSheet('#siheader{border: 1px solid gray;}')
            grid.addWidget(label, 0, col)

            # create layouts with borders for each group
            group2lay = dict()
            for group, data in self.sec2group[sec].items():
                wid = QWidget()
                wid.setObjectName('cell')
                wid.setStyleSheet('#cell{border: 1px solid gray;}')
                if group == 'Photon BPM':
                    lay = QGridLayout(wid)
                else:
                    lay = QVBoxLayout(wid)
                lay.setSpacing(2)
                lay.setContentsMargins(0, 1 if 'BO' in group else 0, 0, 0)
                lay.setAlignment(Qt.AlignHCenter)
                group2lay[group] = lay
                grid.addWidget(
                    wid, data['row'] + 1, col, len(data['slots']), 1)

            # populate layouts with device monitor widgets
            bobpm_cnt = 0
            for dev in devices:
                wid = self._get_monitor_widget(dev)
                if dev.endswith('EVR'):
                    group2lay['Timing'].addWidget(wid)
                elif dev.dev == 'FOFBCtrl':
                    group2lay['FOFB'].addWidget(wid)
                elif dev.dev == 'PBPM':
                    row = 0
                    row += int(dev.idx) - 1
                    if dev.sub.endswith('BCFE'):
                        row += self.PBPM_ID_MAXCOUNT_PERSEC
                    group2lay['Photon BPM'].addWidget(wid, row, 0)
                else:
                    if dev.sub.endswith(('SA', 'SB', 'SP')):
                        group2lay['ID BPM'].addWidget(wid)
                    else:
                        group2lay[dev.sec+' BPM'].addWidget(wid)
                        if dev.sec == 'BO':
                            bobpm_cnt += 1

            if sec == 'IA':
                # add auxiliary layout element for PBPM alignment
                lay_pbpm = group2lay['Photon BPM']
                for row in range(self.PBPM_MAXCOUNT_PERSEC):
                    if not lay_pbpm.itemAtPosition(row, 0):
                        wid = self._get_monitor_widget(SiriusPVName('X-X:X-X'))
                        lay_pbpm.addWidget(wid, row, 0)

                # add auxiliary layout element for BO alignment
                if bobpm_cnt == 2:
                    wid = self._get_monitor_widget(SiriusPVName('X-X:X-X'))
                    group2lay['BO BPM'].addWidget(wid)

                # add BO subsector header
                label = QLabel(
                    f'<h4>{bobpm_n:02}</h4>', self, alignment=Qt.AlignCenter)
                label.setObjectName('boheader')
                label.setStyleSheet('#boheader{border: 1px solid gray;}')
                grid.addWidget(label, 21, col)
                bobpm_n += bobpm_cnt
        return monitor

    def _setupLegendWidget(self):
        dev2info = {
            'Timing': 'Locked',
            'FOFB': 'Partners\nLinked',
            'Photon\nBPM': 'Connected',
            'BPM': (('RFFE\nConnected'), ('BPM ADC\nClock Synced')),
        }

        legend = QWidget()
        legend.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        hlay_leg = QHBoxLayout(legend)

        # legend title
        hlay_leg.addWidget(QLabel('<h4>Legend: </h4>'))

        # for each device type, add a description
        for dev, sts in dev2info.items():
            # device title
            lbl = QLabel(
                f' • {dev}:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            hlay_leg.addWidget(lbl)

            # left description
            if len(sts) == 2:
                dsc = QLabel(
                    sts[0], self, alignment=Qt.AlignRight | Qt.AlignVCenter)
                hlay_leg.addWidget(dsc)
                sts = sts[-1]

            # leds
            wid = self._get_legend_widget(dev)
            hlay_leg.addWidget(wid, alignment=Qt.AlignCenter)

            # right description
            dsc = QLabel(sts, self, alignment=Qt.AlignLeft | Qt.AlignVCenter)
            hlay_leg.addWidget(dsc)
            hlay_leg.addStretch()
        hlay_leg.addStretch()

        return legend

    def _get_monitor_widget(self, dev):
        wids = list()
        if dev.dev.endswith('EVR'):
            wid = EVRMonLed(self, dev, prefix=self.prefix)
            wid.shape = wid.ShapeMap.Square
            wid.setStyleSheet("""
                QLed{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.96em; max-width: 0.96em;
                }""")
            wids.append(wid)
        elif dev.dev == 'FOFBCtrl':
            wid = FOFBCtrlMonLed(self, dev, prefix=self.prefix)
            wid.shape = wid.ShapeMap.Square
            wid.setStyleSheet("""
                QLed{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.96em; max-width: 0.96em;
                }""")
            wids.append(wid)
        elif dev.dev == 'PBPM':
            wid = PBPMMonLed(self, dev, prefix=self.prefix)
            wid.shape = wid.ShapeMap.Square
            wid.setStyleSheet("""
                QLed{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.96em; max-width: 0.96em;
                }""")
            wids.append(wid)
        elif dev.dev == 'BPM':
            anfe = RFFEMonLed(self, dev+':RFFE', prefix=self.prefix)
            anfe.shape = anfe.ShapeMap.Rectangle
            anfe.setStyleSheet("""
                QLed{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.48em; max-width: 0.48em;
                }""")
            dibe = BPMMonLed(self, dev, prefix=self.prefix)
            dibe.shape = dibe.ShapeMap.Rectangle
            dibe.setStyleSheet("""
                QLed{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.48em; max-width: 0.48em;
                }""")
            conn = FRUMonLed(self, dev+'CO-AMC-1', prefix=self.prefix)
            conn.shape = conn.ShapeMap.Circle
            conn.setStyleSheet("""
                QLed{
                    min-height: 0.72em; max-height: 0.72em;
                    min-width: 0.72em; max-width: 0.72em;
                }""")
            duplicate = (
                'M1:DI-BPM', 'C1:DI-BPM-1', 'C2:DI-BPM', 'C3:DI-BPM-2'
                )
            if dev.endswith(duplicate):
                wids.extend([conn, anfe, dibe])
            else:
                wids.extend([anfe, dibe])
        else:
            wid = QLabel()
            wid.setStyleSheet("""
                QLabel{
                    min-height: 0.96em; max-height: 0.96em;
                    min-width: 0.96em; max-width: 0.96em;
                }""")
            wids.append(wid)
        monwid = QWidget()
        lay = QHBoxLayout(monwid)
        lay.setContentsMargins(6, 5, 6, 5)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(0)
        for wid in wids:
            lay.addWidget(wid)
        return monwid

    def _get_legend_widget(self, dev):
        if dev != 'BPM':
            wid = QLed(self)
            wid.state = 0
            wid.offColor = QLed.Blue
            wid.shape = wid.ShapeMap.Square
        else:
            wid = QWidget()
            lay = QHBoxLayout(wid)
            lay.setAlignment(Qt.AlignCenter)
            lay.setSpacing(0)
            for _ in ['rffe', 'bpm']:
                led = QLed(self)
                led.state = 0
                led.offColor = QLed.Blue
                led.shape = led.ShapeMap.Rectangle
                led.setStyleSheet('QLed{max-width: 0.48em;}')
                lay.addWidget(led)
        return wid
