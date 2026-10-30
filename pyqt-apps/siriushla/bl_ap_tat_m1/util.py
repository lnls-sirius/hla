
class Mirror:
    def __init__(self, pv):
        self.set = pv
        self.rbv = f"{pv}.RBV"
        self.enbl = f"{pv}.CNEN"
        self.stop = f"{pv}.STOP"

UPWARD = 154.0

DOWNWARD = 0.0
