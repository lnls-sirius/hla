
class Mirror:
    def __init__(self, pv):
        self.set = pv
        self.rbv = f"{pv}.RBV"
        self.enbl = f"{pv}.CNEN"
        self.stop = f"{pv}.STOP"

DIRECTIONS = {
    "Up": {
        "Name": "Upward",
        "Value": 154.0,
        "Icon": "fa.arrow-circle-o-up",
        "Limits": {
            "Upward-1": "TAT:F:EPS01:MR1LS1"
        }
    },
    "Down": {
        "Name": "Downward",
        "Value": 0.0001,
        "Icon": "fa.arrow-circle-o-down",
        "Limits": {
            "Downward-1": "TAT:F:EPS01:MR1IND1",
            "Downward-2": "TAT:F:EPS01:MR1IND2"
        }
    }
}
