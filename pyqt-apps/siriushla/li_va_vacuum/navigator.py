from .chart import ChartWindow
from .details import DetailWindow, IpsDetailWindow, VgcDetailWindow

def selWindow(self, cat, id=0):
    if cat == "CCG Graphs":
        self.window = ChartWindow()
    elif cat == "Pump":
        self.window = IpsDetailWindow(id_ips=id)
    elif cat == "Vacuum":
        self.window = VgcDetailWindow(id_vgc=id)
    else:
        self.window = DetailWindow()
    self.window.show()
