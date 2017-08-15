import sys
from pydm import PyDMApplication
from siriushla.as_ps_cycle import PsCycleWindow


app = PyDMApplication(None, sys.argv)
window = PsCycleWindow()
window.show()
sys.exit(app.exec_())
