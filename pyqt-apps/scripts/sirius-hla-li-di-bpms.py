import sys
from siriushla.li_di_bpms import DigBeamPosProc
from siriushla.sirius_application import SiriusApplication

app = SiriusApplication()
wid = DigBeamPosProc()
wid.setStyleSheet('''
                    *{
                        font-size: 12px;
                        background-color: #f3d2d5;
                    }
                    PyDMLineEdit{
                        border: 1px solid #000000;
                        background-color: #FFFFFF;
                        width: 40px;
                        padding-left: 5px;
                        padding-right: 5px;
                        border-radius: 5px;
                    }
                    QGroupBox{
                        border: 2px solid #b0b0b0;
                        padding-left: 5px;
                        padding-right: 5px;
                        padding-top: 5px;
                        margin: 3px;
                        font-weight: bold;
                    }
                    QGroupBox::title{
                        font-size: 15;
                        position: relative;
                        bottom: 5px;
                    }
                    QLabel{
                        padding-right: 5px;
                    }
                    GraphWave{
                        background-color:#000000
                    }
                    ''')
wid.show()
sys.exit(app.exec_())