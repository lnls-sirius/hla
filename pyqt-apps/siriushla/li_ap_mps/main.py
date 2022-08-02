''' Monitor Protection System Controller Interface '''
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGroupBox, QHBoxLayout, \
    QGridLayout, QLabel, QTabWidget, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMSpinbox
from .util import PV_MPS, MPS_PREFIX, CTRL_TYPE, GROUP_POS, \
    GROUP_POSALL, LBL_MPS, LBL_WATER, PV_TEMP_MPS, TEMP_TYPE, LBL_ALL
from ..util import get_appropriate_color
from ..widgets import PyDMLedMultiChannel,\
     PyDMLed, SiriusPushButton
from .bypass_btn import BypassBtn


class MPSControl(QWidget):
    ''' Monitor Protection System Controller Interface '''

    def __init__(self, parent=None, prefix=''):
        '''Contain all the graphic interface data'''
        super().__init__(parent)

        self.prefix = prefix + ('-' if prefix else '')
        self.pv_obj = {}
        self.led_clicked = False
        self.all_clicked = False
        self.stop = False

        color = get_appropriate_color('LI')
        self.setObjectName('LIApp')
        self.setWindowIcon(qta.icon('mdi.monitor-dashboard', color=color))

        self.setWindowTitle('LI MPS Controls')
        self._setupUi()

    def eventFilter(self, obj_wid, event):
        ''' Hover listener with hover function'''
        obj = self.pv_obj.get(obj_wid)
        if event.type() == QEvent.Leave:
            if self.led_clicked:
                self.controlHiddenBox(
                    obj.get("name"), obj.get("layout"), obj.get("config"))
                self.stop = False
        return False

    def getDeviceName(self, pv_name):
        ''' Set device name '''
        if 'LA-RF:LLRF:KLY' in pv_name:
            device_name = ''
        else:
            device_name = MPS_PREFIX
        return device_name

    def getCtrlWidget(self, pv_name, ctrl_type, config):
        '''Display the specific control widget'''
        device_name = self.getDeviceName(pv_name)
        if ctrl_type in ['_I', '_L', '']:
            ch2vals = {
                device_name + pv_name + ctrl_type: config}
            widget = PyDMLedMultiChannel(self)
            widget.set_channels2values(ch2vals)
            if pv_name == 'HeartBeat':
                widget.setOffColor(PyDMLed.Yellow)
        elif ctrl_type == '_B':
            widget = BypassBtn(
                self,
                init_channel=device_name + pv_name + ctrl_type)
        elif ctrl_type == '_R':
            widget = SiriusPushButton(
                self,
                init_channel=device_name + pv_name + ctrl_type,
                label='Reset',
                pressValue=1,
                releaseValue=0)
        widget.setStyleSheet('''
            min-width: 3.2em; max-width: 4.2em;
            min-height: 1.29em; max-height: 1.29em;
        ''')
        return widget

    def statusBox(self, pv_name, config):
        ''' Display the status widget'''
        sb_hlay = QHBoxLayout()
        sb_hlay.addWidget(
            self.getCtrlWidget(pv_name, '', config), 1)
        return sb_hlay

    def getTempWidget(self, pv_name, temp_type):
        ''' Display the temperature label widget '''
        device_name = self.getDeviceName(pv_name)
        if temp_type == 'Thrd':
            widget = PyDMSpinbox(
                parent=self,
                init_channel=device_name + pv_name + temp_type
            )
            widget.showStepExponent = False
        else:
            widget = PyDMLabel(
                parent=self,
                init_channel=device_name + pv_name + temp_type
            )
            widget.showUnits = True
        return widget

    def clearLayout(self, lay):
        '''Erase the layout's content'''
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        return lay

    def controlHiddenBox(self, pv_name, cb_glay, config):
        '''Display the status of the PV - Hidden control Box'''

        if cb_glay == '':
            cb_glay = QGridLayout()
        else:
            cb_glay = self.clearLayout(cb_glay)

        widget = self.getCtrlWidget(pv_name, '_L', config)
        widget.clicked.connect(
            lambda: self.controlBox(pv_name, cb_glay, config, True, 0))
        cb_glay.addWidget(widget, 1, 0, 1, 1)

        return cb_glay

    def controlBox(self, pv_name, lay, config, has_title, wid_type):
        ''' Display the control features - Open control Box'''

        if lay != '':
            lay = self.clearLayout(lay)
        else:
            lay = QGridLayout()
        pos = [0, 0]
        self.led_clicked = True
        for control_name in CTRL_TYPE:
            if self.getParamAll(has_title, pv_name, wid_type):
                lb_title = QLabel(control_name)
                lb_title.setAlignment(Qt.AlignCenter)
                lay.addWidget(lb_title, pos[0], pos[1], 1, 1)
            ctrl_widget = self.getCtrlWidget(
                pv_name, CTRL_TYPE.get(control_name), config)
            lay.addWidget(ctrl_widget, pos[0]+1, pos[1], 1, 1)
            pos[1] += 1
        return lay

    def controlWidget(self, pv_name, lay, config):
        '''Create the control widget with opening and closing functions'''
        '''Default - closed'''

        widget = QWidget()
        hlay = QHBoxLayout()

        if 'WFS' in pv_name:
            hlay.addWidget(
                self.setPvLbl(pv_name))

        control_layout = self.controlHiddenBox(pv_name, lay, config)
        widget.setLayout(control_layout)
        self.pv_obj.update(
            {widget: {
                "name": pv_name,
                "layout": control_layout,
                "config": config
            }})
        widget.installEventFilter(self)
        widget.setObjectName('Container')
        widget.setStyleSheet('''
            #Container::hover{
                background-color: #ff8b98;
                border-radius: 1em;
            }
        ''')
        hlay.addWidget(widget)
        return hlay

    def gateValve(self, pv_name, config):
        ''' Display the gate valves widget '''
        device_name = self.getDeviceName(pv_name)
        if 'U' in pv_name:

            if 'Open' in pv_name:
                name = 'Open'
            else:
                name = 'Close'

            pb_lay = QHBoxLayout()
            widget = SiriusPushButton(
                        self,
                        init_channel=device_name + pv_name,
                        label=name,
                        pressValue=1,
                        releaseValue=0)
            widget.setStyleSheet('''
                min-width: 3.2em; max-width: 4.2em;
                min-height: 1.29em; max-height: 1.29em;
            ''')
            pb_lay.addWidget(widget)
            return pb_lay
        else:
            return self.statusBox(pv_name, config)

    def tempMonBox(self, pv_name):
        ''' Display the status features for the temperature monitor'''
        lay = QHBoxLayout()
        for temp_name in TEMP_TYPE:
            ctrl_widget = self.getTempWidget(
                pv_name, TEMP_TYPE.get(temp_name))
            lay.addWidget(ctrl_widget, 1)
            ctrl_widget.setAlignment(Qt.AlignCenter)
        return lay

    def genStringTempPV(self, name, prefix_num, name_num):
        ''' Generate Temperature PV name '''
        return name + str(prefix_num) + 'Temp' + str(name_num)

    def getPVConfig(self, config, index):
        ''' Get if the PV has configuration 1 or 0'''

        if isinstance(config, list):
            return config[index]
        return config

    def getPVControl(self, is_control, index):
        ''' Get if the PV is a control or a status'''

        if isinstance(is_control, list):
            return is_control[index]
        return is_control

    def countGen(self, count, val):
        ''' Counter for water data positioning '''
        if count[1] >= val:
            count[0] += 1
            count[1] = 1
        else:
            count[1] += 1
        return count

    def countVA(self, count):
        ''' Counter for vaccum data positioning '''

        if count in [
            [2, 3], [3, 3], [6, 3],
            [11, 3], [12, 3]
        ]:
            count[1] += 1
        if count in [
            [4, 1], [5, 1], [8, 1],
            [10, 1], [13, 1], [15, 1]
        ]:
            count[1] += 3

        count = self.countGen(count, 4)
        return count

    def countWater(self, count):
        if count in [
            [2, 5], [3, 5]
        ]:
            count[1] += 3
        count = self.countGen(count, 6)
        return count

    def countTemp(self, count, title):
        ''' Counter for temperature data positioning '''
        if title == 'Water Temperature':
            orient = [1, 0, 6]
        else:
            orient = [0, 1, 2]

        if count[orient[1]] >= orient[2]:
            count[orient[0]] += 1
            count[orient[1]] = 1
        else:
            count[orient[1]] += 1
        return count

    def updateCount(self, count, title):
        ''' Update counter for data positioning '''
        if title == 'Klystrons':
            count = self.countGen(count, 4)
        elif title == 'Water':
            count = self.countWater(count)
        elif title == 'Modulator':
            count = self.countGen(count, 2)
        elif title == 'Gate Valve':
            count = self.countGen(count, 5)
        elif title in ['Temperature', 'Water Temperature']:
            self.countTemp(count, title)
        elif title == 'VA':
            count = self.countVA(count)
        else:
            count = self.countGen(count, 1)

        return count

    def setTitleLabel(self, item, axis, layout):
        ''' Display title labels '''
        pos = [0, 0]
        for pos[axis] in range(1, len(item)+1):
            lbl_header = QLabel('<h4>'+item[pos[axis]-1]+'</h4>')
            lbl_header.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_header, pos[0], pos[1], 1, 1)
            if axis == 0:
                lbl_header.setStyleSheet(
                    'QLabel{min-width:6em; max-width:6em;}')
        return layout

    def setPvLbl(self, pv_name):
        ''' Display the water title label'''
        lbl_pv = LBL_WATER.get(pv_name)
        lbl_title_wid = QLabel(lbl_pv)
        lbl_title_wid.setAlignment(Qt.AlignCenter)
        return lbl_title_wid

    def setParamLabel(self, layout):
        ''' Display Temperature parameters labels '''
        pos = 0
        for _ in range(0, 2):
            for item in TEMP_TYPE:
                lbl_param = QLabel(item)
                lbl_param.setAlignment(Qt.AlignCenter)
                layout.addWidget(lbl_param, 1, pos, 1, 1)
                pos += 1
        return layout

    def setTempHeader(self, item_list, layout):
        ''' Display Temperature header labels '''
        widget = QWidget()
        hd_glay = QGridLayout()
        pos = 0
        for item in item_list:
            lbl_header = QLabel('<h4>'+item+'</h4>')
            lbl_header.setAlignment(Qt.AlignCenter)
            hd_glay.addWidget(lbl_header, 0, pos, 1, 3)
            pos += 3

        hd_glay = self.setParamLabel(hd_glay)
        hd_glay.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(hd_glay)
        layout.addWidget(widget, 0, 1, 1, 6)
        return layout

    def getSingleTitle(self, title, layout):
        ''' Display a single Title '''
        if title in LBL_MPS:
            lbl_item = LBL_MPS.get(title)
            layout = self.setTitleLabel(lbl_item[0], 0, layout)
            if title not in ['Water Temperature', 'Temperature']:
                layout = self.setTitleLabel(lbl_item[1], 1, layout)
            else:
                layout = self.setTempHeader(lbl_item[1], layout)
        return layout

    def getParamAll(self, has_title, pv_name, wid_type):
        if wid_type == 0 or pv_name in LBL_ALL:
            return has_title
        return False

    def dispayHiddenControls(self, pv_name, control, config):
        if control:
            return self.controlWidget(
                pv_name, '',
                config)
        return self.statusBox(pv_name, config)

    def dispayAllControls(self, pv_name, control, config):
        if control:
            widget = QWidget()
            hlay = QHBoxLayout()
            if 'WFS' in pv_name:
                hlay.addWidget(
                    self.setPvLbl(pv_name))
            control_layout = self.controlBox(pv_name, '', config, control, 1)
            widget.setLayout(control_layout)
            hlay.addWidget(widget)
            return hlay
        else:
            return self.statusBox(pv_name, config)

    def displayGroup(self, pv_data, title, group_type):
        ''' Display one MPS group '''
        dg_glay = QGridLayout()
        group = QGroupBox()
        count = [1, 1]

        dg_glay = self.getSingleTitle(title, dg_glay)
        index = 0
        for pv_name in pv_data.get('name'):
            if title != 'Gate Valve':
                if group_type == 0:
                    dg_glay.addLayout(
                        self.dispayHiddenControls(
                            pv_name,
                            self.getPVControl(pv_data.get('control'), index),
                            self.getPVConfig(pv_data.get('config'), index)),
                        count[0], count[1], 1, 1)
                else:
                    dg_glay.addLayout(
                        self.dispayAllControls(
                            pv_name,
                            self.getPVControl(pv_data.get('control'), index),
                            self.getPVConfig(pv_data.get('config'), index)),
                        count[0], count[1], 1, 1)
            else:
                dg_glay.addLayout(
                    self.gateValve(pv_name,
                        self.getPVConfig(pv_data.get('config'), index)),
                    count[0], count[1], 1, 1)
            count = self.updateCount(count, title)
            index += 1

        group.setTitle(title)
        group.setLayout(dg_glay)

        return group

    def displayTempGroup(self, pv_data, title):
        ''' Display one temperature group'''
        dtg_glay = QGridLayout()
        dtg_glay.setHorizontalSpacing(0)
        group = QGroupBox()
        count = [1, 1]

        dtg_glay = self.getSingleTitle(title, dtg_glay)
        for counter_prefix in range(1, pv_data[0][0]+1):
            for counter_name in range(1, pv_data[0][1]+1):
                pv_name = self.genStringTempPV(
                    pv_data[1], counter_prefix, counter_name)

                dtg_glay.addLayout(
                    self.tempMonBox(pv_name),
                    count[0], count[1], 1, 1)
                count = self.updateCount(count, title)

        group.setTitle(title)
        group.setLayout(dtg_glay)

        return group

    def displayMpsGroups(self, group_type):
        ''' Display all the MPS groups'''
        mp_glay = QGridLayout()
        for group in PV_MPS:
            pv_data = PV_MPS.get(group)

            if group_type == 0:
                group_pos = GROUP_POS.get(group)
            else:
                group_pos = GROUP_POSALL.get(group)
            mp_glay.addWidget(
                self.displayGroup(pv_data, group, group_type),
                group_pos[0], group_pos[1], group_pos[2], group_pos[3])
        return mp_glay

    def displayTempGroups(self):
        ''' Display all the temperatures groups'''
        dt_glay = QGridLayout()
        for group in PV_TEMP_MPS:
            pv_data = PV_TEMP_MPS.get(group)
            group_pos = GROUP_POS.get(group)
            dt_glay.addWidget(
                self.displayTempGroup(pv_data, group),
                group_pos[0], group_pos[1], group_pos[2], group_pos[3])
        return dt_glay

    def displayControlMPS(self, tab_type):
        ''' Display the desired tab widget '''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if tab_type != 0:
            if_glay.addLayout(self.displayTempGroups(), 0, 0, 1, 1)

        if_glay.setAlignment(Qt.AlignTop)
        wid.setLayout(if_glay)

        if tab_type == 0:
            self.mps_glay = if_glay
            self.changeWid(self.mps_glay)
        return wid

    def displayTabs(self):
        ''' Display all the tabs '''
        tab = QTabWidget()
        tab.setObjectName("LITab")
        tab.addTab(self.displayControlMPS(0), "MPS Controls")
        tab.addTab(self.displayControlMPS(1), "Temperature")
        tab.currentChanged.connect(self.adjustSize)
        return tab

    def changeWid(self, layout):
        layout = self.clearLayout(layout)
        if self.all_clicked:
            wid = QWidget()
            wid.setLayout(self.displayMpsGroups(1))
            layout.addWidget(wid)
            self.all_clicked = False
        else:
            wid = QWidget()
            wid.setLayout(self.displayMpsGroups(0))
            layout.addWidget(wid)
            self.all_clicked = True

    def displayHeader(self):
        ''' Display the window header '''
        wid = QWidget()
        hd_hlay = QHBoxLayout()
        lbl_title = QLabel("<h2>Linac Machine Protection System</h2>")
        lbl_title.setAlignment(Qt.AlignCenter)
        hd_hlay.addWidget(lbl_title, 10)

        btn_all = QPushButton("Hide/Show All")
        btn_all.clicked.connect(
            lambda: self.changeWid(self.mps_glay))
        hd_hlay.addWidget(btn_all, 1)
        wid.setLayout(hd_hlay)

        return wid

    def _setupUi(self):
        ''' Display the tabs of the graphic interface '''

        if_glay = QGridLayout()
        if_glay.addWidget(self.displayTabs(), 1, 0, 1, 1)
        if_glay.addWidget(self.displayHeader(), 0, 0, 1, 1)
        if_glay.setAlignment(Qt.AlignTop)

        self.setLayout(if_glay)
