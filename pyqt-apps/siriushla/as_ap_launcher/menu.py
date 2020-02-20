#!/usr/bin/env python-sirius

"""Mock application launcher."""

from epics import PV as _PV

from qtpy.QtWidgets import QVBoxLayout, QMessageBox, QMenuBar, \
    QMenu, QHBoxLayout, QWidget, QPushButton, QAction, QGroupBox, \
    QInputDialog
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _prefix
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName

from siriushla import util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ap_configdb.pvsconfigs import SelectAndApplyPVsWidget
from siriushla.as_di_scrns.list_scrns import get_scrn_list
from siriushla.as_di_dccts.main import get_dcct_list


def get_pushbutton(name, parent):
    wid = QPushButton(name, parent)
    menu = QMenu(wid)
    wid.setMenu(menu)
    return menu


def get_object(ismenubar=True, parent=None):
    SUPER = QMenuBar if ismenubar else QWidget
    LEVEL1 = QMenu if ismenubar else QGroupBox
    LEVEL2M = QMenu if ismenubar else get_pushbutton
    LEVEL2A = QAction if ismenubar else QPushButton

    class MainMenuBar(SUPER):
        """Main launcher."""

        def __init__(self, parent=None):
            """Constructor."""
            super().__init__(parent=parent)
            self._setup_ui()
            self.setStyleSheet("""
                QPushButton{
                    min-width:4.5em; max-width:4.5em;
                    min-height:1.5em; max-height:1.5em;
                }""")

        def _setup_ui(self):
            as_apps = self._create_as_menu()
            li_apps = self._create_li_menu()
            tb_apps = self._create_section_menu('TB', 'TB')
            bo_apps = self._create_section_menu('BO', 'BO')
            ts_apps = self._create_section_menu('TS', 'TS')
            si_apps = self._create_section_menu('SI', 'SI')
            tool_apps = self._create_tool_menu()
            config = self._create_config_menu()

            self.add_object_to_level0(config)
            self.add_object_to_level0(as_apps)
            self.add_object_to_level0(li_apps)
            self.add_object_to_level0(tb_apps)
            self.add_object_to_level0(bo_apps)
            self.add_object_to_level0(ts_apps)
            self.add_object_to_level0(si_apps)
            self.add_object_to_level0(tool_apps)

        def add_object_to_level0(self, widget):
            if ismenubar:
                self.addMenu(widget)
            else:
                lay = self.layout()
                if not isinstance(lay, QVBoxLayout):
                    lay = QVBoxLayout(self)
                    self.setLayout(lay)
                lay.addWidget(widget)

        def add_object_to_level1(self, pai, filho):
            if ismenubar:
                if isinstance(filho, QAction):
                    pai.addAction(filho)
                else:
                    pai.addMenu(filho)
            else:
                lay = pai.layout()
                if not isinstance(lay, QHBoxLayout):
                    pai.setLayout(QHBoxLayout(pai))
                    lay = pai.layout()
                if isinstance(filho, QMenu):
                    icon = filho.icon()
                    filho = filho.parent()
                    filho.setIcon(icon)
                lay.addWidget(filho)

        def _create_config_menu(self):
            pvsconfig = LEVEL1('Configs', self)
            pvsconfig.setObjectName('Config')

            pvssave = LEVEL2A('Save', pvsconfig)
            self.connect_newprocess(
                pvssave, 'sirius-hla-as-ap-pvsconfigs-save.py')
            pvsload = LEVEL2A('Load', pvsconfig)
            self.connect_newprocess(
                pvsload, 'sirius-hla-as-ap-pvsconfigs-load.py')
            standby = LEVEL2A('Standby', pvsconfig)
            signal = util.get_appropriate_signal(standby)
            signal.connect(self._applyconfig)
            turnoff = LEVEL2A('TurnOff', pvsconfig)
            signal = util.get_appropriate_signal(turnoff)
            signal.connect(self._applyconfig)

            self.add_object_to_level1(pvsconfig, pvssave)
            self.add_object_to_level1(pvsconfig, pvsload)
            self.add_object_to_level1(pvsconfig, standby)
            self.add_object_to_level1(pvsconfig, turnoff)
            return pvsconfig

        def _create_tool_menu(self):
            menu = LEVEL1('Tools', self)
            menu.setObjectName('ToolMenu')
            servconf = LEVEL2A('ConfigDB', menu)
            self.connect_newprocess(servconf, 'sirius-hla-as-ap-configdb.py')
            self.add_object_to_level1(menu, servconf)
            chart = LEVEL2A('TimeChart', menu)
            self.connect_newprocess(chart, 'timechart')
            self.add_object_to_level1(menu, chart)
            return menu

        def _create_as_menu(self):
            menu = LEVEL1('AS', self)
            menu.setObjectName('ASApp')

            injection = LEVEL2A('Injection', menu)
            self.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')
            timing = LEVEL2M('Timing', menu)
            timing.setIcon(qta.icon('mdi.timer'))
            timing.setObjectName('ASApp')
            main = QAction('Main', timing)
            main.setIcon(qta.icon('mdi.timer'))
            self.connect_newprocess(
                main, ['sirius-hla-as-ti-control.py', '-t', 'main'])
            summary = QAction('Monitor', timing)
            summary.setIcon(util.get_monitor_icon('mdi.timer'))
            self.connect_newprocess(
                summary, ['sirius-hla-as-ti-control.py', '-t', 'monitor'])
            timing.addAction(main)
            timing.addAction(summary)

            pwrsupply = LEVEL2M('PS', menu)
            pwrsupply.setIcon(qta.icon('mdi.car-battery'))
            pwrsupply.setObjectName('ASApp')
            pscycle = QAction('Cycle', pwrsupply)
            pscycle.setIcon(qta.icon('mdi.recycle'))
            self.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')
            psdiag = QAction('Diag', pwrsupply)
            psdiag.setIcon(qta.icon('mdi.stethoscope'))
            self.connect_newprocess(psdiag, 'sirius-hla-as-ps-diag.py')
            pstest = QAction('Test', pwrsupply)
            pstest.setIcon(qta.icon('mdi.test-tube'))
            self.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')
            psmonitor = QAction('Monitor', pwrsupply)
            psmonitor.setIcon(util.get_monitor_icon('mdi.car-battery'))
            self.connect_newprocess(psmonitor, 'sirius-hla-as-ps-monitor.py')
            pwrsupply.addAction(pscycle)
            pwrsupply.addAction(psdiag)
            pwrsupply.addAction(pstest)
            pwrsupply.addAction(psmonitor)

            optics = LEVEL2M('Optics', menu)
            optics.setObjectName('ASApp')
            energy_button = QAction('Energy Button', optics)
            self.connect_newprocess(
                energy_button, 'sirius-hla-as-ap-energybutton.py')
            offconv = QAction('Offline Converter', optics)
            self.connect_newprocess(offconv, 'sirius-hla-as-ap-magoffconv.py')
            optics.addAction(energy_button)
            optics.addAction(offconv)

            self.add_object_to_level1(menu, injection)
            self.add_object_to_level1(menu, timing)
            self.add_object_to_level1(menu, pwrsupply)
            self.add_object_to_level1(menu, optics)
            return menu

        def _create_li_menu(self):
            menu = LEVEL1('LI', self)
            menu.setObjectName('LIApp')
            launcher = LEVEL2A('Launcher', menu)
            util.connect_newprocess(launcher, 'sirius-hla-li-ap-launcher.sh',
                                    is_window=False)

            PS = self._set_ps_menu('li')
            PS.setIcon(qta.icon('mdi.car-battery'))

            mps = LEVEL2M('MPS', menu)
            mps.setObjectName('LIApp')
            mpsmon = QAction('Monitor', mps)
            mpsmon.setIcon(qta.icon('mdi.monitor-dashboard'))
            self.connect_newprocess(mpsmon, 'sirius-hla-li-ap-mpsmon.py')
            mps.addAction(mpsmon)

            optics = LEVEL2M('Optics', menu)
            optics.setObjectName('LIApp')
            energy = QAction('Energy Meas', optics)
            energy.setIcon(qta.icon('mdi.gauge'))
            self.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')
            emit = QAction('Emittance Meas', optics)
            self.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')
            optics.addAction(energy)
            optics.addAction(emit)

            self.add_object_to_level1(menu, PS)
            self.add_object_to_level1(menu, mps)
            self.add_object_to_level1(menu, launcher)
            self.add_object_to_level1(menu, optics)
            return menu

        def _create_section_menu(self, name, sec):
            sec = sec.lower()
            menu = LEVEL1(name, self)
            menu.setObjectName(sec.upper()+'App')

            PS = self._set_ps_menu(sec)
            PS.setIcon(qta.icon('mdi.car-battery'))
            if sec in {'bo', 'si'}:
                PU = self._set_pu_menu(sec)
                PU.setIcon(qta.icon('mdi.current-ac'))
            OPT = self._set_optics_menu(sec)
            DIG = self._set_diagnostic_menu(sec)
            self.add_object_to_level1(menu, PS)
            if sec in {'bo', 'si'}:
                self.add_object_to_level1(menu, PU)
                RF = self._set_rf_menu(sec)
                RF.setIcon(qta.icon('mdi.waves'))
                self.add_object_to_level1(menu, RF)
            self.add_object_to_level1(menu, DIG)
            self.add_object_to_level1(menu, OPT)
            return menu

        def _set_optics_menu(self, sec):
            optics = LEVEL2M('Optics', self)
            optics.setObjectName(sec.upper()+'App')

            if sec in {'tb', 'ts'}:
                launcher = QAction('Main', optics)
                self.connect_newprocess(
                    launcher, 'sirius-hla-'+sec+'-ap-control.py')
                optics.addAction(launcher)
            elif sec == 'bo':
                injbo = QAction('InjBO', optics)
                self.connect_newprocess(
                    injbo, 'sirius-hla-bo-ap-injcontrol.py')
                optics.addAction(injbo)

            sofb = QAction('SOFB', optics)
            sofb.setIcon(qta.icon('fa5s.hammer'))
            self.connect_newprocess(sofb, 'sirius-hla-'+sec+'-ap-sofb.py')
            optics.addAction(sofb)

            if sec in {'tb', 'ts'}:
                PosAng = QAction('PosAng CH-Sept', optics)
                self.connect_newprocess(
                    PosAng, 'sirius-hla-'+sec+'-ap-posang.py')
                optics.addAction(PosAng)
            if 'tb' in sec:
                PosAngCHCH = QAction('PosAng CH-CH', optics)
                self.connect_newprocess(
                    PosAngCHCH, 'sirius-hla-'+sec+'-ap-posang-chch.py')
                optics.addAction(PosAngCHCH)
                Emittance = QAction('Emittance Meas', optics)
                self.connect_newprocess(
                    Emittance, 'sirius-hla-tb-ap-emittance.py')
                optics.addAction(Emittance)
            if sec in {'bo', 'si'}:
                TuneCorr = QAction('Tune Correction', optics)
                self.connect_newprocess(
                    TuneCorr, 'sirius-hla-'+sec+'-ap-tunecorr.py')
                ChromCorr = QAction('Chromaticity Correction', optics)
                optics.addAction(TuneCorr)
                self.connect_newprocess(
                    ChromCorr, 'sirius-hla-'+sec+'-ap-chromcorr.py')
                optics.addAction(ChromCorr)
            if 'si' in sec:
                CurrLT = QAction('Current and Lifetime', optics)
                self.connect_newprocess(
                    CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')
                optics.addAction(CurrLT)
            if 'bo' in sec:
                ChargeMon = QAction('Charge Monitor', optics)
                self.connect_newprocess(
                    ChargeMon, 'sirius-hla-bo-ap-chargemon.py')
                optics.addAction(ChargeMon)
                ramp = QAction('Ramp', optics)
                ramp.setIcon(qta.icon('mdi.escalator', scale_factor=1.5))
                self.connect_newprocess(ramp, 'sirius-hla-bo-ap-ramp.py')
                optics.addAction(ramp)
            return optics

        def _set_diagnostic_menu(self, sec):
            diag = LEVEL2M('DI', self)
            diag.setObjectName(sec.upper()+'App')
            BPMs = self._set_bpm_menu(sec)
            act = QAction('BPMs', diag)
            act.setIcon(qta.icon('mdi.currency-sign'))
            act.setMenu(BPMs)
            diag.addAction(act)
            # diag.addMenu(BPMs)
            if sec in {'tb', 'ts'}:
                ICTs = QAction('ICTs', diag)
                self.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')
                diag.addAction(ICTs)
            elif sec in {'bo', 'si'}:
                DCCT = QMenu('DCCTs', diag)
                DCCT.setObjectName('SIApp')
                for dev in get_dcct_list(sec.upper()):
                    act_dev = DCCT.addAction(dev)
                    self.connect_newprocess(
                        act_dev, ['sirius-hla-as-di-dcct.py', dev])
                diag.addMenu(DCCT)
            if 'tb' in sec:
                Slits = QAction('Slits', diag)
                self.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')
                diag.addAction(Slits)
            if sec in {'bo', 'si'}:
                Tune = QAction('Tune', diag)
                self.connect_newprocess(Tune, 'sirius-hla-'+sec+'-di-tune.py')
                diag.addAction(Tune)
                VLight = QAction('VLight', diag)
                self.connect_newprocess(
                    VLight, 'sirius-hla-'+sec+'-di-vlight.py')
                diag.addAction(VLight)
            if 'si' not in sec:
                Scrns = QMenu('Screens', diag)
                Scrns.setObjectName(sec.upper()+'App')
                for dev in get_scrn_list(sec.upper()):
                    act_dev = Scrns.addAction(dev)
                    self.connect_newprocess(
                        act_dev, ['sirius-hla-as-di-scrn.py', dev])
                diag.addMenu(Scrns)
            return diag

        def _set_bpm_menu(self, sec):
            cmd = ['sirius-hla-as-di-bpm.py', sec]
            menu = QMenu('BPMs', self)
            menu.setObjectName(sec.upper()+'App')
            menu.setIcon(qta.icon('mdi.currency-sign'))
            action = menu.addAction('Monitor')
            action.setIcon(util.get_monitor_icon('mdi.currency-sign'))
            self.connect_newprocess(action, cmd + ['-w', 'Monitor', ])
            typs = ('Single Pass', 'Multi Turn')
            acts = ('SPass', 'MTurn')
            for typ, act in zip(typs, acts):
                if sec in {'bo', 'si'}:
                    menu2 = menu.addMenu(typ)
                    menu2.setObjectName(sec.upper()+'App')
                    if act == 'SPass':
                        self._create_bpm_actions(sec, menu2, act, cmd)
                    else:
                        for mode in ('Antennas', 'Positions'):
                            menu3 = menu2.addMenu(mode)
                            menu3.setObjectName(sec.upper()+'App')
                            cmd2 = cmd + ['-m', mode]
                            self._create_bpm_actions(sec, menu3, act, cmd2)
                else:
                    if act == 'SPass':
                        self._create_bpm_actions(sec, menu, act, cmd, typ)
                    else:
                        menu2 = menu.addMenu(typ)
                        menu2.setObjectName(sec.upper()+'App')
                        for mode in ('Antennas', 'Positions'):
                            cmd2 = cmd + ['-m', mode]
                            self._create_bpm_actions(
                                sec, menu2, act, cmd2, mode)
            return menu

        def _create_bpm_actions(self, sec, menu, act, cmd, name=None):
            cmd = cmd + ['-w', act]
            if sec == 'bo':
                for i in range(5):
                    action = menu.addAction('subsec {0:02d}-{1:02d}'.format(
                        10*i+2, ((10*(i+1)+1)) % 50))
                    self.connect_newprocess(action, cmd + ['-s', str(i+1)])
            elif sec == 'si':
                for i in range(1, 21):
                    sub = '{0:02d}'.format(i)
                    action = menu.addAction('SI-' + sub)
                    self.connect_newprocess(action, cmd + ['-s', sub])
            else:
                action = menu.addAction(name)
                self.connect_newprocess(action, cmd)

        def _set_ps_menu(self, sec):
            scr = 'sirius-hla-' + sec + '-ps-control.py'
            psmenu = LEVEL2M('PS', self)
            psmenu.setObjectName(sec.upper()+'App')

            all_dev = QAction(
                'All'+('' if sec != 'si' else ' Families'), psmenu)
            self.connect_newprocess(all_dev, scr)
            psmenu.addAction(all_dev)

            if sec != 'li':
                dip = QAction('Dipoles', psmenu)
                self.connect_newprocess(dip, [scr, '--device', 'dipole'])
                psmenu.addAction(dip)
            else:
                spect = QAction('Spectrometer', psmenu)
                self.connect_newprocess(
                    spect, [scr, '--device', 'spectrometer'])
                psmenu.addAction(spect)

            quad = QAction('Quadrupoles', psmenu)
            self.connect_newprocess(quad, [scr, '--device', 'quadrupole'])
            psmenu.addAction(quad)

            if sec in {'bo', 'si'}:
                sext = QAction('Sextupoles', psmenu)
                self.connect_newprocess(sext, [scr, '--device', 'sextupole'])
                psmenu.addAction(sext)

                if sec == 'bo':
                    skew = QAction('Skew Quadrupoles', psmenu)
                    self.connect_newprocess(
                        skew, [scr, '--device', 'skew-quadrupole'])
                    psmenu.addAction(skew)
                else:
                    skew_menu = psmenu.addMenu('Skew Quadrupoles')
                    skew_menu.setObjectName(sec.upper()+'App')
                    skew_all_act = skew_menu.addAction('All')
                    self.connect_newprocess(
                        skew_all_act, [scr, '--device', 'skew-quadrupole'])
                    skew_sec_menu = skew_menu.addMenu('Subsectors')
                    skew_sec_menu.setObjectName('SIApp')
                    for i in range(1, 21):
                        act = skew_sec_menu.addAction('SI-{:02d}'.format(i))
                        self.connect_newprocess(
                            act, [scr, '--device', 'skew-quadrupole',
                                  '--subsection', '{:02d}.*'.format(i)])

            if sec in {'li', 'tb', 'ts', 'bo'}:
                corrs = QAction('Correctors', psmenu)
                self.connect_newprocess(
                    corrs, [scr, '--device', 'corrector-slow'])
                psmenu.addAction(corrs)
            else:
                corrs_menu = psmenu.addMenu('Correctors')
                corrs_menu.setObjectName('SIApp')
                corrs_all_act = corrs_menu.addAction('All')
                self.connect_newprocess(
                    corrs_all_act, [scr, '--device', 'corrector-slow'])
                corrs_sec_menu = corrs_menu.addMenu('Subsectors')
                corrs_sec_menu.setObjectName('SIApp')
                for i in range(1, 21):
                    act = corrs_sec_menu.addAction('SI-{:02d}'.format(i))
                    self.connect_newprocess(
                        act, [scr, '--device', 'corrector-slow',
                              '--subsection', '{:02d}.*'.format(i)])

            if sec == 'si':
                trims_menu = psmenu.addMenu('Trims')
                trims_menu.setObjectName(sec.upper()+'App')
                trims_all_act = trims_menu.addAction('All')
                self.connect_newprocess(
                    trims_all_act, [scr, '--device', 'trim-quadrupole'])
                trims_sec_menu = trims_menu.addMenu('Subsectors')
                trims_sec_menu.setObjectName('SIApp')
                for i in range(1, 21):
                    act = trims_sec_menu.addAction('SI-{:02d}'.format(i))
                    self.connect_newprocess(
                        act, [scr, '--device', 'trim-quadrupole',
                              '--subsection', '{:02d}.*'.format(i)])
                trims_fam_menu = trims_menu.addMenu('Families')
                trims_fam_menu.setObjectName('SIApp')
                fams = PSSearch.get_psnames(
                    {'sec': 'SI', 'sub': 'Fam', 'dev': 'Q(D|F|[1-4]).*'})
                for fam in fams:
                    fam = SiriusPVName(fam)
                    act = trims_fam_menu.addAction(fam.dev)
                    self.connect_newprocess(
                        act, [scr, '--device', fam, '-istrim'])

            #     fcorr = QAction('Fast Correctors', psmenu)
            #     self.connect_newprocess(
            #         fcorr, [scr, '--device', 'corrector-fast'])
            #     psmenu.addAction(fcorr)

            elif sec == 'bo':
                wfmerr = QAction('Waveform Error', psmenu)
                self.connect_newprocess(wfmerr, 'sirius-hla-bo-ps-wfmerror.py')
                psmenu.addAction(wfmerr)

            elif sec == 'li':
                lens = QAction('Lens', psmenu)
                self.connect_newprocess(lens, [scr, '--device', 'lens'])
                psmenu.addAction(lens)
                slnd = QAction('Solenoids', psmenu)
                self.connect_newprocess(slnd, [scr, '--device', 'solenoid'])
                psmenu.addAction(slnd)

            return psmenu

        def _set_pu_menu(self, sec):
            pumenu = LEVEL2M('PU', self)
            pumenu.setObjectName(sec.upper()+'App')
            script = 'sirius-hla-' + sec + '-pu-control.py'
            if sec == 'si':
                pmag = QAction('PU Injection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'InjSI'])
                pumenu.addAction(pmag)
                pmag = QAction('PU Pingers', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'Ping'])
                pumenu.addAction(pmag)
            elif sec == 'bo':
                pmag = QAction('PU Injection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'InjBO'])
                pumenu.addAction(pmag)
                pmag = QAction('PU Ejection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'EjeBO'])
                pumenu.addAction(pmag)
            return pumenu

        def _set_rf_menu(self, sec):
            menu = LEVEL2M('RF', self)
            menu.setObjectName(sec.upper()+'App')

            status = QAction('Main', menu)
            status.setIcon(qta.icon('mdi.waves'))
            self.connect_newprocess(
                status, 'sirius-hla-'+sec.lower()+'-rf-control.py')
            menu.addAction(status)
            return menu

        def connect_newprocess(self, button, cmd):
            util.connect_newprocess(button, cmd, parent=self)

        def _applyconfig(self):
            sender_text = self.sender().text()
            if 'Standby' in sender_text:
                config_name = 'standby'
            elif 'TurnOff' in sender_text:
                config_name = 'turnoff'

            ans = QMessageBox.question(
                self, 'Are you Sure?',
                "Do you really want to apply the Configuration '" +
                config_name + "' to the machine?",
                QMessageBox.Yes, QMessageBox.Cancel)
            if ans != QMessageBox.Yes:
                return

            current, ok = QInputDialog.getDouble(
                self, 'Enter value: ',
                'Enter FilaPS standby current [A]\n'
                'or cancel to not set it: ',
                value=0.7, min=0.0, max=1.5, decimals=3)
            if ok:
                fila_pv = _PV(
                    _prefix+'LI-01:EG-FilaPS:currentoutsoft',
                    connection_timeout=0.05)
                fila_pv.get()  # force connection
                if fila_pv.connected:
                    fila_pv.put(current)
                else:
                    QMessageBox.warning(
                        self, 'Message',
                        'Could not connect to LI-01:EG-FilaPS!')

            client = ConfigDBClient()

            WinClass = create_window_from_widget(
                SelectAndApplyPVsWidget, 'Select PVs to Apply Standby')
            wind = WinClass(self, client)
            wind.widget.settingFinished.connect(wind.close)
            wind.widget.fill_config('global_config', config_name)
            wind.exec_()

    return MainMenuBar(parent=parent)


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusMainWindow

    app = SiriusApplication()
    main = SiriusMainWindow()
    menubar = get_object(ismenubar=True)
    main.setMenuBar(menubar)
    wid = get_object(ismenubar=False)
    main.setCentralWidget(wid)
    main.show()
    sys.exit(app.exec_())
