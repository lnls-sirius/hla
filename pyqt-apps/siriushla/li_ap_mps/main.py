''' Diagnostic Interface of the LINAC's BPM'''
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGroupBox, QHBoxLayout, \
    QVBoxLayout, QGridLayout, QLabel, QTabWidget
import qtawesome as qta

from .util import PV_MPS, MPS_PREFIX, CTRL_TYPE, GROUP_POS, LBL_MPS, LBL_WATER
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, PyDMLedMultiChannel,\
     PyDMLed, SiriusPushButton
from .custom_widget import BypassBtn


class MPSController(SiriusMainWindow):
    ''' Monitor Protection System Controller Interface '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.pv_obj = {}
        self.clicked = False

        color = get_appropriate_color('LI')
        self.setObjectName('LIApp')
        self.setWindowIcon(qta.icon('mdi.monitor-dashboard', color=color))

        self.setWindowTitle('LI MPS Controller')
        self._setupUi()

    def clearLayout(self, lay):
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        return lay

    def controlWidget(self, pv_name, lay, config):
        widget = QWidget()
        vlay = QVBoxLayout()

        if pv_name.find('WFS') != -1:
            vlay.addWidget(
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
                border-radius: 5px;
            }
        ''')
        vlay.addWidget(widget)
        return vlay

    def controlBox(self, pv_name, lay, config):
        lay = self.clearLayout(lay)
        pos = [1, 0]
        self.clicked = True
        for control_name in CTRL_TYPE:
            lb_title = QLabel(control_name)
            lay.addWidget(lb_title, pos[0], pos[1], 1, 1)
            ctrl_widget = self.getCtrlWidget(
                pv_name, CTRL_TYPE.get(control_name), config)
            lay.addWidget(ctrl_widget, pos[0]+1, pos[1], 1, 1)
            pos[1] += 1
            if pos[1] >= 2:
                pos[1] = 0
                pos[0] += 2
        return lay

    def setPvLbl(self, pv_name):
        pvLbl = LBL_WATER.get(pv_name)
        lb_titleWid = QLabel(pvLbl)
        lb_titleWid.setAlignment(Qt.AlignCenter)
        return lb_titleWid

    def controlHiddenBox(self, pv_name, cb_glay, config):
        '''Display the box for the control Interface'''

        if cb_glay == '':
            cb_glay = QGridLayout()
        else:
            cb_glay = self.clearLayout(cb_glay)

        widget = self.getCtrlWidget(pv_name, '_L', config)
        widget.clicked.connect(
            lambda: self.controlBox(pv_name, cb_glay, config))
        cb_glay.addWidget(widget, 1, 0, 1, 1)

        return cb_glay

    def eventFilter(self, ob, event):
        obj = self.pv_obj.get(ob)
        # if event.type() == QEvent.Enter:
        #     self.controlBox(obj.get("name"), obj.get("layout"))
        #     self.stop = True
        #     return True
        if event.type() == QEvent.Leave:
            if self.clicked:
                self.controlHiddenBox(obj.get("name"), obj.get("layout"), obj.get("config"))
                self.stop = False
        return False

    def getDeviceName(self, pv_name):
        if pv_name.find('LA-RF:LLRF:KLY') != -1:
            device_name = ''
        else:
            device_name = MPS_PREFIX
        return device_name

    def getCtrlWidget(self, pv_name, ctrl_type, config):
        device_name = self.getDeviceName(pv_name)
        if ctrl_type in ['_I', '_L', '']:
            # edit
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
        return widget

    def getListSize(self, pv_data):
        for item in pv_data:
            if type(item) == list:
                return len(item)
        return 1

    def statusBox(self, pv_name, config):
        sb_hlay = QHBoxLayout()
        sb_hlay.addWidget(
            self.getCtrlWidget(pv_name, '', config), 1)
        return sb_hlay

    def genStringPV(self, prefix, suffix, num):

        if prefix in ['HeartBeat', 'LAWarn', 'LAAlarm', 'Gun', 'WaterState']:
            pv_name = str(prefix)+str(suffix)
        elif prefix == 'PPState':
            pv_name = str(prefix)+str(num+6)+str(suffix)
        else:
            pv_name = str(prefix)+str(num)+str(suffix)

        return pv_name

    def getLoopQuant(self, loopQuant, index):
        if type(loopQuant) == list:
            return loopQuant[index]+1
        else:
            return loopQuant+1

    def getPvConfig(self, config, index):
        if type(config) == list:
            return config[index]
        else:
            return config

    def getPVComplement(self, string, index):
        if type(string) == list:
            return string[index]
        else:
            return string

    def countWater(self, count):
        if count[1] >= 4:
            count[0] += 1
            count[1] = 1
        else:
            count[1] += 1
        return count

    def countKGM(self, count, title):
        val = 2
        if title == 'Modulator Status':
            val = 1
        if count[0] >= val:
            count[1] += 1
            count[0] = 1
        else:
            count[0] += 1
        return count

    def countVA(self, count):
        if count in [
            [7, 2], [9, 2], [12, 2], [14, 2],
            [7, 3], [9, 3], [12, 3], [14, 3],
            [7, 4], [14, 4]]:
            count[0] += 1
        elif count in [[3, 2], [3, 3]]:
            count[0] += 2
        elif count == [1, 4]:
            count[0] += 5
        elif count == [9, 4]:
            count[0] += 4

        count[0] += 1

        if count[0] >= 17:
            count[1] += 1
            count[0] = 1
        return count

    def updateCount(self, count, title):
        if title in ['Water']:
            count = self.countWater(count)
        elif title in ['Klystrons', 'General Control', 'Modulator Status']:
            count = self.countKGM(count, title)
        else:
            count = self.countVA(count)

        return count

    def setTitleLabel(self, item, axis, layout):
        pos = [0, 0]
        for pos[axis] in range(1, len(item)+1):
            lbl_header = QLabel(item[pos[axis]-1])
            lbl_header.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_header, pos[0], pos[1], 1, 1)
        return layout

    def getSingleTitle(self, title, layout):
        pos = [0, 0]
        if title in LBL_MPS:
            lbl_item = LBL_MPS.get(title)
            layout = self.setTitleLabel(lbl_item[0], 0, layout)
            layout = self.setTitleLabel(lbl_item[1], 1, layout)
        return layout

    def displayGroup(self, pv_data, pv_size, title):
        dg_glay = QGridLayout()
        group = QGroupBox()
        count = [1, 1]

        dg_glay = self.getSingleTitle(title, dg_glay)
        for index in range(0, pv_size):
            loop_quant = self.getLoopQuant(pv_data[0], index)
            for counter in range(1, loop_quant):
                pv_name = self.genStringPV(
                    self.getPVComplement(pv_data[1], index),
                    self.getPVComplement(pv_data[2], index),
                    counter)
                if pv_data[4]:
                    dg_glay.addLayout(
                        self.controlWidget(
                            pv_name, '',
                            self.getPvConfig(pv_data[3], index)),
                        count[0], count[1], 1, 1)
                else:
                    dg_glay.addLayout(
                        self.statusBox(pv_name,
                        self.getPvConfig(pv_data[3], index)),
                        count[0], count[1], 1, 1)

                count = self.updateCount(count, title)

        group.setTitle(title)
        group.setLayout(dg_glay)

        return group

    def displayMpsGroups(self):
        dm_glay = QGridLayout()
        for group in PV_MPS:
            pv_data = PV_MPS.get(group)
            pv_size = self.getListSize(pv_data)
            group_pos = GROUP_POS.get(group)
            dm_glay.addWidget(
                self.displayGroup(pv_data, pv_size, group),
                group_pos[0], group_pos[1], group_pos[2], group_pos[3])

        return dm_glay

    def displayControlMPS(self):
        wid = QWidget(self)
        if_glay = QGridLayout()
        if_glay.addLayout(self.displayMpsGroups(), 0, 0, 1, 1)

        if_glay.setAlignment(Qt.AlignTop)

        wid.setLayout(if_glay)
        return wid

    def _setupUi(self):

        tab = QTabWidget()
        tab.setObjectName("LITab")
        tab.addTab(self.displayControlMPS(), "MPS Controller")

        self.setCentralWidget(tab)
