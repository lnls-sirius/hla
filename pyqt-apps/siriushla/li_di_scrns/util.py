DEVICES = [
    "PRF1",
    "PRF2",
    "PRF3",
    "PRF4",
    "PRF5"
]

WID_DICT = {
    0: 'label',
    1: 'led',
    2: 'pushBtn',
    3: 'spinBox',
    4: 'lineEdit',
    5: 'motorBtn'
}

SCREENS_PANEL = {
    "title": "Screens Panel",
    "labels": [
        "Devices", "Selected", "Busy"
    ],
    "content": [
        "POS_R", "BUSY"
    ]
}

SCREENS_INFO = {
    "title": "Screen Information",
    "content": {
        "Limit Top": "IS_B",
        "Limit Bottom": "IS_A",
        "Limit Mode": "MODE",
        "Motor Status": "BUSY",
        "Motor Code": "AL"
    },
    "special_content": [
        {
            "selected": "POS_R",
            "labels": [
                "OUT", "CAL", "AL203",
                "YAG", "OTR"
            ],
            "content": [
                "POS1.PROC", "POS2.PROC", "POS3.PROC",
                "POS4.PROC", "POS5.PROC"
            ]
        },
        {
            "title": "Zero Operation",
            "content": {
                "Zero": "UP-O.PROC",
                "Zero (!Expert)": "UP-M.PROC"
            }
        }
    ]
}

HEADER = {
    "All Motor Out": "OUT",
    "All Motor Zero": "UP"
}

GRAPH = {
    "Horizontal": {
        "labelX": "Points",
        "labelY": "Projection",
        "channel": {
            "centroid": "CAL:ProfileCentroidX_RBV",
            "data": "X:Gauss:Data"
        },
        "info": {
            "Center": "X:Gauss:Peak",
            "Sigma": "X:Gauss:Sigma",
            "Coefficient": "X:Gauss:Coef"
        }
    },
    "Vertical": {
        "labelX": "Points",
        "labelY": "Projection",
        "channel": {
            "centroid": "CAL:ProfileCentroidY_RBV",
            "data": "Y:Gauss:Data"
        },
        "info": {
            "Center": "Y:Gauss:Peak",
            "Sigma": "Y:Gauss:Sigma",
            "Coefficient": "Y:Gauss:Coef"
        }
    },
    "ROI": {
        "Resolution": [
            "MaxSizeX_RBV", "MaxSizeY_RBV"],
        "Size": [
            "SizeX_RBV", "SizeY_RBV"],
        "X Start": [
            "MinX_RBV", "MinX_"],
        "Y Start": [
            "MinY_RBV", "MinY_"]
    }
}

SCREEN_CONFIG = {
    "LED": [
        "LED",
        "CMD"
    ],
    "Connection": "CONNECTION.SEVR",
    "Acquire": "Acquire",
    "CCD Reconnect": "RESET.PROC"
}

SCREEN = {
    "Screen": {
        "data": "RAW:ArrayData",
        "width": "RAW:ArraySize0_RBV"
    },
    "info": {
        "Counter": "CAM:ArrayCounter_RBV",
        "Exposure": [
            "AcquireTime_RBV",
            "AcquireTime"
        ],
        "Gain": [
            "Gain_RBV",
            "Gain"
        ],
        "Centroid Threshold": "CAL:CentroidThreshold"
    }
}
