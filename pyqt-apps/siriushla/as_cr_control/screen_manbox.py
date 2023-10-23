from .colors import COLOR

LABELS_MANBOX = {
    "LN2": [-0.75, 17.75],
    "Atm": (
        [13, 17.75], [92, 1]),
    "NS1.CM050": [10, 65],
    "1906\nCbx entry": [35, 13],
    "1923\nCGR": [55, 19],
    "1921\nDewar": [57.9, 19],
    "PR1.CM050": [41, 65],
    "LN2 Supply 1": {
        "position": [48, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "gHe Return 1": {
        "position": [53.5, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "LHe Supply 1": {
        "position": [58, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "LN2 Supply 2": {
        "position": [67.5, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "gHe Return 2": {
        "position": [73.5, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "LHe Supply 2": {
        "position": [78, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "LN2 Supply 3": {
        "position": [84, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "gHe Return 3": {
        "position": [90, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "LHe Supply 3": {
        "position": [94.5, 75],
        "shape": "line",
        "color": COLOR.transparent,
        "rotation": 90
    },
    "NS1.050.U.LC": {
        "position": [21, 47.5],
        "shape": "side_arrows",
        "color": COLOR.gold
    },
    "PR1.050.U.LC": {
        "position": [37, 39],
        "shape": "side_arrows",
        "color": COLOR.gold
    },
    "VU1.GQ015": {
        "position": [88.5, 9],
        "shape": "line",
        "color": COLOR.black
    },
    "VU1.QM010": {
        "position": [88.5, 14.5],
        "shape": "line",
        "color": COLOR.black
    }
}

PVS_MANBOX = {
    "NS1.QN020": {
        "position": [5.5, 47.5],
        "pvname": "",
        "color": COLOR.wine
    },
    "NS1.050.L": {
        "position": [21.25, 52.5],
        "pvname": "",
        "color": COLOR.gold
    },
    "NS1.050.T": {
        "position": [21.25, 60],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "LP1.EG050": {
        "position": [43, 18],
        "pvname": "",
        "color": COLOR.transparent,
        "editable": True
    },
    "PR1.QN080": {
        "position": [51.5, 27.5],
        "pvname": "",
        "color": COLOR.blue
    },
    "PR1.050.P": {
        "position": [40, 34],
        "pvname": "",
        "color": COLOR.blue
    },
    "PR1.065.T": {
        "position": [49.5, 34],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "PR1.050.L2": {
        "position": [37.5, 52.2],
        "pvname": "",
        "color": COLOR.blue
    },
    "PR1.050.L": {
        "position": [37.5, 50],
        "pvname": "",
        "color": COLOR.gold
    },
    "PR1.050.J": {
        "position": [37.5, 67.5],
        "pvname": "",
        "color": COLOR.black
    },
    "PR1.EB050": {
        "position": [45, 67.5],
        "pvname": "",
        "color": COLOR.black
    },
    "PS1.QN020": {
        "position": [62.5, 27.5],
        "pvname": "",
        "color": COLOR.blue
    },
    "PS1.020.T": {
        "position": [63, 34],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "PR1.020.T": {
        "position": [54.25, 80],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "PR2.020.T": {
        "position": [74.25, 80],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "PR3.020.T": {
        "position": [90.75, 80],
        "pvname": "",
        "color": COLOR.dark_red
    },
    "VU1.020.P": {
        "position": [89, 19],
        "pvname": "",
        "color": COLOR.blue
    }
}
