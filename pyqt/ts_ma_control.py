import sys
from pydm import PyDMApplication
from siriusdm.as_ma_control import ToSiriusMagnetControlWindow


app = PyDMApplication(None, sys.argv)
window = ToSiriusMagnetControlWindow()
window.show()
sys.exit(app.exec_())
