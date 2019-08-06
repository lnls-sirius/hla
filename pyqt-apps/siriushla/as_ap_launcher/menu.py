#!/usr/bin/env python-sirius

"""Mock application launcher."""

from epics import PV as _PV

from qtpy.QtWidgets import QVBoxLayout, QMessageBox, QMenuBar, \
    QMenu, QHBoxLayout, QWidget, QPushButton, QAction, QGroupBox, \
    QInputDialog

from siriuspy.envars import vaca_prefix as _prefix
from siriuspy.clientconfigdb import ConfigDBClient

from siriushla import util
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter


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
            serv_apps = self._create_serv_menu()
            config = self._create_config_menu()

            self.add_object_to_level0(config)
            self.add_object_to_level0(as_apps)
            self.add_object_to_level0(li_apps)
            self.add_object_to_level0(tb_apps)
            self.add_object_to_level0(bo_apps)
            self.add_object_to_level0(ts_apps)
            self.add_object_to_level0(si_apps)
            self.add_object_to_level0(serv_apps)

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
                    filho = filho.parent()
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

        def _create_serv_menu(self):
            menu = LEVEL1('Services', self)
            menu.setObjectName('ServMenu')
            servconf = LEVEL2A('ConfigDB', menu)
            self.connect_newprocess(servconf, 'sirius-hla-as-ap-configdb.py')
            self.add_object_to_level1(menu, servconf)
            return menu

        def _create_as_menu(self):
            menu = LEVEL1('AS', self)
            menu.setObjectName('ASApp')

            injection = LEVEL2A('Injection', menu)
            self.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')
            timing = LEVEL2A('Timing', menu)
            self.connect_newprocess(timing, 'sirius-hla-as-ti-control.py')

            pwrsupply = LEVEL2M('PS', menu)
            pwrsupply.setObjectName('ASApp')
            pscycle = QAction('Cycle', pwrsupply)
            self.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')
            psdiag = QAction('Diag', pwrsupply)
            self.connect_newprocess(psdiag, 'sirius-hla-as-ps-diag.py')
            pstest = QAction('Test', pwrsupply)
            self.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')
            psmonitor = QAction('Monitor', pwrsupply)
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
            util.connect_newprocess(launcher, 'sirius-hla-li-launcher.sh',
                                    is_window=False)

            optics = LEVEL2M('Optics', menu)
            optics.setObjectName('LIApp')
            energy = QAction('Energy Meas', optics)
            self.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')
            emit = QAction('Emittance Meas', optics)
            self.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')
            optics.addAction(energy)
            optics.addAction(emit)

            self.add_object_to_level1(menu, launcher)
            self.add_object_to_level1(menu, optics)
            return menu

        def _create_section_menu(self, name, sec):
            sec = sec.lower()
            menu = LEVEL1(name, self)
            menu.setObjectName(sec.upper()+'App')

            PS = self._set_psma_menu(sec, dis='ps')
            MA = self._set_psma_menu(sec, dis='ma')
            OPT = self._set_optics_menu(sec)
            DIG = self._set_diagnostic_menu(sec)
            self.add_object_to_level1(menu, PS)
            self.add_object_to_level1(menu, MA)
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
                CurrLT = QAction('Current and Lifetime', optics)
                self.connect_newprocess(
                    CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')
                TuneCorr = QAction('Tune Correction', optics)
                self.connect_newprocess(
                    TuneCorr, 'sirius-hla-'+sec+'-ap-tunecorr.py')
                ChromCorr = QAction('Chromaticity Correction', optics)
                self.connect_newprocess(
                    ChromCorr, 'sirius-hla-'+sec+'-ap-chromcorr.py')
                optics.addAction(CurrLT)
                optics.addAction(TuneCorr)
                optics.addAction(ChromCorr)
            if 'bo' in sec:
                Ramp = QAction('Ramp', optics)
                self.connect_newprocess(Ramp, 'sirius-hla-bo-ap-ramp.py')
                optics.addAction(Ramp)
            return optics

        def _set_diagnostic_menu(self, sec):
            diag = LEVEL2M('DI', self)
            diag.setObjectName(sec.upper()+'App')
            BPMs = self._set_bpm_menu(sec)
            act = QAction('BPMs', diag)
            act.setMenu(BPMs)
            diag.addAction(act)
            # diag.addMenu(BPMs)
            if sec in {'tb', 'ts'}:
                ICTs = QAction('ICTs', diag)
                self.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')
                diag.addAction(ICTs)
            elif sec in {'si', 'bo'}:
                DCCT = QAction('DCCTs', diag)
                self.connect_newprocess(
                    DCCT, ['sirius-hla-as-di-dcct.py', sec.upper()])
                diag.addAction(DCCT)
            if 'tb' in sec:
                Slits = QAction('Slits', diag)
                self.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')
                diag.addAction(Slits)
            if 'si' not in sec:
                Scrns = QAction('Screens', diag)
                self.connect_newprocess(
                    Scrns, ['sirius-hla-as-di-scrn.py', sec.upper()])
                diag.addAction(Scrns)
            return diag

        def _set_bpm_menu(self, sec):
            cmd = ['sirius-hla-as-di-bpm.py', sec, '-w']
            menu = QMenu('BPMs', self)
            menu.setObjectName(sec.upper()+'App')
            action = menu.addAction('Summary')
            self.connect_newprocess(action, cmd + ['Summary', ])
            typs = ('Single Pass', 'Multi Turn')
            acts = ('SPass', 'MTurn')
            for typ, act in zip(typs, acts):
                if sec == 'bo':
                    menu2 = menu.addMenu(typ)
                    menu2.setObjectName(sec.upper()+'App')
                    action2 = menu2.addAction('All')
                    self.connect_newprocess(action2, cmd + [act, ])
                    action2 = menu2.addAction('subsec 02-11')
                    self.connect_newprocess(action2, cmd + [act, '-s', '1'])
                    action2 = menu2.addAction('subsec 12-21')
                    self.connect_newprocess(action2, cmd + [act, '-s', '2'])
                    action2 = menu2.addAction('subsec 22-31')
                    self.connect_newprocess(action2, cmd + [act, '-s', '3'])
                    action2 = menu2.addAction('subsec 32-41')
                    self.connect_newprocess(action2, cmd + [act, '-s', '4'])
                    action2 = menu2.addAction('subsec 42-01')
                    self.connect_newprocess(action2, cmd + [act, '-s', '5'])
                else:
                    action = menu.addAction(typ)
                    self.connect_newprocess(action, cmd + [act, ])
            return menu

        def _set_psma_menu(self, sec, dis='ps'):
            scr = 'sirius-hla-' + sec + '-' + dis + '-control.py'
            psma = LEVEL2M(
                'MA' if dis == 'ma' else 'PS', self)
            psma.setObjectName(sec.upper()+'App')

            all_dev = QAction('All', psma)
            self.connect_newprocess(all_dev, scr)
            dip = QAction('Dipoles', psma)
            self.connect_newprocess(dip, [scr, '--device', 'dipole'])
            quad = QAction('Quadrupoles', psma)
            self.connect_newprocess(quad, [scr, '--device', 'quadrupole'])
            psma.addAction(all_dev)
            psma.addAction(dip)
            psma.addAction(quad)

            if sec in {'bo', 'si'}:
                sext = QAction('Sextupoles', psma)
                self.connect_newprocess(sext, [scr, '--device', 'sextupole'])
                psma.addAction(sext)

                skew = QAction('Skew Quadrupoles', psma)
                self.connect_newprocess(
                    skew, [scr, '--device', 'quadrupole-skew'])
                psma.addAction(skew)
            corrs = QAction('Correctors', psma)
            self.connect_newprocess(corrs, [scr, '--device', 'corrector-slow'])
            psma.addAction(corrs)
            if sec in 'si':
                fcorr = QAction('Fast Correctors', psma)
                self.connect_newprocess(
                    fcorr, [scr, '--device', 'corrector-fast'])
                psma.addAction(fcorr)
            if dis in 'ma':
                pmag = QAction('Pulsed Magnets', psma)
                self.connect_newprocess(
                    pmag, 'sirius-hla-'+sec+'-pm-control.py')
                psma.addAction(pmag)
            return psma

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

            if config_name == 'standby':
                current, ok = QInputDialog.getDouble(
                    self, 'Enter value: ',
                    'Enter FilaPS standby current [A]\n'
                    'or cancel to not set it: ',
                    value=0.7, min=0.0, max=1.5, decimals=3)
                if ok:
                    fila_pv = _PV(_prefix+'LI-01:EG-FilaPS:currentoutsoft',
                                  connection_timeout=0.05)
                    fila_pv.get()  # force connection
                    if fila_pv.connected:
                        fila_pv.put(current)
                    else:
                        QMessageBox.warning(
                            self, 'Message',
                            'Could not connect to LI-01:EG-FilaPS!')

            server_global = ConfigDBClient(config_type='global_config')
            try:
                config = server_global.get_config_value(config_name)['pvs']
            except Exception:
                QMessageBox.critical(
                    self, 'Problem Loading',
                    'Configuration \''+config_name+'\' not found in Server!')
                return

            set_pvs_tuple = list()
            check_pvs_tuple = list()
            for t in config:
                try:
                    pv, value, delay = t
                except ValueError:
                    pv, value = t
                    delay = 1e-2
                set_pvs_tuple.append((pv, value, delay))
                check_pvs_tuple.append((pv, value, delay))

            # Create thread
            pvs, values, delays = zip(*set_pvs_tuple)
            set_task = EpicsSetter(pvs, values, delays, PyEpicsWrapper, self)
            pvs, values, delays = zip(*check_pvs_tuple)
            check_task = EpicsChecker(
                pvs, values, delays, PyEpicsWrapper, self)
            failed = []
            check_task.itemChecked.connect(
                lambda pv, status: failed.append(pv) if not status else None)

            # Set/Check PVs values and show wait dialog informing user
            labels = ['Setting PV values', 'Checking PV values']
            tasks = [set_task, check_task]
            dlg = ProgressDialog(labels, tasks, self)
            dlg.rejected.connect(set_task.exit_task)
            dlg.rejected.connect(check_task.exit_task)
            ret = dlg.exec_()
            if ret == dlg.Rejected:
                return

            # Show report dialog informing user results
            self._report = ReportDialog(failed, self)
            self._report.show()

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
