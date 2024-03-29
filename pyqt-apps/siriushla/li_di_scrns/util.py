DEVICES = [
    "PRF1",
    "PRF2",
    "PRF3",
    "PRF4",
    "PRF5"
]

SCREENS_PANEL = {
    "title": "Screens Panel",
    "labels": [
        "Devices", "Selected", "Busy", "Beam Path"
    ],
    "content": [
        "POS_R", "BUSY"
    ]
}

SCREENS_INFO = {
    "title": "Screen Motor",
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
            "content": {
                "POS5.PROC": {
                    "GEN": '',
                    "PRF5": "YAG"
                },
                "POS4.PROC": {
                    "GEN": "YAG",
                    "PRF5": "OTR"
                },
                "POS3.PROC": {
                    "GEN": "AL203",
                    "PRF4": "OTR"
                },
                "POS2.PROC": "CAL",
                "POS1.PROC": "OUT"
            }
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
        "CCD Resolution": [
            "MaxSizeY_RBV", "MaxSizeX_RBV"],
        "X Size": [
            "SizeX_RBV", "SizeX"],
        "X Start": [
            "MinX_RBV", "MinX_"],
        "Y Size": [
            "SizeY_RBV", "SizeY"],
        "Y Start": [
            "MinY_RBV", "MinY_"]
    }
}

SCREEN = {
    "Screen_ROI": {
        "title": "ROI View",
        "data": "IMG:ArrayData",
        "width": "IMG:ArraySize0_RBV"
    },
    "Screen_Camera": {
        "title": "Screen Camera",
        "data": "RAW:ArrayData",
        "width": "RAW:ArraySize0_RBV"
    },
    "info": {
        "Connection": "CAM:CONNECTION.SEVR",
        "Acquire": "CAM:Acquire",
        "LED": [
            "LED",
            "CMD"
        ],
        "Centroid Threshold": "CAL:CentroidThreshold",
        "Exposure": [
            "AcquireTime_RBV",
            "AcquireTime"
        ],
        "Gain": [
            "Gain_RBV",
            "Gain"
        ],
        "Counter": "CAM:ArrayCounter_RBV",
        "CCD Reconnect": "RESET.PROC"
    }
}
