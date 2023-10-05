class COLOR:
    black = "#000000"
    dark_red = "#6b1c40"
    dark_blue = "#325692"
    blue = "#0000ff"
    gold = "#808000"


LABELS = {
    "CP1.CW1.GQ050": [11, 11],
    "Master Mode": [10.5, 20],
    "CP2.CW1.GQ050": [11, 54],
    "OC1.HP1.HQ010": [28.5, 1],
    "OC1.HP1.HQ020": [35.5, 1],
    "OC1.HP1.010.L": [31.75, 12],
    "OC1.HP1.020.L": [38.75, 12],
    "TUI.QN020": [31.5, 29.5],
    "OC2.HP1.HQ010": [28.5, 43],
    "OC2.HP1.HQ020": [35.5, 43],
    "OC2.HP1.010.L": [31.75, 54],
    "OC2.HP1.020.L": [38.75, 54],
    "OC1.HP1.HP050": [45.25, 1],
    "LS1.010.U.LC": (
        [62.5, 7], [62.5, 49]),
    "OC2.HP1.HP050": [45.25, 43],
    "Detector": [51, 75],
    "Coldbox": (
        [91.75, 10], [91.75, 92]),
    "BS1.CM030": [91.75, 39],
    "BS2.CM030": [91.75, 57],
    "BS3.CM030": [91.75, 75],
    "CI1.LP1.016.U.PC": {
        "position": [4.5, 36],
        "shape": "round",
        "color": COLOR.blue
    },
    "CI1.LP1.015.U.PC": {
        "position": [4.5, 38.75],
        "shape": "round",
        "color": COLOR.blue
    },
    "CI2.LP1.016.U.PC": {
        "position": [16, 75],
        "shape": "round",
        "color": COLOR.blue
    },
    "CI2.LP1.015.U.PC": {
        "position": [16, 78],
        "shape": "round",
        "color": COLOR.blue
    },
    "OC1.HP1.QM010": {
        "position": [31.75, 21.85],
        "shape": "line",
        "color": COLOR.dark_red
    },
    "OC1.HP1.QM020": {
        "position": [39.25, 21.85],
        "shape": "line",
        "color": COLOR.dark_red
    },
    "CW1.050.U.SC": {
        "position": [25.25, 25.8],
        "shape": "round",
        "color": COLOR.gold
    },
    "CW1.052.U.SC": {
        "position": [25.25, 31.25],
        "shape": "round",
        "color": COLOR.gold
    },
    "OC2.HP1.QM010": {
        "position": [31.75, 63.85],
        "shape": "line",
        "color": COLOR.dark_red
    },
    "OC2.HP1.QM020": {
        "position": [39.25, 63.85],
        "shape": "line",
        "color": COLOR.dark_red
    },
    "GP1.HP1.010.U.PC": {
        "position": [58.25, 9],
        "shape": "round",
        "color": COLOR.blue
    },
    "GP2.HP1.010.U.PC": {
        "position": [58.25, 51],
        "shape": "round",
        "color": COLOR.blue
    },
    "MC1.HP1.QM010": {
        "position": [43.25, 59],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "MC1.HP2.QM010": {
        "position": [56.25, 59],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "MC1.QM040": {
        "position": [52.5, 69],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "MC1.LP1.QM010": {
        "position": [43.25, 84],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "MC1.LP2.QM010": {
        "position": [56.25, 84],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "GP1.HP1.051.U.GC": {
        "position": [71, 26.5],
        "shape": "round",
        "color": COLOR.black
    },
    "GP2.HP1.051.U.GC": {
        "position": [71, 68.5],
        "shape": "round",
        "color": COLOR.black
    }
}

PVS = {
    "CP1.CW1.035.T": {
        "position": [4.75, 11],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_red
    },
    "CP1.CW1.065.P": {
        "position": [18, 6.25],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.blue
    },
    "CP1.CW1.065.T": {
        "position": [18, 11],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_red
    },
    "CP1.CW1.GQ050": {
        "position": [16.5, 18],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.black
    },
    "CP1.CW1.050.S": {
        "position": [16.5, 23],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "CP1.LP1.015.P": {
        "position": [4.75, 29],
        "pvname": (
            "RAD:Thermo1:Gamma", "RAD:Thermo1:Gamma"),
        "color": COLOR.blue
    },
    "CP2.CW1.035.T": {
        "position": [4.75, 54],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_red
    },
    "CP2.CW1.065.P": {
        "position": [18, 49.25],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.blue
    },
    "CP2.CW1.065.T": {
        "position": [18, 54],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_red
    },
    "CP2.CW1.GQ050": {
        "position": [16.5, 61],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.black
    },
    "CP2.CW1.050.S": {
        "position": [16.5, 66],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "CP2.LP1.015.P": {
        "position": [16.25, 81],
        "pvname": (
            "RAD:Thermo1:Gamma", "RAD:Thermo1:Gamma"),
        "color": COLOR.blue
    },
    "GP1.HP1.010.P": {
        "position": [51.8, 5],
        "pvname": (
            "RAD:Thermo1:Gamma", "RAD:Thermo1:Gamma"),
        "color": COLOR.blue
    },
    "GP2.HP1.010.P": {
        "position": [51.8, 47],
        "pvname": (
            "RAD:Thermo1:Gamma", "RAD:Thermo1:Gamma"),
        "color": COLOR.blue
    },
    "MC1.051.A": {
        "position": [37, 73],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "MC1.052.A": {
        "position": [44, 73],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "MC1.053.A": {
        "position": [37, 78],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "MC1.054.A": {
        "position": [44, 78],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.gold
    },
    "GP1.HP1.QN030": {
        "position": [71.25, 18],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP1.HP1.QN050": {
        "position": [71.25, 31.75],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP1.HP1.QN070": {
        "position": [71.25, 38],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP1.HP1.040.P": {
        "position": [79, 22],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.blue
    },
    "GP2.HP1.QN030": {
        "position": [71.25, 60],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP2.HP1.QN050": {
        "position": [71.25, 73.75],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP2.HP1.QN070": {
        "position": [71.25, 80],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.dark_blue
    },
    "GP2.HP1.040.P": {
        "position": [79, 57.5],
        "pvname": "RAD:Thermo1:Gamma",
        "color": COLOR.blue
    }
}
