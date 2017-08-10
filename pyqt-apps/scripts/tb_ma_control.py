import sys
from pydm import PyDMApplication
from siriushla.as_ma_control import ToBoosterMagnetControlWindow


app = PyDMApplication(None, sys.argv)
window = ToBoosterMagnetControlWindow()
window.show()
sys.exit(app.exec_())
