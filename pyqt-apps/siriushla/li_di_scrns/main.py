''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
from qtpy.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets  import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QFrame, QLabel, QGridLayout, QRadioButton, QStackedWidget
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMPushButton, \
    PyDMWaveformPlot, PyDMSpinbox, PyDMImageView, PyDMLineEdit
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, PyDMLedMultiChannel
from .util import DEVICES, SCREENS_PANEL, SCREENS_INFO, HEADER, \
    GRAPH, SCREEN
from .motorBtn import MotorBtn

class LiBeamProfile(SiriusMainWindow):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = get_appropriate_color('LI')

        self.device_name = 'LA-BI'

        self.setWindowIcon(qta.icon('mdi.camera-metering-center', color=color))
        self.setWindowTitle(self.device_name)
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
                _os.path.abspath(_os.path.dirname(__file__)), "linac.png"))
        self.stackScreens = QStackedWidget()
        self.stackScreen = QStackedWidget()
        self.stackGraphs = QStackedWidget()
        self._setupUi()

    def resizeEvent(self, event):
        ''' Resize Image'''
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height())
        )
        SiriusMainWindow.resizeEvent(self, event)

    def radioBtnClick(self):
        ''' Action on radio button change '''
        radioButton = self.sender()
        if radioButton.isChecked():
            self.selected_device = radioButton.device
            deviceIndex = DEVICES.index(self.selected_device)
            self.stackScreens.setCurrentIndex(deviceIndex)
            self.stackScreen.setCurrentIndex(deviceIndex)
            self.stackGraphs.setCurrentIndex(deviceIndex)

    def getPvName(self, device, pv_name):
        ''' Build PV name '''
        return self.device_name + ':' + device + ":" + pv_name

    def setWidgetType(self, widType, device, pv_name, label='', value=0):
        ''' Get widget type '''
        pvName = self.getPvName(device, pv_name)
        if widType == 'label':
            widget = PyDMLabel(self,
                init_channel=pvName)
            widget.showUnits = True
            widget.setAlignment(Qt.AlignCenter)
        elif widType == 'led':
            ch2vals = {pvName: value}
            widget = PyDMLedMultiChannel(self)
            widget.set_channels2values(ch2vals)
        elif widType == 'pushBtn':
            widget = PyDMPushButton(self,
                init_channel=pvName,
                label=label,
                pressValue=value)
        elif widType == 'spinBox':
            widget = PyDMSpinbox(
                init_channel=pvName)
            widget.showStepExponent = False
            widget.showUnits = True
        elif widType == 'lineEdit':
            widget = PyDMLineEdit(
                init_channel=pvName)
            widget.setAlignment(Qt.AlignCenter)
            widget.showUnits = True
        elif widType == 'motorBtn':
            widget = MotorBtn(
                init_channel=pvName)
        else:
            widget = QLabel("Error: Unknown device")
        widget.setMinimumWidth(60)
        widget.setFixedHeight(20)
        return widget

    def getRadioBtn(self, device):
        ''' Get the one radio button '''
        radiobutton = QRadioButton(device)
        radiobutton.device = device
        radiobutton.toggled.connect(self.radioBtnClick)
        if device == DEVICES[0]:
            radiobutton.setChecked(True)
        return radiobutton

    def setBasicInfo(self, device, label, pv_name):
        ''' Build one basic information Component '''
        bi_hlay = QHBoxLayout()
        bi_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignCenter)
        if label in ['Limit Mode', 'Motor Code', 'Counter', 'Sigma', 'Center']:
            widType = 'label'
        elif label == "Coefficient":
            widType = 'spinBox'
        elif label == "Centroid Threshold":
            widType = 'lineEdit'
        else:
            widType = 'led'
        bi_hlay.addWidget(
            self.setWidgetType(widType, device, pv_name))
        return bi_hlay

    def setRBVObj(self, device, pv_name, label, pv_prefix):
        ''' Build formatted RBV Component'''
        rbv_hlay = QHBoxLayout()
        rbv_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignCenter)
        for item in range(1, -1, -1):
            pvName = pv_prefix + pv_name[item]
            if 'RBV' not in pvName:
                if label in ['Gain', 'Exposure']:
                    widType = 'lineEdit'
                else:
                    widType = 'spinBox'
            else:
                widType = 'label'
            widget = self.setWidgetType(widType, device, pvName)
            widget.setMaximumWidth(75)
            if item != 0:
                rbv_hlay.addWidget(
                        widget,
                        alignment=Qt.AlignRight)
                if 'Size' in pv_name[0]:
                    sepLabel = QLabel("X")
                    sepLabel.setFixedWidth(10)
                    rbv_hlay.addWidget(
                        sepLabel,
                        Qt.AlignCenter)
            else:
                rbv_hlay.addWidget(
                        widget,
                        alignment=Qt.AlignLeft)
        return rbv_hlay

    def setGraph(self, device, graph_data, title):
        '''Build a graph widget'''

        graph_plot = PyDMWaveformPlot(background="#ffffff")
        graph_plot.setTitle(title)
        graph_plot.setLabel(
            'left',
            text=graph_data.get("labelY"))
        graph_plot.setLabel(
            'bottom',
            text=graph_data.get("labelX"))
        graph_plot.addChannel(
            y_channel=self.getPvName(device, graph_data['channel']['centroid']),
            color="#ff8b98",
            lineWidth=1)
        graph_plot.addChannel(
            y_channel=self.getPvName(device, graph_data['channel']['data']),
            color="#ff0000",
            lineWidth=1)
        graph_plot.setMinimumSize(50, 100)

        return graph_plot

    def setSingleScrn(self, device):
        ''' Build a single screen Component '''
        group = QGroupBox()
        ss_vlay = QVBoxLayout()

        imageWid = PyDMImageView(
                image_channel=self.getPvName(device, SCREEN['Screen']['data']),
                width_channel=self.getPvName(device, SCREEN['Screen']['width']))
        imageWid.setMinimumSize(500, 100)

        ss_vlay.addWidget(
            imageWid, 5)
        ss_vlay.addLayout(
            self.setScrnInfo(device), 1)

        group.setTitle(SCREEN['title'] + " " + device)
        group.setLayout(ss_vlay)
        return group

    def setScrnHeader(self, device, layout):
        ''' Build the screen panel header '''
        count = 0
        for text in SCREENS_PANEL.get('labels'):
            layout.addWidget(
                QLabel(text),
                0, count,
                alignment=Qt.AlignCenter)
            count += 1
        return layout

    def setPanelInfo(self, device, layout, row):
        ''' Build the information of one screen in screen panel '''
        pvList = SCREENS_PANEL.get('content')
        pv_name = 'MOTOR'+":"
        count = 0

        layout.addWidget(
            self.getRadioBtn(device),
            row, count, alignment=Qt.AlignCenter)

        count += 1
        for item in range(0, len(pvList)):
            if item == 0:
                widType = 'label'
            else:
                widType = 'led'

            layout.addWidget(
                self.setWidgetType(
                    widType, device, pv_name+pvList[item]),
                row, count,
                alignment=Qt.AlignCenter)
            count+=1

        layout.addWidget(
                self.setWidgetType('led', device, pv_name+pvList[0], value=1),
                row, count,
                alignment=Qt.AlignCenter)

        return layout

    def setMotorsConfig(self):
        ''' Build the Motor Control Buttons'''
        mc_hlay = QHBoxLayout()
        for label, channel in HEADER.items():
            mc_hlay.addWidget(
                self.setWidgetType('pushBtn', "PRF:MOTOR", channel, label),
                alignment=Qt.AlignCenter)
        return mc_hlay

    def setScrnPanel(self):
        ''' Build the Screens Panel Component'''
        group = QGroupBox()
        am_glay = QGridLayout()

        am_glay = self.setScrnHeader(
            SCREENS_PANEL.get('title'), am_glay)

        row = 1
        for device in DEVICES:
            am_glay = self.setPanelInfo(
                device, am_glay, row)
            row += 1

        am_glay.addLayout(
            self.setMotorsConfig(),
            row, 0, 1, 4)

        group.setTitle(SCREENS_PANEL.get('title'))
        group.setLayout(am_glay)
        return group

    def getScrnSelBtns(self, device, label):
        ''' Get the button label for the position of the screen '''
        if isinstance(label, dict):
            if device in label.keys():
                return label[device]
            return label["GEN"]
        return label

    def setScrnSelection(self, selectionInfo, device):
        ''' Build the screen position selection menu '''
        widget = QGroupBox()
        ms_vlay = QVBoxLayout()
        ms_vlay.addWidget(
            PyDMLabel(
                init_channel=self.getPvName(
                    device, 'MOTOR:' + selectionInfo.get('selected'))),
            alignment=Qt.AlignCenter)

        for pv_name, label in selectionInfo.get('content').items():
            label = self.getScrnSelBtns(device, label)
            if label:
                ms_vlay.addWidget(
                    PyDMPushButton(
                        init_channel=self.getPvName(device, 'MOTOR:' + pv_name),
                        label=label))
        widget.setLayout(ms_vlay)
        widget.setTitle("Position")
        return widget

    def setZeroOpt(self, item, device):
        ''' Build Zero Operation Component'''
        zo_hlay = QHBoxLayout()
        zo_hlay.addWidget(
            QLabel(item["title"]))
        count = 0
        for label, pv_name in item["content"].items():
            widget = self.setWidgetType('pushBtn', device, "MOTOR:"+pv_name, label)
            if count == 1:
                widget.setStyleSheet("background-color:#ffff00;")
            zo_hlay.addWidget(
                widget,
                alignment=Qt.AlignCenter)
            count += 1
        return zo_hlay

    def setLight(self, device, pvList, title):
        ''' Build Light Component '''
        lo_hlay = QHBoxLayout()
        lo_hlay.addWidget(
            QLabel(title))
        lo_hlay.addWidget(
            self.setWidgetType('led', device, "MOTOR:"+pvList[0]))
        lo_hlay.addWidget(
            self.setWidgetType('motorBtn', device, "MOTOR:"+pvList[1]))
        return lo_hlay

    def setSingleScrnInfo(self, device):
        ''' Build selected screen information '''
        group = QGroupBox()
        sm_glay = QGridLayout()
        pos = [0, 0]
        for label, channel in SCREENS_INFO.get('content').items():
            sm_glay.addLayout(
                self.setBasicInfo(device, label, 'MOTOR:'+channel),
                pos[0], pos[1], 1, 2)
            pos[0]+=1

        sm_glay.addLayout(
            self.setZeroOpt(
                SCREENS_INFO.get('special_content')[1], device),
            pos[0], pos[1], 1, 3)

        pos[0] = 0

        sm_glay.addWidget(
            self.setScrnSelection(
                SCREENS_INFO.get('special_content')[0], device),
            pos[0], pos[1]+2, 5, 1)

        group.setTitle(SCREENS_INFO.get('title')+' '+device)
        group.setLayout(sm_glay)
        return group

    def setGraphInfo(self, device, graph_info):
        ''' Build the basic graph information '''
        gi_hlay = QHBoxLayout()
        for label, channel in graph_info.items():
            gi_hlay.addLayout(
                self.setBasicInfo(device, label, channel))
        return gi_hlay

    def setRoiInfo(self, device, roi_data, title):
        ''' Build the ROI information '''
        group = QGroupBox()
        ri_vlay = QVBoxLayout()
        for label, channel in roi_data.items():
            ri_vlay.addLayout(
                self.setRBVObj(device, channel, label, 'ROI:'))

        group.setLayout(ri_vlay)
        group.setTitle(title)
        return group

    def setGraphs(self, device):
        ''' Build the graph group '''
        group = QGroupBox()
        ag_vlay = QVBoxLayout()
        for title, graph_data in GRAPH.items():
            if title == "ROI":
                ag_vlay.addWidget(self.setRoiInfo(device, graph_data, title))
            else:
                ag_vlay.addWidget(self.setGraph(device, graph_data, title))
                ag_vlay.addLayout(self.setGraphInfo(device, graph_data['info']))

        group.setLayout(ag_vlay)
        group.setTitle("Projections "+device)
        return group

    def getStackItem(self, stackType, device):
        ''' Get one stack item '''
        if stackType == 0:
            return self.setSingleScrnInfo(device)
        elif stackType == 1:
            return self.setGraphs(device)
        elif stackType == 2:
            return self.setSingleScrn(device)

    def saveStack(self, stack, stackType):
        ''' Save the stack for future item changes '''
        if stackType == 0:
            self.stackScreens = stack
        elif stackType == 1:
            self.stackGraphs = stack
        elif stackType == 2:
            self.stackScreen = stack

    def buildStacks(self, stackType):
        ''' Build all the stack groups '''
        stack = QStackedWidget()
        for device in DEVICES:
            stack.addWidget(
                self.getStackItem(stackType, device))
        self.saveStack(stack, stackType)
        return stack

    def setScrnInfo(self, device):
        ''' Build the screen information Component'''
        si_glay = QGridLayout()
        counter = [0, 0]
        for title, item in SCREEN['info'].items():
            if title in ['Gain', 'Exposure']:
                si_glay.addLayout(
                    self.setRBVObj(device, item, title, 'CAM:'),
                    counter[0], counter[1])
            elif title == 'LED':
                si_glay.addLayout(
                    self.setLight(device, item, title),
                    counter[0], counter[1])
            elif item == "RESET.PROC":
                si_glay.addWidget(
                    self.setWidgetType('pushBtn', device, 'CAM:' + item, title),
                    counter[0], counter[1])
            else:
                si_glay.addLayout(
                    self.setBasicInfo(device, title, item),
                    counter[0], counter[1])

            si_glay.setColumnStretch(counter[1], 10)
            counter[0] += 1
            if counter[0] >= 2:
                counter[1] += 1
                counter[0] = 0

        return si_glay

    def header(self):
        ''' Build the header'''
        hd_hlay = QHBoxLayout()
        title = QLabel("<h2>Linac Screen View</h2>")
        hd_hlay.addWidget(title, alignment=Qt.AlignCenter)
        return hd_hlay

    def imageViewer(self):
        ''' Build the image'''
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height()))
        self.image_container.setMinimumSize(700, 250)
        self.image_container.setMaximumSize(1500, 250)
        self.image_container.setAlignment(Qt.AlignCenter)
        return self.image_container

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 10)
        if_glay.addWidget(self.imageViewer(), 1, 1, 3, 9)
        if_glay.addWidget(self.setScrnPanel(), 1, 0, 3, 1)
        if_glay.addWidget(self.buildStacks(2), 4, 2, 6, 8)
        if_glay.addWidget(self.buildStacks(0), 4, 0, 3, 2)
        if_glay.addWidget(self.buildStacks(1), 7, 0, 3, 2)
        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
