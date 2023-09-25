from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX


class CryoMain(SiriusMainWindow):

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        super().__init__(parent=parent)
