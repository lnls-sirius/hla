''' Diagnostic Interface of the LINAC's BPM'''
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QVBoxLayout, QTabWidget, \
    QWidget, QLabel, QGridLayout
import qtawesome as qta
from pydm.widgets import enum_button, PyDMEnumComboBox

from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusLedState, SiriusLabel, \
    SiriusSpinbox
from ..as_di_bpms.base import GraphWave


class DigBeamPosProc(SiriusMainWindow):
    ''' Class Digital Beam Position Processor '''

    def __init__(self, device_name, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.device_name = device_name
        self.prefix = prefix + ('-' if prefix else '')

        color = get_appropriate_color('LI')
        self.setWindowIcon(qta.icon('mdi.currency-sign', color=color))
        self.setObjectName('LIApp')

        self.setWindowTitle(self.device_name)

        self.header = {
            "Trigger": "TRIGGER_STATUS",
            "IOC": "HEART_BEAT"
        }

        self.graph_all_data = {
            "ADC Raw Waveform": {
                "title": "ADC",
                "labelX": "Waveform Index",
                "unitX": "",
                "labelY": "ADC Value",
                "unitY": "count",
                "channels": {
                    "CH1": {
                        "path": "CH1_ADX_WAVEFORM",
                        "name": "AntA",
                        "color": "#0000FF"
                    },
                    "CH2": {
                        "path": "CH2_ADX_WAVEFORM",
                        "name": "AntB",
                        "color": "#FF0000"
                    },
                    "CH3": {
                        "path": "CH3_ADX_WAVEFORM",
                        "name": "AntC",
                        "color": "#008800"
                    },
                    "CH4": {
                        "path": "CH4_ADX_WAVEFORM",
                        "name": "AntD",
                        "color": "#FF00FF"
                    }
                }
            },
            "Hilbert": {
                "Amplitude": {
                    "title": "Amplitude",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Amplitude Value",
                    "unitY": "count",
                    "channels": {
                        "CH1": {
                            "path": "CH1_HIB_AMP_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2": {
                            "path": "CH2_HIB_AMP_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3": {
                            "path": "CH3_HIB_AMP_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4": {
                            "path": "CH4_HIB_AMP_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                },
                "Phase": {
                    "title": "Phase",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Phase Value",
                    "unitY": "count",
                    "channels": {
                        "CH1": {
                            "path": "CH1_HIB_PH_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2": {
                            "path": "CH2_HIB_PH_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3": {
                            "path": "CH3_HIB_PH_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4": {
                            "path": "CH4_HIB_PH_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                }
            },
            "FFT": {
                "Amplitude": {
                    "title": "Amplitude",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Amplitude Value",
                    "unitY": "count",
                    "channels": {
                        "CH1": {
                            "path": "CH1_FFT_AMP_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2": {
                            "path": "CH2_FFT_AMP_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3": {
                            "path": "CH3_FFT_AMP_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4": {
                            "path": "CH4_FFT_AMP_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                },
                "Phase": {
                    "title": "Phase",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Phase Value",
                    "unitY": "count",
                    "channels": {
                        "CH1": {
                            "path": "CH1_FFT_PH_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2": {
                            "path": "CH2_FFT_PH_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3": {
                            "path": "CH3_FFT_PH_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4": {
                            "path": "CH4_FFT_PH_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                }
            }
        }

        self.bpm_main_data = {
            "Max ADC": {
                "A": "CH1_MAXADC",
                "B": "CH2_MAXADC",
                "C": "CH3_MAXADC",
                "D": "CH4_MAXADC"
                },
            "Position": {
                "X": "POS_X",
                "Y": "POS_Y",
                "S": "POS_S"
                },
            "V": {
                "A": "POS_VA",
                "B": "POS_VB",
                "C": "POS_VC",
                "D": "POS_VD"
                },
            "Trigger Cnt": "TRIGGER_CNT",
            "Cycle": "ACQ_TIME_USED",
            "FFT": {
                "Center": "FFT_CENTER",
                "Width": "FFT_WIDTH"
                },
            "Hilbert": {
                "Center": "HIB_CENTER",
                "Width": "HIB_WIDTH"
                },
            "Gain": {
                "X": "POS_KX",
                "Y": "POS_KY",
                "S": "POS_KS"
                },
            "Offset": {
                "X": "POS_OX",
                "Y": "POS_OY"
                }
            }

        self.bpm_sec_data = {
            "Attenuator": "FE_ATTEN_SP",
            "ADC Threshold": "ADC_THD",
            "Orientation": "BPM_STRIP"
            }

        self.selectors_data = {
            "Trigger Mode": "ACQ_TRIGGER",
            "Position Algorithm": "POS_ALG"
            }

        self._setupUi()

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.display_header(), 0, 0, 1, 3)
        if_glay.addLayout(self.display_graph(), 1, 0, 2, 1)
        if_glay.addLayout(self.display_mainData(), 1, 1, 1, 1)
        if_glay.addLayout(self.display_selectors(), 1, 2, 1, 1)
        if_glay.setAlignment(Qt.AlignTop)
        if_glay.setColumnStretch(0, 10)

        wid.setLayout(if_glay)
        self.setCentralWidget(wid)

    def display_header(self):
        '''Display the header of the interface'''
        hd_glay = QGridLayout()

        title_lb = QLabel('<h2>' + self.device_name + ' - POSITION MONITOR </h2>', self)
        title_lb.setAlignment(Qt.AlignCenter)
        hd_glay.addWidget(title_lb, 0, 2, 2, 1)

        countx = 0

        for led_lb, led_channel in self.header.items():
            trig_led = SiriusLedState(
                init_channel=self.prefix + self.device_name + ':' + led_channel)
            trig_led.setFixedSize(30, 30)
            hd_glay.addWidget(trig_led, 0, countx, 1, 1)

            trig_lb = QLabel(led_lb)
            trig_lb.setAlignment(Qt.AlignCenter)
            hd_glay.addWidget(trig_lb, 1, countx, 1, 1)

            countx += 1

        hd_glay.setAlignment(Qt.AlignCenter)

        return hd_glay

    def createGraph(self, graph_data):
        '''Build a graph widget'''
        graph_plot = GraphWave()

        graph_plot.graph.title = graph_data.get("title")
        graph_plot.setLabel(
            'left',
            text=graph_data.get("labelY"),
            units=graph_data.get("unitY"))
        graph_plot.setLabel(
            'bottom',
            text=graph_data.get("labelX"),
            units=graph_data.get("unitX"))

        for channel in graph_data.get("channels"):

            channel_data = graph_data.get("channels").get(channel)
            graph_plot.addChannel(
                y_channel=self.prefix + self.device_name + ':' + channel_data.get('path'),
                name=channel_data.get('name'),
                color=channel_data.get('color'),
                lineWidth=1)

        graph_plot.setMinimumWidth(600)
        graph_plot.setMinimumHeight(250)

        return graph_plot

    def display_graph(self):
        '''Display the graph tabs and all their contents'''
        gp_vlay = QVBoxLayout()
        tab = QTabWidget()
        tab.setObjectName("LITab")

        for graph_name in self.graph_all_data:
            tablay = QVBoxLayout()
            tab_content = QWidget()

            graph_item = self.graph_all_data.get(graph_name)

            if len(graph_item.items()) != 2:
                tablay.addWidget(self.createGraph(graph_item), 10)
                tab_content.setLayout(tablay)
            else:
                for data in graph_item:
                    tablay.addWidget(
                        self.createGraph(graph_item.get(data)), 10)

                tab_content.setLayout(tablay)
            tab.addTab(tab_content, graph_name)

        gp_vlay.addWidget(tab)

        return gp_vlay

    def dataItem(self, channel, style):
        '''Get data channel info'''
        if style == 0:
            channel_info = SiriusLabel(
                parent=self,
                init_channel=self.prefix + self.device_name + ':' + channel)
        elif style in [1, 2, 4]:
            channel_info = SiriusSpinbox(
                parent=self,
                init_channel=self.prefix + self.device_name + ':' + channel)
            channel_info.showStepExponent = False
        else:
            channel_info = QLabel("Error", self)

        return channel_info

    def display_data(self, title, info, pos_x, pos_y, style):
        '''Build a data widget'''
        glay = QGridLayout()
        group = QGroupBox()

        countx = 0
        county = 0

        if style == 0:
            for text, channel in info.items():

                text_lb = QLabel(text, self)
                glay.addWidget(text_lb, countx, county)

                channel_lb = self.dataItem(channel, pos_y)
                channel_lb.showUnits = True
                glay.addWidget(channel_lb, countx, county+1)

                countx += 1
        else:
            channel_lb = self.dataItem(info, pos_y)
            channel_lb.showUnits = True
            glay.addWidget(channel_lb, pos_x, pos_y)

        glay.setAlignment(Qt.AlignCenter)

        group.setTitle(title)
        group.setLayout(glay)

        return group

    def display_mainData(self):
        '''Display all main data widgets'''
        countx = 0
        county = 0

        md_glay = QGridLayout()

        for title, info in self.bpm_main_data.items():

            if title in ["Trigger Cnt", "Cycle"]:
                md_glay.addWidget(
                    self.display_data(
                        title, info,
                        countx, county, 1),
                    countx, county,
                    1, 1)
                countx += 1
            else:
                md_glay.addWidget(
                    self.display_data(
                        title, info,
                        countx, county, 0),
                    countx, county,
                    2, 1)
                countx += 2

            if countx > 7:
                countx = 0
                county += 2

        md_glay.setAlignment(Qt.AlignCenter)

        return md_glay

    def display_secData(self):
        '''Build the secondary data widget'''

        group = QGroupBox()
        sc_glay = QGridLayout()

        countx = 0
        for text, channel in self.bpm_sec_data.items():

            if text != "Orientation":

                text_lb = QLabel(text, self)
                sc_glay.addWidget(text_lb, countx, 0, 1, 1)

                channel_lb = self.dataItem(channel, 1)
                channel_lb.showUnits = True
                sc_glay.addWidget(channel_lb, countx, 1, 1, 1)
            else:
                text_lb = QLabel(text, self)
                text_lb.setAlignment(Qt.AlignCenter)
                sc_glay.addWidget(text_lb, countx, 0, 1, 2)
                selection = PyDMEnumComboBox(
                    init_channel=self.prefix + self.device_name+":"+channel)
                sc_glay.addWidget(selection, countx+1, 0, 1, 2)
            countx += 1

        sc_glay.setAlignment(Qt.AlignTop)
        group.setLayout(sc_glay)

        return group

    def selectionItem(self, title, channel, orientation):
        '''Build a selection widget'''
        group = QGroupBox()
        lay = QVBoxLayout()

        selector = enum_button.PyDMEnumButton(
            init_channel=self.prefix + self.device_name+":"+channel)
        selector.widgetType = 0
        selector.orientation = orientation
        lay.addWidget(selector, 0)

        group.setLayout(lay)
        group.setTitle(title)

        return group

    def display_selectors(self):
        '''Display the selector and the secondary data'''
        sl_vlay = QVBoxLayout()
        for title, channel in self.selectors_data.items():
            sl_vlay.addWidget(
                self.selectionItem(title, channel, 2), 1)

        sl_vlay.addWidget(self.display_secData(), 0)

        return sl_vlay
