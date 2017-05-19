import sys
from pydm import PyDMApplication
from siriusdm.as_ps_cycle import PsCycleWindow


app = PyDMApplication(None, sys.argv)
window = PsCycleWindow()
window.show()
sys.exit(app.exec_())
