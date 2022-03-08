from re import S
import sys
import json
from PyQt5.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, QHBoxLayout, QVBoxLayout
from pydm import PyDMApplication
from pydm.widgets import PyDMLabel, PyDMLineEdit, enum_button
from siriushla.as_di_bpms.base import GraphWave

# Digital Beam Position Processor
class DigBeamPosProc(QWidget): 
    
    prefix = "LA-BI:BPM2"
        
    radio_buttons = []
    wave_graph = False

    graph_data = {
        "title": "Hilbert Amplitude",
        "labelX": "Waveform Index",
        "unitX": "",
        "labelY": "ADC Value",
        "unitY": "count"
    }

    radio_data = '''
        [
            {
                "text" : "Trigger Mode",
                "channel" : "ACQ_TRIGGER"
            },
            {
                "text" : "Position Algorithm",
                "channel" : "POS_ALG"
            },
            {
                "text" : "Orientation",
                "channel" : "BPM_STRIP"
            },
            {
                "text" : "Display",
                "channel" : "OPI:SEL"
            }
        ]
        '''

    channels_data = '''
        [
            {
                "path": "CH1_HIB_AMP_WAVEFORM",
                "name": "AntA",
                "color": "#0000FF"
            },
            {
                "path": "CH2_HIB_AMP_WAVEFORM",
                "name": "AntB",
                "color": "#FF0000"
            },
            {
                "path": "CH3_HIB_AMP_WAVEFORM",
                "name": "AntC",
                "color": "#008800"
            },
            {
                "path": "CH4_HIB_AMP_WAVEFORM",
                "name": "AntD",
                "color": "#FF00FF"
            }
        ]
    '''

    data_bpm = '''
        [
            {
                "text" : "Max ADC",
                "info" :
                {
                        "A" : "CH1_MAXADC", 
                        "B" : "CH2_MAXADC", 
                        "C" : "CH3_MAXADC", 
                        "D" : "CH4_MAXADC"
                }
            },
            {
                "text" : "V",
                "info" :
                {
                    "A" : "POS_VA", 
                    "B" : "POS_VB", 
                    "C" : "POS_VC", 
                    "D" : "POS_VD"
                }
            },
            {
                "text" : "Position",
                "info" : 
                {
                    "X" : "POS_X", 
                    "Y" : "POS_Y"
                }
            },
            {
                "text" : "Sum",
                "info" : "POS_S"
            },
            {
                "text" : "Trigger Cnt",
                "info" : "TRIGGER_CNT"
            },
            {
                "text" : "Cycle",
                "info" : "ACQ_TIME_USED"
            },
            {
                "text" : "FFT",
                "info" : 
                {
                    "Center" : "FFT_CENTER",
                    "Width" : "FFT_WIDTH"
                }
            },
            {
                "text" : "K",
                "info" : 
                {
                    "X" : "POS_KX",
                    "Y" : "POS_KY"
                }
            },
            {
                "text" : "Offset",
                "info" : 
                {  
                    "X" : "POS_OX",
                    "Y" : "POS_OY"
                }
            },
            {
                "text" : "Ks" ,
                "info" : "POS_KS"
            },
            {
                "text" : "Attenuator",
                "info" : "FE_ATTEN_SP"
            },
            {
                "text" : "ADC Threshold",
                "info" : "ADC_THD"
            },
            {
                "text" : "Hilbert",
                "info" : 
                {
                    "Center" : "HIB_CENTER",
                    "Width" : "HIB_WIDTH"
                }
            }
        ]
    '''


    def __init__(self, parent=None): 
        """Init."""

        super().__init__(parent)
        
        self.setWindowTitle(self.prefix)

        lay = QHBoxLayout()
        lay.addWidget(self.display_section1(), 0)
        lay.addLayout(self.display_section2(), 1)
        lay.addLayout(self.display_section3(), 2)
        self.setLayout(lay)

    def createGraph(self):

        if(self.wave_graph == False):
            self.wave_graph = GraphWave()

            self.wave_graph.setLabel('left', text = self.graph_data.get("labelY"), units = self.graph_data.get("unitY"))
            self.wave_graph.setLabel('bottom', text = self.graph_data.get("labelX"), units = self.graph_data.get("unitX"))
           
        channels_info = json.loads(self.channels_data)
        for channel in channels_info:
            self.wave_graph.addChannel(
                y_channel = self.prefix + ':' + channel['path'],
                name = channel['name'], 
                color = channel['color'], 
                lineWidth= 1)

        self.wave_graph.setMinimumWidth(600)

    def display_section1(self):

        hlay = QHBoxLayout()
        group = QGroupBox()

        contx = 0

        self.createGraph()
        hlay.addWidget(self.wave_graph, 1)
        hlay.setStretch(20, 1)

        contx += 1
        
        group.setTitle(self.graph_data.get("title"))
        group.setAlignment(Qt.AlignCenter)
        group.setLayout(hlay)
        return group

    def data(self, channel, type):
        if(type == 0):
            channelInfo = PyDMLabel(
                parent=self,
                init_channel= self.prefix + ':' + channel)
        elif(type == 2 or type == 4):
            channelInfo = PyDMLineEdit(
                parent=self,
                init_channel= self.prefix + ':' + channel)
        else:
            channelInfo = QLabel("Error", self) 
        
        return channelInfo

    def display(self, title, info, lay, x, y, type):
        
        layG = QGridLayout()
        group = QGroupBox()

        contx = 0
        conty = 0

        if(type == 0):
            for text, channel in info.items():
                
                text_label = QLabel(text, self)
                layG.addWidget(text_label, contx, conty)

                channel_label = self.data(channel, y)
                channel_label.showUnits = True
                layG.addWidget(channel_label, contx, conty+1)

                contx += 1
        else:
            channel_label = self.data(info, y)
            channel_label.showUnits = True
            layG.addWidget(channel_label, x, y)       
        
        layG.setAlignment(Qt.AlignCenter)
        
        group.setTitle(title)
        group.setLayout(layG)

        lay.addWidget(group, x, y)

    def display_section2(self):
        contx = 0
        conty = 0

        lay = QGridLayout()
        
        bpm_info = json.loads(self.data_bpm)
        
        for bpm in bpm_info:
            
            if (bpm["text"] == "Max ADC" 
                or bpm["text"] == "V"
                or bpm["text"] == "Position"
                or bpm["text"] == "FFT"
                or bpm["text"] == "Hilbert"
                or bpm["text"] == "K"
                or bpm["text"] == "Offset"):
                self.display(bpm["text"], bpm["info"], lay, contx, conty, 0)
                contx += 1; 
            else:
                self.display(bpm["text"], bpm["info"], lay, contx, conty, 1)
                contx += 1
            
            if(contx > 5): 
                contx = 0
                conty += 2
        
        lay.setAlignment(Qt.AlignCenter)

        return lay

    def display_section3(self):

        layV = QVBoxLayout()
        
        cont = 0

        selection_data = json.loads(self.radio_data)

        for selection in selection_data:
            selection0 = QLabel(selection["text"])
            layV.addWidget(selection0, cont)

            selection1 = enum_button.PyDMEnumButton(self, self.prefix + ":" + selection["channel"])
            selection1.setMinimumWidth(200)
            selection1.setBaseSize(200,150)
            layV.addWidget(selection1, cont)
            cont += 1

        return layV
