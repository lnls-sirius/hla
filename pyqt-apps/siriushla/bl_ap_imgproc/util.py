"""Utilities."""

from siriuspy.dvfimgproc.csdev import ETypes

IMG_PVS = ['Projection']
LOG_PV = ['Log']
LED_ALERT_PVS = ['IsSaturated Ok']
LED_STATE_PVS = ['IsWithBeam Ok']
LED_DETAIL_PVS = ['DVF Status']
COMBOBOX_PVS = [
    'Enable',
    'Acquire',
    'Image Mode',
    'Gain Auto',
    'Data Type',
    'Pixel Format',
    'Pixel Size',
    'ArrayCallbacks',
    'EnableCallbacks',
    'ffmstream1 - EnableCallbacks',
    'Trans1 - EnableCallbacks',
    'HDF1 - EnableCallbacks',
]
LINEEDIT_PVS = [
    'Min Max',
    'Beam Threshold',
    'NDArrayPort',
    'Acquire Time',
    'Acquire Period',
    'Gain',
]
STATEBUT_PVS = [
    'Update',
    'Use SVD',
]


PVS_IMGPROCOVERVIEW = {
    'Image Info': [
        (1, 0, 1, 3),
        {
            'Size X': 'ImgSizeX-Mon',
            'Size Y': 'ImgSizeY-Mon',
        },
        {
            'Center X': 'ImgROIXFitMean-Mon',
            'Center Y': 'ImgROIYFitMean-Mon',
        },
        {
            'Sigma1': 'ImgFitSigma1-Mon',
            'Sigma2': 'ImgFitSigma2-Mon',
        },
        {
            'Angle': 'ImgFitAngle-Mon',
        }
    ],
    'Image': [
        (2, 0, 1, 3),
        {
            'Projection': ['image1:ArrayData', 'image1:ArraySize0_RBV'],
        }
    ],
}

PVS_IMGPROCCTRL = {
    'IOC':  [
        (1, 0, 1, 2),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon',
        }
    ],
    'DVF': [
        (2, 0, 1, 2),
        {
            'DVF Status': ['ImgDVFStatus-Mon', ETypes.STS_LBLS_DVF],
        },
        {
            'DVF Acquire': 'ImgDVFAcquire-Cmd',
            'DVF Reset': 'ImgDVFReset-Cmd',
        },
        {
            'DVF Size X': 'ImgDVFSizeX-Cte',
            'DVF Size Y': 'ImgDVFSizeY-Cte',

        }
    ],
    'ROI': [
        (3, 1, 1, 2),
        {
            'X': {
                'Min Max': [
                    'ImgROIX-SP', 'ImgROIX-RB'
                ],
                'Center': 'ImgROIXCenter-Mon',
                'FWHM': 'ImgROIXFWHM-Mon'
            },
            'Y': {
                'Min Max': [
                    'ImgROIY-SP', 'ImgROIY-RB'
                ],
                'Center': 'ImgROIYCenter-Mon',
                'FWHM': 'ImgROIYFWHM-Mon'
            }
        }
    ],
    'ROI Update': [
        (3, 0, 1, 1),
        {
            'ROI X FWHM Factor': [
                'ImgROIXUpdateWithFWHMFactor-SP',
                'ImgROIXUpdateWithFWHMFactor-RB'
            ],
            'ROI Y FWHM Factor': [
                'ImgROIYUpdateWithFWHMFactor-SP',
                'ImgROIYUpdateWithFWHMFactor-RB'
            ],
            'Update': [
                'ImgROIUpdateWithFWHM-Sel',
                'ImgROIUpdateWithFWHM-Sts'
            ]
        }
    ],
    'Intensity': [
        (1, 2, 2, 1),
        {
            'Min': 'ImgIntensityMin-Mon',
            'Max': 'ImgIntensityMax-Mon',
            'Beam Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB',
            ],
            'IsWithBeam Ok': 'ImgIsWithBeam-Mon',
            'IsSaturated Ok': 'ImgIsSaturated-Mon',
        }
    ],
    'Fit': [
        (5, 0, 1, 3),
        {
            'Proc. Time': 'ImgFitProcTime-Mon',
            'Use SVD': [
                'ImgFitAngleUseCMomSVD-Sel',
                'ImgFitAngleUseCMomSVD-Sts',
            ],
            'X': {
                'ROI Mean': 'ImgROIXFitMean-Mon',
                'ROI Sigma': 'ImgROIXFitSigma-Mon',
                'ROI Error': 'ImgROIXFitError-Mon'
            },
            'Y': {
                'ROI Mean': 'ImgROIYFitMean-Mon',
                'ROI Sigma': 'ImgROIYFitSigma-Mon',
                'ROI Error': 'ImgROIYFitError-Mon'
            },
            'Angle': 'ImgFitAngle-Mon',
            'Sigma1': 'ImgFitSigma1-Mon',
            'Sigma2': 'ImgFitSigma2-Mon',
        }
    ],
    'Log': [
        (6, 0, 1, 3),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}

PVS_DVF = {
    'ROI Control': [
        (0, 0, 1, 3),
        {
            'X': {
                'Enable': ['ROI1:EnableX', 'ROI1:EnableX_RBV'],
                'Min': ['ROI1:MinX', 'ROI1:MinX_RBV'],
                'Size': ['ROI1:SizeX', 'ROI1:SizeX_RBV'],
            },
            'Y': {
                'Enable': ['ROI1:EnableY', 'ROI1:EnableY_RBV'],
                'Min': ['ROI1:MinY', 'ROI1:MinY_RBV'],
                'Size': ['ROI1:SizeY', 'ROI1:SizeY_RBV'],
            },
            'NDArrayPort': ['ROI1:NDArrayPort', 'ROI1:NDArrayPort_RBV'],
            'EnableCallbacks': [
                'ROI1:EnableCallbacks', 'ROI1:EnableCallbacks_RBV'],
            'ArrayCallbacks': [
                'ROI1:ArrayCallbacks', 'ROI1:ArrayCallbacks_RBV'],
        }
    ],
    'Camera General Status': [
        (1, 0, 1, 1),
        {
            'Max Size X': 'cam1:MaxSizeX_RBV',
            'Max Size Y': 'cam1:MaxSizeY_RBV',
            'Offset X': 'cam1:MinX_RBV',
            'Offset Y': 'cam1:MinY_RBV',
            'Size X': 'cam1:SizeX_RBV',
            'Size Y': 'cam1:SizeY_RBV',
            'Temperature': 'cam1:GC_TemperatureAbs_RBV',
            'Failures': 'cam1:ARFrameFailures',
            'Completed': 'cam1:ARFramesCompleted',
        }
    ],
    'Camera Acquisition': [
        (1, 1, 1, 2),
        {
            'Acquire Time': [
                'cam1:AcquireTime', 'cam1:AcquireTime_RBV'],
            'Acquire Period': [
                'cam1:AcquirePeriod', 'cam1:AcquirePeriod_RBV'],
            'Acquire': [
                'cam1:Acquire', 'cam1:Acquire_RBV'],
            'Image Mode': [
                'cam1:ImageMode', 'cam1:ImageMode_RBV'],
        }
    ],
    'Camera Gain': [
        (2, 0, 1, 1),
        {
            'Gain': [
                'cam1:Gain', 'cam1:Gain_RBV'],
            'Gain Auto': [
                'cam1:GainAuto', 'cam1:GainAuto_RBV'],
        }
    ],
    'Camera Data Settings': [
        (2, 1, 1, 2),
        {
            'Data Type': [
                'cam1:DataType', 'cam1:DataType_RBV'],
            'Pixel Format': [
                'cam1:PixelFormat', 'cam1:PixelFormat_RBV'],
            'ArrayCallbacks': [
                'cam1:ArrayCallbacks', 'cam1:ArrayCallbacks_RBV'],
        }
    ],
    'Image Control': [
        (3, 0, 1, 1),
        {
            'NDArrayPort': ['image1:NDArrayPort', 'image1:NDArrayPort_RBV'],
            'ArraySize0': 'image1:ArraySize0_RBV',
            'ArraySize1': 'image1:ArraySize1_RBV',
            'EnableCallbacks': [
                'image1:EnableCallbacks', 'image1:EnableCallbacks_RBV'],
        },
    ],
    'Other Pluggins Settings': [
        (3, 1, 1, 2),
        {
            'Trans1 - EnableCallbacks': [
                'Trans1:EnableCallbacks', 'Trans1:EnableCallbacks_RBV'],
            'HDF1 - EnableCallbacks': [
                'HDF1:EnableCallbacks', 'HDF1:EnableCallbacks_RBV'],
        },
    ],
}

INTLK_PVS = {
    "gamma": "AS-Glob:MP-Summary:AlarmGammaShutter-Mon"
}
