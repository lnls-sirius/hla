BASIC_INFO = {
    "BUN1": {
        "CH1": {
            "Chart": ["Pick-Up"],
            "Position": [57.5, 77.25, 12.25, 13.5]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [14.5, 76.25, 12.25, 13.5]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [3, 64.5, 12.25, 13.5]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [3, 76.25, 12.25, 13.5]
        }
    },
    "KLY1": {
        "CH1": {
            "Chart": ["Forward", "Reflected"],
            "Position": [30, 43.75, 12.25, 16]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [14.5, 44.75, 12.25, 13.5]
        },
        "CH3": {
            "Chart": ["Forward"],
            "Position": [65, 63.5, 12.25, 13.5]
        },
        "CH4": {
            "Chart": ["Forward"],
            "Position": [65, 48.5, 12.25, 13.5]
        },
        "CH5": {
            "Chart": ["Forward"],
            "Position": [65, 33.5, 12.25, 13.5]
        },
        "CH6": {
            "Chart": ["Forward"],
            "Position": [85, 63.5, 12.25, 13.5]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [3, 33, 12.25, 13.5]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [3, 44.75, 12.25, 13.5]
        }
    },
    "KLY2": {
        "CH1": {
            "Chart": ["Forward", "Reflected"],
            "Position": [30, 12.25, 12.25, 16]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [14.5, 13.25, 12.25, 13.5]
        },
        "CH3": {
            "Chart": ["Forward"],
            "Position": [65, 15.5, 12.25, 13.5]
        },
        "CH4": {
            "Chart": ["Forward"],
            "Position": [65, 0, 12.25, 13.5]
        },
        "CH5": {
            "Chart": ["Forward"],
            "Position": [85, 15.5, 12.25, 13.5]
        },
        "CH6": {
            "Chart": ["Forward"],
            "Position": [85, 0, 12.25, 13.5]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [3, 1.5, 12.25, 13.5]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [3, 13.25, 12.25, 13.5]
        }
    },
    "MOTOR": {
        "SHB": {
            "Position": [83, 88.5, 10, 10]
        },
        "HPPS": {
            "Position": [46, 71, 10, 10]
        }
    }
}

MOTOR_CONTROL = {
    "General": {
        "Absolute Position": ":POS_RB",
        "Status": {
            "Moving": ":BUSY",
            "Error": ":ST"
        },
        "Up to Limit": ":UP.PROC",
        "Limits": {
            "Upper": ":IS_A",
            "Lower": ":IS_B"
        }
    },
    "SHB": {
        "PID Mode": ":SET_PID_MODE",
        "Fw/Bw Steps": ":FL",
        "KI": ":SET_PID_KI",
        "KP": ":SET_PID_KP"
    },
    "HPPS": [
        ":SET_SHIF_MOTOR_ANGLE",
        ":GET_SHIF_MOTOR_ANGLE_CALC"
    ]
}
