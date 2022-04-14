from qtpy.QtCore import QEvent
from ..widgets import SiriusPushButton

# class HoverBtn(SiriusPushButton):

    # def __init__(self, parent=None, functionHidden, functionOpen):
    #     super().__init__(parent, functionHidden = None, functionOpen=None)
    #     print("Cmp")
    #     self.installEventFilter(parent)
    #     self.clicked.connect
    #     # functionHidden

    # def eventFilter(self, ob, event):
    #     obj = self.pv_obj.get(ob)
    #     # if event.type() == QEvent.Enter:
    #     #     self.controlBox(obj.get("name"), obj.get("layout"))
    #     #     self.stop = True
    #     #     return True
    #     if event.type() == QEvent.Leave:
    #         if self.clicked:
    #             self.controlHiddenBox(obj.get("name"), obj.get("layout"), obj.get("config"))
    #             self.stop = False
    #     return False
