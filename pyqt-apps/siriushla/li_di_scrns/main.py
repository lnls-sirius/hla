''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QLabel, QGridLayout, QStackedWidget, \
    QSizePolicy, QPushButton
from pydm.widgets import PyDMPushButton, PyDMImageView, PyDMLineEdit, \
    enum_button
import qtawesome as qta
from .. import util as _util
from ..widgets import SiriusMainWindow, PyDMLedMultiChannel, \
    SiriusWaveformPlot, SiriusLabel, SiriusSpinbox, SiriusConnectionSignal
from .util import DEVICES, SCREENS_PANEL, SCREENS_INFO, HEADER, \
    GRAPH, SCREEN
from .motorBtn import MotorBtn


class GeneralFunctions():
    ''' Class with the functions used in both Screens Windows'''

    def getPvName(self, device, pv_name):
        ''' Build PV name '''
        return self.device_name + ':' + device + ":" + pv_name

    def setWidgetType(self, wid_type, device, pv_name, label='', value=0):
        ''' Get widget type '''
        pv_name = self.getPvName(device, pv_name)
        if wid_type == 'label':
            widget = SiriusLabel(self, init_channel=pv_name)
            widget.showUnits = True
            widget.setAlignment(Qt.AlignCenter)
        elif wid_type == 'led':
            ch2vals = {pv_name: value}
            widget = PyDMLedMultiChannel(self)
            widget.set_channels2values(ch2vals)
            if value == 1:
                widget.shape = widget.ShapeMap.Round
        elif wid_type == 'pushBtn':
            widget = PyDMPushButton(self, init_channel=pv_name,
                                    label=label, pressValue=value)
        elif wid_type == 'spinBox':
            widget = SiriusSpinbox(init_channel=pv_name)
            widget.showUnits = True
        elif wid_type == 'lineEdit':
            widget = PyDMLineEdit(
                init_channel=pv_name)
            widget.setAlignment(Qt.AlignCenter)
            widget.showUnits = True
        elif wid_type == 'motorBtn':
            widget = MotorBtn(
                init_channel=pv_name)
        else:
            widget = QLabel("Error: Unknown device")
        widget.setMinimumWidth(60)
        widget.setFixedHeight(20)
        return widget

    def setBasicInfo(self, device, label, pv_name):
        ''' Build one basic information Component '''
        bi_hlay = QHBoxLayout()
        bi_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignCenter)
        if label in ['Limit Mode', 'Motor Code', 'Counter', 'Sigma', 'Center']:
            wid_type = 'label'
        elif label == "Coefficient":
            wid_type = 'spinBox'
        elif label == "Centroid Threshold":
            wid_type = 'lineEdit'
        else:
            wid_type = 'led'
        bi_hlay.addWidget(
            self.setWidgetType(wid_type, device, pv_name))
        return bi_hlay

    def setRBVObj(self, device, channel, label, pv_prefix):
        ''' Build formatted RBV Component'''
        rbv_hlay = QHBoxLayout()
        title = QLabel(label)
        title.setMinimumWidth(75)
        title.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        rbv_hlay.addWidget(title)
        for item in range(1, -1, -1):
            pv_name = pv_prefix + channel[item]
            if 'RBV' not in pv_name:
                if label in ['Gain', 'Exposure']:
                    wid_type = 'lineEdit'
                else:
                    wid_type = 'spinBox'
            else:
                wid_type = 'label'
            widget = self.setWidgetType(wid_type, device, pv_name)
            widget.setMaximumWidth(75)
            if item != 0:
                rbv_hlay.addWidget(
                    widget,
                    alignment=Qt.AlignRight)
                if 'MaxSize' in channel[0]:
                    sep_label = QLabel("X")
                    sep_label.setFixedWidth(10)
                    rbv_hlay.addWidget(
                        sep_label,
                        Qt.AlignCenter)
            else:
                rbv_hlay.addWidget(
                    widget, alignment=Qt.AlignLeft)
        return rbv_hlay

    def setSingleScrn(self, device, screen):
        ''' Build a single screen Component '''
        group = QGroupBox()
        ss_vlay = QVBoxLayout()

        image_wid = PyDMImageView(
            image_channel=self.getPvName(device, screen['data']),
            width_channel=self.getPvName(device, screen['width']))

        image_wid.readingOrder = image_wid.ReadingOrder.Clike
        ss_vlay.addWidget(image_wid, 5)

        if 'IMG' not in screen['data']:
            ss_vlay.addLayout(self.setScrnInfo(device), 1)
        group.setTitle(screen['title'] + " " + device)
        group.setLayout(ss_vlay)
        return group


class LiBeamProfile(SiriusMainWindow, GeneralFunctions):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = _util.get_appropriate_color('LI')

        self.device_name = 'LA-BI'
        self.window_title = "Linac Screen View"

        self.setWindowIcon(qta.icon('mdi.camera-metering-center', color=color))
        self.setWindowTitle(self.window_title)
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), "linac.png"))
        self.selected_device = ''
        self.stack_screens = QStackedWidget()
        self.stack_screen = QStackedWidget()
        self._setupUi()

    def radioBtnClick(self, value):
        ''' Action on radio button change '''
        self.selected_device = DEVICES[value]
        device_index = DEVICES.index(self.selected_device)
        self.stack_screens.setCurrentIndex(device_index)
        self.stack_screen.setCurrentIndex(device_index)

    def selectionItem(self, channel):
        '''Build a selection widget'''
        selector = enum_button.PyDMEnumButton(
            init_channel=self.prefix + self.device_name+":"+channel)
        self.active_screen = SiriusConnectionSignal(
            self.prefix + self.device_name+":"+channel)
        self.active_screen.new_value_signal[int].connect(
            self.radioBtnClick)
        selector.widgetType = 1
        return selector

    def setScrnHeader(self, layout):
        ''' Build the screen panel header '''
        count = 0
        for text in SCREENS_PANEL.get('labels'):
            layout.addWidget(
                QLabel('<h4>' + text + '</h4>'),
                0, count,
                alignment=Qt.AlignCenter)
            count += 1
        return layout

    def setPanelInfo(self, device, layout, row):
        ''' Build the information of one screen in screen panel '''
        pv_list = SCREENS_PANEL.get('content')
        pv_name = 'MOTOR' + ":"
        count = 0

        count += 1
        for item in range(0, len(pv_list)):
            if item == 0:
                wid_type = 'label'
            else:
                wid_type = 'led'

            layout.addWidget(
                self.setWidgetType(
                    wid_type, device, pv_name + pv_list[item]),
                row, count,
                alignment=Qt.AlignCenter)
            count += 1
        layout.addWidget(
            self.setWidgetType('led', device, pv_name + pv_list[0], value=1),
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

        am_glay = self.setScrnHeader(am_glay)

        row = 1
        am_glay.addWidget(
            self.selectionItem('PRF:OPI'),
            row, 0, 5, 1,
            alignment=Qt.AlignCenter)
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

    def setScrnSelection(self, selection_info, device):
        ''' Build the screen position selection menu '''
        widget = QGroupBox()
        ms_vlay = QVBoxLayout()
        ms_vlay.addWidget(
            SiriusLabel(
                init_channel=self.getPvName(
                    device, 'MOTOR:' + selection_info.get('selected'))),
            alignment=Qt.AlignCenter)

        for pv_name, label in selection_info.get('content').items():
            label = self.getScrnSelBtns(device, label)
            if label:
                ms_vlay.addWidget(
                    PyDMPushButton(
                        init_channel=self.getPvName(
                            device, 'MOTOR:' + pv_name),
                        label=label, pressValue=0))
        widget.setLayout(ms_vlay)
        widget.setTitle("Position")
        return widget

    def setZeroOpt(self, item, device):
        ''' Build Zero Operation Component'''
        zo_hlay = QHBoxLayout()
        zo_hlay.addWidget(
            QLabel(item["title"]),
            alignment=Qt.AlignCenter)
        count = 0
        for label, pv_name in item["content"].items():
            widget = self.setWidgetType(
                'pushBtn', device, "MOTOR:" + pv_name, label)
            if count == 1:
                widget.setStyleSheet("background-color:#ffff00;")
            zo_hlay.addWidget(
                widget,
                alignment=Qt.AlignCenter)
            count += 1
        return zo_hlay

    def setLight(self, device, pv_list, title):
        ''' Build Light Component '''
        lo_hlay = QHBoxLayout()
        lo_hlay.addWidget(
            QLabel(title))
        lo_hlay.addWidget(
            self.setWidgetType('motorBtn', device, "MOTOR:" + pv_list[1]))
        lo_hlay.addWidget(
            self.setWidgetType('led', device, "MOTOR:" + pv_list[0]))
        return lo_hlay

    def setSingleScrnInfo(self, device):
        ''' Build selected screen information '''
        group = QGroupBox()
        sm_glay = QGridLayout()
        group.setTitle(SCREENS_INFO.get('title') + ' ' + device)
        group.setLayout(sm_glay)

        pos = [0, 0]
        for label, channel in SCREENS_INFO.get('content').items():
            sm_glay.addLayout(
                self.setBasicInfo(device, label, 'MOTOR:' + channel),
                pos[0], pos[1], 2, 2)
            pos[0] += 2

        sm_glay.addLayout(
            self.setZeroOpt(
                SCREENS_INFO.get('special_content')[1], device),
            pos[0], pos[1], 1, 3)

        btn = QPushButton("ROI View")
        _util.connect_window(
            btn, ROIViewWindow,
            parent=self)
        sm_glay.addWidget(btn, pos[0]+1, 0, 1, 3)

        pos[0] = 0

        sm_glay.addWidget(
            self.setScrnSelection(
                SCREENS_INFO.get('special_content')[0], device),
            pos[0], pos[1] + 2, 10, 1)

        return group

    def getStackItem(self, stack_type, device):
        ''' Get one stack item '''
        if stack_type == 0:
            return self.setSingleScrnInfo(device)
        elif stack_type == 1:
            return self.setSingleScrn(device, SCREEN['Screen_Camera'])

    def saveStack(self, stack, stack_type):
        ''' Save the stack for future item changes '''
        if stack_type == 0:
            stack.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            self.stack_screens = stack
        elif stack_type == 1:
            self.stack_screen = stack

    def buildStacks(self, stack_type):
        ''' Build all the stack groups '''
        stack = QStackedWidget()
        for device in DEVICES:
            stack.addWidget(
                self.getStackItem(stack_type, device))
        self.saveStack(stack, stack_type)
        return stack

    def setScrnInfo(self, device):
        ''' Build the screen information Component'''
        si_glay = QGridLayout()
        counter = [0, 0]
        for title, item in SCREEN['info'].items():
            if title in ['Gain', 'Exposure']:
                si_glay.addLayout(
                    self.setRBVObj(device, item, title, 'CAM:'),
                    counter[0], counter[1],
                    alignment=Qt.AlignHCenter)
            elif title == 'LED':
                si_glay.addLayout(
                    self.setLight(device, item, title),
                    counter[0], counter[1],
                    alignment=Qt.AlignHCenter)
            elif item == "RESET.PROC":
                si_glay.addWidget(
                    self.setWidgetType(
                        'pushBtn', device, 'CAM:' + item, title),
                    counter[0], counter[1],
                    alignment=Qt.AlignHCenter)
            else:
                si_glay.addLayout(
                    self.setBasicInfo(device, title, item),
                    counter[0], counter[1],
                    alignment=Qt.AlignHCenter)

            counter[0] += 1
            if counter[0] >= 2:
                si_glay.setColumnStretch(counter[1], 30)
                counter[1] += 1
                counter[0] = 0

        return si_glay

    def header(self):
        ''' Build the header'''
        hd_hlay = QHBoxLayout()
        title = QLabel("<h2>" + self.window_title + "</h2>")
        hd_hlay.addWidget(title, alignment=Qt.AlignCenter)
        return hd_hlay

    def imageViewer(self):
        ''' Build the image'''
        self.image_container.setPixmap(self.pixmap)
        self.image_container.setScaledContents(True)
        self.image_container.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored)
        return self.image_container

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 10)
        if_glay.addWidget(self.imageViewer(), 1, 1, 4, 10)
        if_glay.addWidget(self.setScrnPanel(), 1, 0, 7, 1)
        if_glay.addWidget(self.buildStacks(0), 8, 0, 7, 1)
        if_glay.addWidget(self.buildStacks(1), 5, 1, 10, 10)
        wid.setLayout(if_glay)
        self.setCentralWidget(wid)


class ROIViewWindow(SiriusMainWindow, GeneralFunctions):
    """Show the ROI View Window."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self.device_name = 'LA-BI'
        self.setObjectName('LIApp')
        self.setWindowTitle('ROI View')
        self.active_screen = SiriusConnectionSignal(
            prefix + self.device_name+":PRF:OPI")
        self.active_screen.new_value_signal[int].connect(
            self.radioBtnClick)
        self.selected_device = 0
        self.stack_graphs = QStackedWidget()
        self.stack_screen = QStackedWidget()
        self.connect_sign = dict()
        self.curves = dict()
        self.roi_screens = dict()
        self._setupUi()

    def setGraphInfo(self, device, graph_info):
        ''' Build the basic graph information '''
        wid = QWidget()
        gi_hlay = QHBoxLayout()
        wid.setLayout(gi_hlay)

        gi_hlay.addStretch()
        for label, channel in graph_info.items():
            gi_hlay.addLayout(
                self.setBasicInfo(device, label, channel))
            gi_hlay.addStretch()
        return wid

    def setRoiInfo(self, device, roi_data, title):
        ''' Build the ROI information '''
        group = QGroupBox()
        ri_glay = QGridLayout()
        counter = [0, 0]
        col_span = 2
        for label, channel in roi_data.items():
            ri_glay.addLayout(
                self.setRBVObj(device, channel, label, 'ROI:'),
                counter[0], counter[1], 1, col_span)
            if counter[0] == 2:
                counter[0] = 0
                counter[1] = 1
            counter[0] += 1
            col_span = 1

        group.setLayout(ri_glay)
        group.setTitle(title)
        return group

    def radioBtnClick(self, value):
        ''' Action on radio button change '''
        self.selected_device = DEVICES[value]
        device_index = DEVICES.index(self.selected_device)
        self.stack_graphs.setCurrentIndex(device_index)
        self.stack_screen.setCurrentIndex(device_index)

    def rotate_chart(self, x_array):
        ''' Rotate X and Y Axis in the Chart '''
        pvname = self.sender().address
        device = pvname.split(':')[1]
        curvename = 'data' if 'Gauss:Data' in pvname else 'centroid'
        curve = self.curves[device][curvename]
        size = len(x_array)
        curve.receiveXWaveform(x_array)
        curve.receiveYWaveform(_np.linspace(0, size, num=size))

    def setGraph(self, device, graph_data, orientation='V'):
        '''Build a graph widget'''

        self.connect_sign[device] = dict()
        self.curves[device] = dict()

        graph_plot = SiriusWaveformPlot(background="#ffffff")
        pvname = self.getPvName(device, graph_data['channel']['centroid']) \
            if orientation != 'V' else 'Fake'
        graph_plot.addChannel(
            y_channel=pvname,
            color="#ff8b98",
            lineWidth=1,
            symbol='o',
            symbolSize=5)

        pvname = self.getPvName(device, graph_data['channel']['data']) \
            if orientation != 'V' else 'Fake'
        graph_plot.addChannel(
            y_channel=pvname,
            color="#ff0000",
            lineWidth=1,
            symbol='o',
            symbolSize=5)

        if orientation == 'V':
            self.curves[device]['centroid'] = graph_plot.curveAtIndex(0)
            self.connect_sign[device]['centroid'] = SiriusConnectionSignal(
                self.getPvName(
                    device, graph_data['channel']['centroid']))
            self.connect_sign[device]['centroid'].new_value_signal[_np.ndarray].connect(
                self.rotate_chart)

            self.curves[device]['data'] = graph_plot.curveAtIndex(1)
            self.connect_sign[device]['data'] = SiriusConnectionSignal(
                self.getPvName(
                    device, graph_data['channel']['data']))
            self.connect_sign[device]['data'].new_value_signal[_np.ndarray].connect(
                self.rotate_chart)

            graph_plot.setMaximumWidth(400)
        else:
            graph_plot.setMaximumHeight(300)

        return graph_plot

    def scrnAndProj(self, device):
        ''' Display ROI Screen, the projection charts
            and the projection information '''

        group = QGroupBox()
        lay = QGridLayout()
        group.setLayout(lay)

        self.roi_screens[device] = self.setSingleScrn(
            device, SCREEN['Screen_ROI'])
        lay.addWidget(
            self.roi_screens[device], 0, 0, 3, 3)

        lay.addWidget(
            self.setGraph(device, GRAPH["Horizontal"], 'H'),
            3, 0, 1, 3)

        lay.addWidget(
            self.setGraph(device, GRAPH["Vertical"], 'V'),
            0, 3, 1, 1)

        info_group = QGroupBox()
        lay_info = QVBoxLayout()
        info_group.setLayout(lay_info)
        info_group.setTitle("Projections Info")
        for title in ["Horizontal", "Vertical"]:
            lay_info.addWidget(
                QLabel(title), 1, alignment=Qt.AlignHCenter)
            lay_info.addWidget(
                self.setGraphInfo(device, GRAPH[title]['info']),
                1, alignment=Qt.AlignTop)
        lay.addWidget(info_group, 3, 3, 1, 1)

        return group

    def getStackItem(self, stack_type, device):
        ''' Get one stack item '''
        if stack_type == 0:
            return self.scrnAndProj(device)
        elif stack_type == 1:
            return self.setRoiInfo(device, GRAPH["ROI"], "ROI")

    def saveStack(self, stack, stack_type):
        ''' Save the stack for future item changes '''
        if stack_type == 0:
            self.stack_screen = stack
        elif stack_type == 1:
            self.stack_graphs = stack

    def buildStacks(self, stack_type):
        ''' Build all the stack groups '''
        stack = QStackedWidget()
        for device in DEVICES:
            stack.addWidget(
                self.getStackItem(stack_type, device))
        self.saveStack(stack, stack_type)
        return stack

    def _setupUi(self):
        """Build the UI."""
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout()
        wid.setLayout(lay)

        lay.addWidget(self.buildStacks(0))
        lay.addWidget(self.buildStacks(1))
