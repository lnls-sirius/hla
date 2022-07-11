BASIC_INFO = {
    "BUN1": {
        "CH1": {
            "Chart": ["Pick-Up"],
            "Position": [22.75, 57.5, 12.25, 12]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [11.5, 54.75, 12.25, 12]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [0, 75, 12.25, 12]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [0, 54.75, 12.25, 12]
        }
    },
    "KLY1": {
        "CH1": {
            "Chart": ["Forward", "Reflected"],
            "Position": [27, 26.5, 12.25, 13]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [12.5, 26.5, 12.25, 12]
        },
        "CH3": {
            "Chart": ["Forward"],
            "Position": [35, 67, 12.25, 12]
        },
        "CH4": {
            "Chart": ["Forward"],
            "Position": [48.5, 67, 12.25, 12]
        },
        "CH5": {
            "Chart": ["Forward"],
            "Position": [61.5, 67, 12.25, 12]
        },
        "CH6": {
            "Chart": ["Forward"],
            "Position": [35, 89, 12.25, 12]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [0, 44, 12.25, 12]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [0, 26.5, 12.25, 12]
        }
    },
    "KLY2": {
        "CH1": {
            "Chart": ["Forward", "Reflected"],
            "Position": [27, 0, 12.25, 13]
        },
        "CH2": {
            "Chart": ["Forward"],
            "Position": [12.5, 0, 12.25, 12]
        },
        "CH3": {
            "Chart": ["Forward"],
            "Position": [75, 67, 12.25, 12]
        },
        "CH4": {
            "Chart": ["Forward"],
            "Position": [88.5, 67, 12.25, 12]
        },
        "CH5": {
            "Chart": ["Forward"],
            "Position": [75, 89, 12.25, 12]
        },
        "CH6": {
            "Chart": ["Forward"],
            "Position": [88.5, 89, 12.25, 12]
        },
        "CH7": {
            "Chart": ["Reference"],
            "Position": [0, 0, 12.25, 12]
        },
        "CH8": {
            "Chart": ["VM"],
            "Position": [0, 16, 12.25, 12]
        }
    }
}


# Extra Windows Parameters
# [
#     para_kly2.edl -> PV_PREFIX=KLY2,SUB_NAME=Klystron2
#     para_kly1.edl -> PV_PREFIX=KLY1,SUB_NAME=Klystron1
#     para_kly0.edl -> PV_PREFIX=BUN1,SUB_NAME=Buncher
# ]

# Extra Windows Motor Control
# [
#     shb.edl -> BUN1_PREFIX=BUN1,SHB_PREFIX=SHB
#     hpps.edl -> PPS_PREFIX=HPPS
# ]

# # buncher

# GET_AMP
# GET_EXTERNAL_TRIGGER_ENABLE
# GET_FB_MODE
# GET_INTEGRAL_ENABLE
# GET_PHASE
# GET_PHASE_DIFF
# GET_STREAM
# GET_TRIGGER_STATUS
# SET_AMP
# SET_EXTERNAL_TRIGGER_ENABLE
# SET_FB_MODE
# SET_INTEGRAL_ENABLE
# SET_PHASE
# SET_STREAM

# # klystron 1

# GET_AMP
# GET_EXTERNAL_TRIGGER_ENABLE
# GET_FB_MODE
# GET_INTEGRAL_ENABLE
# GET_INTERLOCK
# GET_PHASE
# GET_REFL_POWER_LIMIT
# GET_STREAM
# GET_TRIGGER_STATUS
# SET_AMP
# SET_EXTERNAL_TRIGGER_ENABLE
# SET_FB_MODE
# SET_INTEGRAL_ENABLE
# SET_PHASE
# SET_REFL_POWER_LIMIT
# SET_STREAM


# # klystron 2

# GET_AMP
# GET_EXTERNAL_TRIGGER_ENABLE
# GET_FB_MODE
# GET_INTEGRAL_ENABLE
# GET_INTERLOCK
# GET_PHASE
# GET_REFL_POWER_LIMIT
# GET_STREAM
# GET_TRIGGER_STATUS
# SET_AMP
# SET_EXTERNAL_TRIGGER_ENABLE
# SET_FB_MODE
# SET_INTEGRAL_ENABLE
# SET_PHASE
# SET_REFL_POWER_LIMIT
# SET_STREAM
