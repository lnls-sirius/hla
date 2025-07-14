from qtpy.QtWidgets import QVBoxLayout, QGridLayout, QLabel, \
    QWidget, QGroupBox, QHBoxLayout

from qtpy.QtCore import Qt

from ...widgets import SiriusLabel, SiriusEnumComboBox, \
    SiriusPushButton, SiriusLedAlert, PyDMLed
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import RaBPMSearch

import qtawesome as qta

from ...common.afc_board import ipmi_mngr_pvs


class AFCAdvancedSettings(QWidget):
    def __init__(self, parent=None, prefix='', display='', data_prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.display = _PVName(display)
        self.data_prefix = data_prefix
        if display.sec == 'IA':
            if display.dev == 'AMCFPGAEVR':
                sec = 'AS'
            elif display.dev == 'FOFBCtrl':
                sec = 'SI'
        else:
            sec = display.sec
        self.setObjectName(f'{sec}App')
        self.setupui()

    def setupui(self):
        lay = QVBoxLayout(self)
        if self.display.dev == 'FOFBCtrl':
            tag = 'AFCv4.0 Settings'
        else:
            tag = 'AFCv3.1 Settings'
        lab = QLabel(
            f'<h2>{self.display} {tag}</h2>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lab)

        slot = RaBPMSearch.conv_devname_2_slot(self.display)

        lab_num = QLabel(
            f'<h4>AMC-{slot}</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(lab_num)

        pv_help = RaBPMSearch.get_bpm_pair(self.display)
        if pv_help is None:
            pass
        else:
            lab_help = QLabel(
                f'<h3>(also refers to {pv_help})</h3>',
                    self, alignment=Qt.AlignCenter)
            lay.addWidget(lab_help)

        amc_lay = QHBoxLayout()

        sensors_widget = self._sensorsAFC(slot)
        fru_widget = self._fruAFC(slot)

        amc_lay.addWidget(sensors_widget)
        amc_lay.addWidget(fru_widget)

        lay.addLayout(amc_lay)

    def _sensorsAFC(self, amc_number):
        if self.display.dev == 'FOFBCtrl':
            pv_list_sensors = ipmi_mngr_pvs.AFCv4_0_PV_LIST['sensors']

        else:
            pv_list_sensors = ipmi_mngr_pvs.AFCv3_1_PV_LIST['sensors']

        group = self._setup_pv_group(
            self.display, amc_number, pv_list_sensors)

        return group

    def _setup_pv_group(self, device, slot, pv_dict):
        device = _PVName(device)
        crate = RaBPMSearch.conv_devname_2_cratename(device)
        amc_number = slot

        sections = {
            "Pwr": QGroupBox("Power Module", self),
            "12V": QGroupBox("12V", self),
            "VADJ": QGroupBox("VADJ", self),
            "3V3": QGroupBox("3V3", self),
            "Temp": QGroupBox("Temperature", self)
        }
        layouts = {k: QGridLayout(sections[k]) for k in sections}

        wid = QWidget(self)
        lay_sensor = QGridLayout(wid)

        def add_volt_widgets(label, k, pv_name):
            lay = QGridLayout()
            lbl_title = QLabel(f"<h5>{label}</h5>", alignment=Qt.AlignCenter)
            if k[:3] in ['AMC', 'RTM']:
                lab_pv = QLabel(k[:3], alignment=Qt.AlignCenter)
            else:
                lab_pv = QLabel(k[:4], alignment=Qt.AlignCenter)
            slab_pv = SiriusLabel(
                self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}")
            slab_pv.showUnits = True
            lay.addWidget(lab_pv, 0, 0, alignment=Qt.AlignCenter)
            lay.addWidget(slab_pv, 0, 1, alignment=Qt.AlignCenter)
            return lbl_title, lay

        def add_curr_widgets(label, pv_name):
            lay = QGridLayout()
            lbl_title = QLabel(f"<h5>{label}</h5>", alignment=Qt.AlignCenter)
            slab_pv = SiriusLabel(
                self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}")
            slab_pv.showUnits = True
            lay.addWidget(slab_pv, 0, 0, alignment=Qt.AlignCenter)
            return lbl_title, lay

        def add_temp_widgets(k, pv_name):
            lay = QGridLayout()
            lab_pv = QLabel(k[4:], alignment=Qt.AlignCenter)
            slab_pv = SiriusLabel(
                self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}")
            slab_pv.showUnits = True
            lay.addWidget(lab_pv, 0, 0, 1, 2, alignment=Qt.AlignLeft)
            lay.addWidget(slab_pv, 0, 2, 1, 2, alignment=Qt.AlignRight)
            return lay

        def add_led_alert(pv_name):
            led = SiriusLedAlert(
                self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}")
            led.onColor = PyDMLed.LightGreen
            led.offColor = PyDMLed.Red
            return led

        row = {
            "12V": 1,
            "VADJ": 1,
            "3V3": 1,
            "Temp": 1
        }

        for k, pv_name in pv_dict.items():
            for section in sections:
                if section in pv_name and section in str(k):
                    layout = layouts[section]
                    if 'Mon' in pv_name:
                        if 'Pwr' in pv_name and 'Pwr' in str(k):
                            lay = QGridLayout()
                            lay.setHorizontalSpacing(40)
                            lab_pv = QLabel("<h5>Current</h5>",
                                            alignment=Qt.AlignCenter)
                            slab_pv = SiriusLabel(
                                self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}")
                            slab_pv.showUnits = True
                            lay.addWidget(lab_pv, 0, 0, 1, 2,
                                          alignment=Qt.AlignLeft)
                            lay.addWidget(slab_pv, 0, 2, 1, 2,
                                          alignment=Qt.AlignRight)
                            layout.addLayout(lay, 0, 0)
                        if 'Volt' in pv_name and 'Volt' in str(k):
                            volt_title, volt_lay = add_volt_widgets(
                                "Voltage", k, pv_name)
                            layout.addWidget(volt_title, 0, 0,
                                             alignment=Qt.AlignCenter)
                        if 'Curr' in pv_name and 'Curr' in str(k):
                            curr_title, curr_lay = add_curr_widgets(
                                "Current", pv_name)
                            layout.addWidget(curr_title, 0, 1,
                                             alignment=Qt.AlignCenter)
                            layout.addLayout(
                                volt_lay, row[section], 0, alignment=Qt.AlignCenter)
                            layout.addLayout(
                                curr_lay, row[section], 1, alignment=Qt.AlignCenter)
                            row[section] += 1
                        if section == 'Temp':
                            temp_lay = add_temp_widgets(k, pv_name)
                            layout.addLayout(temp_lay, row[section], 0)
                            row[section] += 1

                    elif 'Cte' in pv_name:
                        led = add_led_alert(pv_name)
                        if 'Volt' in pv_name and 'Volt' in str(k):
                            volt_lay.addWidget(
                                led, 0, 2, alignment=Qt.AlignCenter)
                        elif 'Curr' in pv_name and 'Curr' in str(k):
                            curr_lay.addWidget(
                                led, 0, 2, alignment=Qt.AlignCenter)
                        elif 'Temp' in pv_name and 'Temp' in str(k):
                            temp_lay.addWidget(
                                led, 0, 4, alignment=Qt.AlignRight)

        lay_sensor.addWidget(sections['Pwr'], 0, 0, alignment=Qt.AlignCenter)
        lay_sensor.addWidget(sections['12V'], 1, 0, alignment=Qt.AlignCenter)
        lay_sensor.addWidget(sections['VADJ'], 2, 0, alignment=Qt.AlignCenter)
        lay_sensor.addWidget(sections['3V3'], 3, 0, alignment=Qt.AlignCenter)
        lay_sensor.addWidget(sections['Temp'], 4, 0, alignment=Qt.AlignCenter)

        area = QGroupBox('Sensors', self)
        lay_area = QHBoxLayout(area)
        lay_area.addWidget(wid)
        return area

    def _fruAFC(self, amc_number):
        wid = QWidget(self)
        lay_fru = QGridLayout(wid)
        lay_fru.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter),
            0, 0, alignment=Qt.AlignLeft)
        lay_fru.addWidget(
            QLabel('<h4>Measurement</h4>', self, alignment=Qt.AlignCenter), 0, 1)

        row = 1
        if self.display.dev == 'FOFBCtrl':
            pv_list_fru = ipmi_mngr_pvs.AFCv4_0_PV_LIST['FRU']
        else:
            pv_list_fru = ipmi_mngr_pvs.AFCv3_1_PV_LIST['FRU']

        for k, pv_name in pv_list_fru.items():
            if 'PowerCtl-Sel' in pv_name:
                grbx = QGroupBox('Power Control', self)
                grbx_lay = QGridLayout(grbx)
                grbx_lay.setSpacing(30)
                crate = RaBPMSearch.conv_devname_2_cratename(self.display)
                scbx_pv = SiriusEnumComboBox(
                    self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_list_fru['PowerCtl']}"
                )
                grbx_lay.addWidget(scbx_pv, 0, 1)
                lay_fru.addWidget(grbx, row, 0, 1, 2)
                row += 1

            elif 'SoftRst-Cmd' in pv_name:
                grbx = QGroupBox('Soft. Reset', self)
                grbx_lay = QGridLayout(grbx)
                grbx_lay.setSpacing(30)
                crate = RaBPMSearch.conv_devname_2_cratename(self.display)

                cmd_button = SiriusPushButton(
                    self, label='Reset', icon=qta.icon('mdi.restart'),
                    init_channel=f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_list_fru['SoftRst']}"
                )
                grbx_lay.addWidget(cmd_button, 0, 1)

                label_mon = SiriusLabel(
                    self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_list_fru['SoftRstSts']}"
                )
                grbx_lay.addWidget(label_mon, 0, 2)

                lay_fru.addWidget(grbx, row, 0, 1, 2)
                row += 1

            elif 'Cte' in pv_name:
                crate = RaBPMSearch.conv_devname_2_cratename(self.display)
                label = QLabel(k, alignment=Qt.AlignCenter)
                slab_pv = SiriusLabel(
                    self, f"{crate}:{ipmi_mngr_pvs.DIS}-AMC-{amc_number}:{pv_name}"
                )

                lay_fru.addWidget(label, row, 0, alignment=Qt.AlignLeft)
                lay_fru.addWidget(slab_pv, row, 1, alignment=Qt.AlignCenter)
                row += 1

        return self._group_area(wid, 'FRU')

    def _group_area(self, widget, name):
        area = QGroupBox(f'{name}', self)
        lay_area = QHBoxLayout(area)
        lay_area.addWidget(widget)
        return area
