from .colors import COLOR

LABELS_CBX2 = {
    "Cbx1": [0, 2],
    "CW1.052.USC": [1.5, 23],
    "761\nCbx1": [0, 51.5],
    "1552\nCbx1": [0, 70],
    "1228\nCbx1": [0, 87.5],
    "TU1.ML050": [22, 31],
    "TU2.ML050": [40.25, 31],
    "AT1.HP050": [37, 57],
    "HP1.010.UPC": [67, 17],
    "LS1.CM015": [80, 9],
    "1921\nMfb": [93, 85.5],
    "Manifoldbox": [87, 88],
    "1923\nMfb": [93, 90],
    "HP1.EQ200": {
        "position": [6.75, 50],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "HP1.EQ300": {
        "position": [30, 50],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "HP1.EQ400": {
        "position": [34.75, 50],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "HP1.EQ500": {
        "position": [60.75, 50],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "WP1.QM110": {
        "position": [14, 7.5],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "TU1.050.U.SC": {
        "position": [28, 22],
        "shape": "side_arrows",
        "color": COLOR.gold
    },
    "WP1.QM010": {
        "position": [45, 7.5],
        "shape": "line",
        "color": COLOR.dark_blue
    },
    "TU2.050.U.SC": {
        "position": [45.75, 22],
        "shape": "side_arrows",
        "color": COLOR.gold
    },
    "TU2.065.U.TC": {
        "position": [43, 43],
        "shape": "side_arrows",
        "color": COLOR.dark_red
    },
    "TU2.066.U.TC": {
        "position": [43, 45.5],
        "shape": "side_arrows",
        "color": COLOR.dark_red
    },
    "TU2.067.U.TDC": {
        "position": [43, 63.75],
        "shape": "side_arrows",
        "color": COLOR.dark_red
    },
    "HP1.500.U.PC": {
        "position": [66, 49],
        "shape": "side_arrows",
        "color": COLOR.blue
    },
    "LS1.010.U.LC": {
        "position": [73.5, 19.25],
        "shape": "side_arrows",
        "color": COLOR.gold
    },
    "LP1.510.U.PC": {
        "position": [84.75, 66.5],
        "shape": "side_arrows",
        "color": COLOR.blue
    },
    "LP1.511.U.PC": {
        "position": [84.75, 64],
        "shape": "side_arrows",
        "color": COLOR.blue
    }
}

prc_prefix = "-rPrcOut"
db_prefix = "dbAdsSta_strAdsA-"

PVS_CBX2 = {
    "TU1.QN020": {
        "position": [8, 21],
        "pvname": "m13CB1TU1QN020"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "CD1.QN110": {
        "position": [8, 85],
        "pvname": "m13CB1CD1QN110"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "TU1.035.T": {
        "position": [14.5, 21.75],
        "pvname": db_prefix+"m13CB1TU1035T",
        "color": COLOR.dark_red
    },
    "TU1.035.P": {
        "position": [14.5, 29.75],
        "pvname": db_prefix+"m13CB1TU1035P",
        "color": COLOR.blue
    },
    "TU1.QN050": {
        "position": [21.5, 7.5],
        "pvname": "m13CB1TU1QN050"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "TU1.050.T": {
        "position": [28.25, 15],
        "pvname": db_prefix+"m13CB1TU1050T",
        "color": COLOR.dark_red
    },
    "TU1.050.S": {
        "position": [28.5, 25.5],
        "pvname": (db_prefix+"m13CB1TU1050S",""),
        "color": COLOR.gold
    },
    "TU2.QN050": {
        "position": [39, 7.5],
        "pvname": "m13CB1TU2QN050"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "TU2.035.P": {
        "position": [35.5, 29.75],
        "pvname": db_prefix+"m13CB1TU2035P",
        "color": COLOR.blue
    },
    "TU2.050.T": {
        "position": [46, 15],
        "pvname": db_prefix+"m13CB1TU2050T",
        "color": COLOR.dark_red
    },
    "TU2.050.S": {
        "position": [46.25, 25.5],
        "pvname": (db_prefix+"m13CB1TU2050S", ""),
        "color": COLOR.gold
    },
    "TU2.065.T": {
        "position": [43, 48],
        "pvname": db_prefix+"m13CB1TU2065T",
        "color": COLOR.dark_red
    },
    "CD1.QN410": {
        "position": [44.5, 83.5],
        "pvname": "m13CB1CD1QN410"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "HP1.QN500": {
        "position": [59, 34],
        "pvname": "m13CB1HP1QN500"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "HP1.QN410": {
        "position": [55, 62.5],
        "pvname": "m13CB1HP1QN410"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "HP1.500.P": {
        "position": [66.5, 42],
        "pvname": db_prefix+"m13CB1HP1500P",
        "color": COLOR.blue
    },
    "LP1.510.T": {
        "position": [64, 69],
        "pvname": db_prefix+"m13CB1LP1510T",
        "color": COLOR.dark_red
    },
    "DW1.LS1.010.L": {
        "position": [73.75, 23],
        "pvname": (db_prefix+"m14DW1LS1010L", ""),
        "color": COLOR.gold
    },
    "DW1.LS1.010.J": {
        "position": [73.75, 40],
        "pvname": db_prefix+"m14DW1LS1010J",
        "color": COLOR.black
    },
    "LS1.EB010": {
        "position": [80, 40],
        "pvname": "m14DW1LS1EB010"+prc_prefix,
        "color": COLOR.black
    },
    "HP1.QN510": {
        "position": [78, 49],
        "pvname": "m13CB1HP1QN510"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "LP1.QN510": {
        "position": [77.75, 67],
        "pvname": "m13CB1LP1QN510"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "LP1.510.P": {
        "position": [85, 69],
        "pvname": db_prefix+"m13CB1LP1510P",
        "color": COLOR.blue
    },
    "PR1.QN510": {
        "position": [73, 83.5],
        "pvname": "m13CB1PR1QN510"+prc_prefix,
        "color": COLOR.dark_blue
    },
    "PR1.510.T": {
        "position": [74.75, 87.5],
        "pvname": db_prefix+"m13CB1PR1510T",
        "color": COLOR.dark_red
    }
}

LEDS_CBX2 = {
    "TU1.QN020": {
        "position": [4.75, 25],
        "pvname": "TU1QN020LOWER"
    }
}