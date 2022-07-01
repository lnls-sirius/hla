#!/usr/bin/env python-sirius

"""Mock application launcher."""

from epics import PV as _PV

from qtpy.QtWidgets import QVBoxLayout, QMessageBox, QMenuBar, \
    QMenu, QHBoxLayout, QWidget, QPushButton, QAction, QGroupBox, \
    QInputDialog
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _prefix
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.search import PSSearch, IDSearch
from siriuspy.namesys import SiriusPVName
from siriuspy.oscilloscope import Scopes

from siriushla import util
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ap_configdb.pvsconfigs import SelectAndApplyPVsWidget
from siriushla.as_di_scrns.list_scrns import get_scrn_list
from siriushla.as_di_dccts.main import get_dcct_list


def get_pushbutton(name, parent):
    """."""
    wid = QPushButton(name, parent)
    menu = QMenu(wid)
    wid.setMenu(menu)
    return menu


def get_object(ismenubar=True, parent=None):
    """."""
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
            config = self._create_config_menu()
            as_apps = self._create_as_menu()
            li_apps = self._create_li_menu()
            tb_apps = self._create_section_menu('TB', 'TB')
            bo_apps = self._create_section_menu('BO', 'BO')
            ts_apps = self._create_section_menu('TS', 'TS')
            si_apps = self._create_section_menu('SI', 'SI')
            id_apps = self._create_id_menu()
            bl_apps = self._create_bl_menu()
            tool_apps = self._create_tool_menu()
            it_apps = self._create_it_menu()

            self.add_object_to_level0(config)
            self.add_object_to_level0(as_apps)
            self.add_object_to_level0(li_apps)
            self.add_object_to_level0(tb_apps)
            self.add_object_to_level0(bo_apps)
            self.add_object_to_level0(ts_apps)
            self.add_object_to_level0(si_apps)
            self.add_object_to_level0(id_apps)
            self.add_object_to_level0(bl_apps)
            self.add_object_to_level0(tool_apps)
            self.add_object_to_level0(it_apps)

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

            procserv = LEVEL2A('ProcServ', menu)
            self.connect_newprocess(
                procserv, 'sirius-hla-as-ap-pctrl', is_pydm=True)
            self.add_object_to_level1(menu, procserv)

            chart = LEVEL2A('TimeChart', menu)
            self.connect_newprocess(chart, 'timechart')
            self.add_object_to_level1(menu, chart)

            macreport = LEVEL2A('Mach.Rep', menu)
            self.connect_newprocess(macreport, 'sirius-hla-as-ap-macreport.py')
            self.add_object_to_level1(menu, macreport)

            osci = LEVEL2M('Osc.View', menu)
            asdifctdig = QAction('AS-DI-FCT', osci)
            util.connect_newprocess(
                asdifctdig, ['gvncviewer', Scopes.AS_DI_FCTDIG],
                is_window=False)
            asdifpmdig = QAction('AS-DI-FPM', osci)
            util.connect_newprocess(
                asdifpmdig, ['gvncviewer', Scopes.AS_DI_FPMDIG],
                is_window=False)
            lidiict = QAction('LI-DI-ICT', osci)
            util.connect_newprocess(
                lidiict, ['gvncviewer', Scopes.LI_DI_ICTOSC],
                is_window=False)
            tbpuinjbo = QAction('TB-PU-InjBO', osci)
            util.connect_newprocess(
                tbpuinjbo, ['gvncviewer', Scopes.TB_PU_OSC_INJBO],
                is_window=False)
            tspuejebo = QAction('TS-PU-EjeBO', osci)
            util.connect_newprocess(
                tspuejebo, ['gvncviewer', Scopes.TS_PU_OSC_EJEBO],
                is_window=False)
            tspuinjsi = QAction('TS-PU-InjSI', osci)
            util.connect_newprocess(
                tspuinjsi, ['gvncviewer', 'TS-PU-Osc-InjSI'],
                is_window=False)
            sipuinjsi = QAction('SI-PU-InjSI', osci)
            util.connect_newprocess(
                sipuinjsi, ['gvncviewer', 'SI-PU-Osc-InjSI'],
                is_window=False)

            osci.addAction(asdifctdig)
            osci.addAction(asdifpmdig)
            osci.addAction(lidiict)
            osci.addAction(tbpuinjbo)
            osci.addAction(tspuejebo)
            osci.addAction(tspuinjsi)
            osci.addAction(sipuinjsi)
            self.add_object_to_level1(menu, osci)
            return menu

        def _create_as_menu(self):
            menu = LEVEL1('AS', self)
            menu.setObjectName('ASApp')

            genstatus = LEVEL2A('Status', menu)
            genstatus.setIcon(qta.icon('mdi.view-split-vertical'))
            self.connect_newprocess(genstatus, 'sirius-hla-si-ap-genstatus.py')

            monitor = LEVEL2A('Monitor', menu)
            monitor.setIcon(qta.icon('mdi.monitor-dashboard'))
            self.connect_newprocess(monitor, 'sirius-hla-as-ap-monitor.py')

            injection = LEVEL2A('Injection', menu)
            injection.setIcon(qta.icon('fa5s.syringe'))
            self.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')

            effmon = LEVEL2A('Efficiency', menu)
            effmon.setIcon(qta.icon('mdi.percent-outline'))
            self.connect_newprocess(effmon, 'sirius-hla-as-ap-effmon.py')

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
            psgraph = QAction('Graph', pwrsupply)
            psgraph.setIcon(qta.icon('mdi.chart-line'))
            self.connect_newprocess(psgraph, 'sirius-hla-as-ps-graphmon.py')
            psmonitor = QAction('Monitor', pwrsupply)
            psmonitor.setIcon(util.get_monitor_icon('mdi.car-battery'))
            self.connect_newprocess(psmonitor, 'sirius-hla-as-ps-monitor.py')
            pwrsupply.addAction(pscycle)
            pwrsupply.addAction(psdiag)
            pwrsupply.addAction(pstest)
            pwrsupply.addAction(psgraph)
            pwrsupply.addAction(psmonitor)

            pulsedps = self._set_pu_menu('as')
            pulsedps.setIcon(qta.icon('mdi.current-ac'))

            vacuum = LEVEL2M('VA', menu)
            vacuum.setObjectName('ASApp')
            agilent = QAction('Agilent', vacuum)
            self.connect_newprocess(
                agilent, 'sirius-hla-as-va-agilent4uhv', is_pydm=True)
            mks = QAction('MKS', vacuum)
            self.connect_newprocess(
                mks, 'sirius-hla-as-va-mks937b', is_pydm=True)
            gamma = QAction('Gamma Counters', vacuum)
            self.connect_newprocess(
                gamma, 'sirius-hla-as-ap-countingpru', is_pydm=True)
            vacuum.addAction(agilent)
            vacuum.addAction(mks)
            vacuum.addAction(gamma)

            radmon = LEVEL2A('RAD', menu)
            radmon.setIcon(qta.icon('fa5s.radiation'))
            self.connect_newprocess(radmon, 'sirius-hla-as-ap-radmon.py')

            termo = LEVEL2A('Temp', menu)
            termo.setIcon(qta.icon('fa5s.thermometer-half'))
            self.connect_newprocess(
                termo, 'sirius-hla-as-ap-mbtemp', is_pydm=True)

            optics = LEVEL2M('Optics', menu)
            optics.setObjectName('ASApp')
            energy_button = QAction('Energy Button', optics)
            self.connect_newprocess(
                energy_button, 'sirius-hla-as-ap-energybutton.py')
            offconv = QAction('Offline Converter', optics)
            self.connect_newprocess(offconv, 'sirius-hla-as-ap-magoffconv.py')
            optics.addAction(energy_button)
            optics.addAction(offconv)

            self.add_object_to_level1(menu, genstatus)
            self.add_object_to_level1(menu, monitor)
            self.add_object_to_level1(menu, injection)
            self.add_object_to_level1(menu, effmon)
            self.add_object_to_level1(menu, timing)
            self.add_object_to_level1(menu, pwrsupply)
            self.add_object_to_level1(menu, pulsedps)
            self.add_object_to_level1(menu, termo)
            self.add_object_to_level1(menu, vacuum)
            self.add_object_to_level1(menu, radmon)
            self.add_object_to_level1(menu, optics)
            return menu

        def _create_li_menu(self):
            menu = LEVEL1('LI', self)
            menu.setObjectName('LIApp')
            launcher = LEVEL2A('Launcher', menu)
            util.connect_newprocess(
                launcher, 'sirius-hla-li-ap-launcher.sh', is_window=False)

            PS = self._set_ps_menu('li')
            PS.setIcon(qta.icon('mdi.car-battery'))

            DIG = LEVEL2M('DI', self)
            DIG.setObjectName('LIApp')

            bpms_menu = DIG.addMenu('BPMs')
            bpms_menu.setIcon(qta.icon('mdi.currency-sign'))
            bpms_menu.setObjectName('LIApp')

            bpm2 = QAction('BPM2', bpms_menu)
            self.connect_newprocess(
                bpm2, ["sirius-hla-li-di-bpms.py", 'LA-BI:BPM2'])
            bpms_menu.addAction(bpm2)
            bpm3 = QAction('BPM3', bpms_menu)
            self.connect_newprocess(
                bpm3, ["sirius-hla-li-di-bpms.py", 'LA-BI:BPM3'])
            bpms_menu.addAction(bpm3)

            scrns = DIG.addAction('Screens')
            scrns.setIcon(qta.icon('mdi.camera-metering-center'))
            self.connect_newprocess(scrns, 'sirius-hla-li-di-scrns.py')
            scrns.setObjectName('LIApp')

            mps = LEVEL2M('MPS', menu)
            mps.setObjectName('LIApp')
            mpsmon = QAction('Monitor', mps)
            mpsmon.setIcon(qta.icon('mdi.monitor-dashboard'))
            self.connect_newprocess(mpsmon, 'sirius-hla-li-ap-mpsmon.py')
            mps.addAction(mpsmon)

            mpscon = QAction('Control', mps)
            self.connect_newprocess(mpscon, 'sirius-hla-li-ap-mpscon.py')
            mps.addAction(mpscon)

            egun = LEVEL2A('Egun', menu)
            egun.setIcon(qta.icon('mdi.spotlight-beam'))
            self.connect_newprocess(egun, 'sirius-hla-li-eg-control.py')

            mod = LEVEL2A('Modltrs', menu)
            mod.setIcon(qta.icon('mdi.current-ac'))
            self.connect_newprocess(mod, 'sirius-hla-li-pu-modltr.py')

            llrf = LEVEL2M('LLRF', menu)
            llrf.setObjectName('LIApp')
            llrf.setIcon(qta.icon('mdi.waves'))
            llrfa = QAction('Main', llrf)
            llrfa.setIcon(qta.icon('mdi.waves'))
            self.connect_newprocess(llrfa, 'sirius-hla-li-rf-llrf.py')
            llrf.addAction(llrfa)

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
            self.add_object_to_level1(menu, DIG)
            self.add_object_to_level1(menu, mps)
            self.add_object_to_level1(menu, egun)
            self.add_object_to_level1(menu, mod)
            self.add_object_to_level1(menu, llrf)
            self.add_object_to_level1(menu, launcher)
            self.add_object_to_level1(menu, optics)
            return menu

        def _create_section_menu(self, name, sec):
            sec = sec.lower()
            menu = LEVEL1(name, self)
            menu.setObjectName(sec.upper()+'App')

            PS = self._set_ps_menu(sec)
            PS.setIcon(qta.icon('mdi.car-battery'))
            self.add_object_to_level1(menu, PS)

            if sec in {'bo', 'si'}:
                PU = self._set_pu_menu(sec)
                PU.setIcon(qta.icon('mdi.current-ac'))
                self.add_object_to_level1(menu, PU)

                RF = self._set_rf_menu(sec)
                RF.setIcon(qta.icon('mdi.waves'))
                self.add_object_to_level1(menu, RF)

            DIG = self._set_diagnostic_menu(sec)
            self.add_object_to_level1(menu, DIG)

            VA = self._set_va_menu(sec)
            self.add_object_to_level1(menu, VA)

            if sec == 'si':
                INTLK = LEVEL2A('Orb.Intlk', menu)
                INTLK.setIcon(qta.icon(
                    'mdi.currency-sign', 'mdi.alarm-light',
                    options=[dict(scale_factor=1.1), dict(scale_factor=0.5)]))
                self.connect_newprocess(INTLK, 'sirius-hla-si-ap-orbintlk.py')
                self.add_object_to_level1(menu, INTLK)

            OPT = self._set_optics_menu(sec)
            self.add_object_to_level1(menu, OPT)

            return menu

        def _create_id_menu(self):
            menu = LEVEL1('ID', self)
            menu.setObjectName('IDApp')

            All = LEVEL2A('All', menu)
            self.connect_newprocess(
                All, ['sirius-hla-si-id-control.py', '-isall'])
            self.add_object_to_level1(menu, All)

            idlist = ['SI-06SB:ID-APU22', 'SI-07SP:ID-APU22',
                      'SI-08SB:ID-APU22', 'SI-09SA:ID-APU22',
                      'SI-11SP:ID-APU58']
            for idname in idlist:
                idname = SiriusPVName(idname)
                beamline = IDSearch.conv_idname_2_beamline(idname)
                text = '{0} - {1} ({2})'.format(
                    idname.dev, idname.sub, beamline) \
                    if LEVEL2A == QAction else beamline
                APU = LEVEL2A(text, menu)
                self.connect_newprocess(
                    APU, ['sirius-hla-si-id-control.py', '-dev', idname])
                self.add_object_to_level1(menu, APU)

            return menu

        def _create_bl_menu(self):
            menu = LEVEL1('BL', self)
            menu.setObjectName('IDApp')

            Manaca = LEVEL2A('MANACA', menu)
            self.connect_newprocess(
                Manaca, ['sirius-hla-si-ap-manaca.py'])
            self.add_object_to_level1(menu, Manaca)

            return menu

        def _create_it_menu(self):
            menu = LEVEL1('IT', self)
            menu.setObjectName('ITApp')

            PS = self._set_ps_menu('it')
            PS.setIcon(qta.icon('mdi.car-battery'))
            self.add_object_to_level1(menu, PS)

            egun = LEVEL2A('Egun', menu)
            egun.setIcon(qta.icon('mdi.spotlight-beam'))
            self.connect_newprocess(egun, 'sirius-hla-it-eg-control.py')
            self.add_object_to_level1(menu, egun)

            TI = LEVEL2A('Timing', menu)
            TI.setIcon(qta.icon('mdi.timer'))
            self.connect_newprocess(TI, 'sirius-hla-it-ti-control.py')
            self.add_object_to_level1(menu, TI)

            Cam = LEVEL2A('Cam', menu)
            Cam.setIcon(qta.icon('mdi.camera-outline'))
            self.connect_newprocess(Cam, 'sirius-hla-it-di-vlight.py')
            self.add_object_to_level1(menu, Cam)

            VA = self._set_va_menu('it')
            self.add_object_to_level1(menu, VA)

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
                PosAng = QAction('PosAng', optics)
                self.connect_newprocess(
                    PosAng, 'sirius-hla-'+sec+'-ap-posang.py')
                optics.addAction(PosAng)
            if 'tb' in sec:
                Emittance = QAction('Emittance Meas', optics)
                self.connect_newprocess(
                    Emittance, 'sirius-hla-tb-ap-emittance.py')
                optics.addAction(Emittance)
            if sec in {'bo', 'si'}:
                TuneCorr = QAction('Tune Correction', optics)
                icon = qta.icon('mdi.pulse', 'mdi.hammer', options=[
                    dict(scale_factor=1.3, offset=(0.0, 0.05)),
                    dict(scale_factor=0.72, offset=(-0.1, -0.3), hflip=True)])
                TuneCorr.setIcon(icon)
                self.connect_newprocess(
                    TuneCorr, 'sirius-hla-'+sec+'-ap-tunecorr.py')
                optics.addAction(TuneCorr)

                ChromCorr = QAction('Chromaticity Correction', optics)
                self.connect_newprocess(
                    ChromCorr, 'sirius-hla-'+sec+'-ap-chromcorr.py')
                optics.addAction(ChromCorr)

                trajfit = QAction('Trajectory Fitting', optics)
                self.connect_newprocess(
                    trajfit, 'sirius-hla-'+sec+'-ap-trajfit.py')
                optics.addAction(trajfit)
            if 'si' in sec:
                CurrLT = QAction('Current and Lifetime', optics)
                self.connect_newprocess(
                    CurrLT, 'sirius-hla-si-ap-currlt.py')
                optics.addAction(CurrLT)

                coupm = QAction('Coupling Meas', optics)
                self.connect_newprocess(
                    coupm, 'sirius-hla-si-ap-coupmeas.py')
                optics.addAction(coupm)
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
                DCCT.setObjectName(sec.upper()+'App')
                DCCT.setIcon(qta.icon('mdi.current-dc'))
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
                Tune.setIcon(qta.icon('mdi.pulse', scale_factor=1.3))
                self.connect_newprocess(Tune, 'sirius-hla-'+sec+'-di-tune.py')
                diag.addAction(Tune)
                VLight = QAction('VLight', diag)
                self.connect_newprocess(
                    VLight, 'sirius-hla-'+sec+'-di-vlight.py')
                diag.addAction(VLight)
            if 'si' not in sec:
                Scrns = QMenu('Screens', diag)
                Scrns.setIcon(qta.icon('mdi.camera-metering-center'))
                Scrns.setObjectName(sec.upper()+'App')
                for dev in get_scrn_list(sec.upper()):
                    act_dev = Scrns.addAction(dev)
                    self.connect_newprocess(
                        act_dev, ['sirius-hla-as-di-scrn.py', dev])
                diag.addMenu(Scrns)
            else:
                Scrap = QAction('Scrapers', diag)
                self.connect_newprocess(Scrap, 'sirius-hla-si-di-scraps.py')
                diag.addAction(Scrap)

                BbB = QMenu('BbB', diag)
                BbB.setObjectName(sec.upper()+'App')

                AllBbB = BbB.addAction('All')
                self.connect_newprocess(
                    AllBbB, ['sirius-hla-si-di-bbb.py', '-dev', 'all'])

                for idc in ['Horizontal', 'Vertical', 'Longitudinal']:
                    dev_pref = 'SI-Glob:DI-BbBProc-'+idc[0]
                    act_dev = BbB.addAction(idc)
                    self.connect_newprocess(
                        act_dev, ['sirius-hla-si-di-bbb.py', '-dev', dev_pref])

                diag.addMenu(BbB)
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

            if sec == 'it':
                lens = QAction('Lens', psmenu)
                self.connect_newprocess(lens, [scr, '--device', 'lens'])
                psmenu.addAction(lens)
                return psmenu

            all_dev = QAction(
                'All'+('' if sec != 'si' else ' Families'), psmenu)
            self.connect_newprocess(all_dev, scr)
            psmenu.addAction(all_dev)

            # dips
            if sec != 'li':
                dip = QAction('Dipoles', psmenu)
                self.connect_newprocess(dip, [scr, '--device', 'dipole'])
                psmenu.addAction(dip)
            else:
                spect = QAction('Spectrometer', psmenu)
                self.connect_newprocess(
                    spect, [scr, '--device', 'spectrometer'])
                psmenu.addAction(spect)

            # quads
            quad = QAction('Quadrupoles', psmenu)
            self.connect_newprocess(quad, [scr, '--device', 'quadrupole'])
            psmenu.addAction(quad)

            # sext
            if sec in {'bo', 'si'}:
                sext = QAction('Sextupoles', psmenu)
                self.connect_newprocess(sext, [scr, '--device', 'sextupole'])
                psmenu.addAction(sext)

            ps_indiv = {
                'Correctors': {
                    'device': 'corrector-slow',
                    'graphs': {'All': 'C(H|V)', 'CH': 'CH', 'CV': 'CV'},
                },
                'Trims': {
                    'device': 'trim-quadrupole',
                    'graphs': {'All': 'Q(F|D|[1-4]).*', 'QF': 'QF.*',
                               'QD': 'QD.*', 'Q1,Q2,Q3&&Q4': 'Q[1-4].*'},
                },
                'Skew Quadrupoles': {
                    'device': 'skew-quadrupole',
                    'graphs': {'All': 'QS'},
                },
                'Fast Correctors': {
                    'device': 'corrector-fast',
                    'graphs': {'All': 'FC(H|V)', 'FCH': 'FCH', 'FCV': 'FCV'},
                },
            }
            if sec != 'li':
                for pstype, data in ps_indiv.items():
                    type_menu = psmenu.addMenu(pstype)
                    type_menu.setObjectName(sec.upper()+'App')

                    if sec == 'si':
                        all_menu = type_menu.addMenu('All')
                        all_menu.setObjectName(sec.upper()+'App')
                    elif pstype == 'Correctors':
                        all_menu = type_menu

                    # list
                    all_lst_act = QAction('List', all_menu)
                    self.connect_newprocess(
                        all_lst_act, [scr, '--device', data['device']])
                    all_menu.addAction(all_lst_act)

                    # graphs
                    if len(data['graphs']) > 1:
                        all_gph_menu = all_menu.addMenu('Graph')
                        all_gph_menu.setObjectName(sec.upper()+'App')
                        for label, filt in data['graphs'].items():
                            act = QAction(label, all_gph_menu)
                            self.connect_newprocess(
                                act, ['sirius-hla-as-ps-graphmon.py',
                                      '--section', sec.upper(), '--device', filt])
                            all_gph_menu.addAction(act)
                    else:
                        all_gph_act = QAction('Graph', all_menu)
                        self.connect_newprocess(
                            all_gph_act,
                            ['sirius-hla-as-ps-graphmon.py',
                             '--section', sec.upper(), '--device',
                             data['graphs']['All']])
                        all_menu.addAction(all_gph_act)

                    if sec != 'si':
                        break

                    # subsectors
                    sec_menu = type_menu.addMenu('Subsectors')
                    sec_menu.setObjectName('SIApp')
                    for i in range(20):
                        act = sec_menu.addAction('SI-{:02d}'.format(i+1))
                        self.connect_newprocess(
                            act, [scr, '--device', data['device'],
                                  '--subsection', '{:02d}.*'.format(i+1)])

                    # trims fams
                    if pstype != 'Trims':
                        continue

                    fam_all_menu = type_menu.addMenu('Families')
                    fam_all_menu.setObjectName('SIApp')
                    fams = PSSearch.get_psnames(
                        {'sec': 'SI', 'sub': 'Fam', 'dev': 'Q(D|F|[1-4]).*'})
                    for fam in fams:
                        fam = SiriusPVName(fam)
                        fam_menu = fam_all_menu.addMenu(fam.dev)
                        fam_menu.setObjectName('SIApp')
                        act1 = QAction('List', fam_menu)
                        self.connect_newprocess(
                            act1, [scr, '--device', fam, '-istrim'])
                        fam_menu.addAction(act1)
                        act2 = QAction('Graph', fam_menu)
                        self.connect_newprocess(
                            act2, ['sirius-hla-as-ps-graphmon.py',
                                   '--section', 'SI', '--device', fam.dev])
                        fam_menu.addAction(act2)
            else:
                corrs = QAction('Correctors', psmenu)
                self.connect_newprocess(
                    corrs, [scr, '--device', 'corrector-slow'])
                psmenu.addAction(corrs)
                lens = QAction('Lens', psmenu)
                self.connect_newprocess(lens, [scr, '--device', 'lens'])
                psmenu.addAction(lens)
                slnd = QAction('Solenoids', psmenu)
                self.connect_newprocess(slnd, [scr, '--device', 'solenoid'])
                psmenu.addAction(slnd)

            if sec == 'bo':
                skew = QAction('Skew Quadrupoles', psmenu)
                self.connect_newprocess(
                    skew, [scr, '--device', 'skew-quadrupole'])
                psmenu.addAction(skew)

                wfmerr = QAction('Waveform Error', psmenu)
                self.connect_newprocess(wfmerr, 'sirius-hla-bo-ps-wfmerror.py')
                psmenu.addAction(wfmerr)

            return psmenu

        def _set_pu_menu(self, sec):
            pumenu = LEVEL2M('PU', self)
            pumenu.setObjectName(sec.upper()+'App')
            script = 'sirius-hla-' + sec + '-pu-control.py'
            if sec == 'si':
                pmag = QAction('Injection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'InjSI'])
                pumenu.addAction(pmag)
                pmag = QAction('Pingers', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'Ping'])
                pumenu.addAction(pmag)
            elif sec == 'bo':
                pmag = QAction('Injection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'InjBO'])
                pumenu.addAction(pmag)
                pmag = QAction('Ejection', pumenu)
                self.connect_newprocess(pmag, [script, '-s', 'EjeBO'])
                pumenu.addAction(pmag)
            elif sec == 'as':
                pmag = QAction('InjBO, EjeBO, InjSI && Ping', pumenu)
                self.connect_newprocess(
                    pmag, 'sirius-hla-as-pu-control.py')
                pumenu.addAction(pmag)
                pmag = QAction('TB, BO, TS && SI', pumenu)
                self.connect_newprocess(
                    pmag, ['sirius-hla-as-pu-control.py', '-g', 'sectors'])
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

        def _set_va_menu(self, sec):
            secl = sec.lower()
            menu = LEVEL2M('VA', self)
            menu.setObjectName(sec.upper()+'App')

            if sec != 'it':
                agilent = QAction('Agilent', menu)
                self.connect_newprocess(
                    agilent,
                    'sirius-hla-'+secl+'-va-agilent4uhv-overview',
                    is_pydm=True)
                menu.addAction(agilent)

            mks = QAction('MKS', menu)
            self.connect_newprocess(
                mks,
                'sirius-hla-'+secl+'-va-mks937b-overview',
                is_pydm=True)
            menu.addAction(mks)

            return menu

        def connect_newprocess(self, button, cmd, is_pydm=False):
            util.connect_newprocess(button, cmd, parent=self, is_pydm=is_pydm)

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
