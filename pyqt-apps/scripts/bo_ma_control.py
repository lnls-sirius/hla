import sys
from pydm import PyDMApplication
from siriusdm.as_ma_control import BoosterMagnetControlWindow


app = PyDMApplication(None, sys.argv)
window = BoosterMagnetControlWindow()
window.show()
sys.exit(app.exec_())
