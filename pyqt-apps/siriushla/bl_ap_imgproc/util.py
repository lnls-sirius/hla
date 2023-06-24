IMG_PVS = ['Projection']

LED_PVS = [
    'Saturated', 'With Beam',
]

LED_ALARM = ['DVF Status']

LOG_PV = ['Log']

PVS = {
    'IOC':  [
        (1, 0, 1, 1),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon'
        }
    ],
    'DVF': [
        (2, 0, 1, 1),
        {
            'DVF Status': 'ImgDVFStatus-Mon',
            'DVF Size X': 'ImgDVFSizeX-Cte',
            'DVF Size Y': 'ImgDVFSizeY-Cte',
            'DVF Reset': 'ImgDVFReset-Cmd',
            'DVF Acquire': 'ImgDVFAcquire-Cmd',
        }
    ],
    'Img': [
        (3, 0, 6, 1),
        {
            'Img Size X': 'ImgSizeX-Mon',
            'Img Size Y': 'ImgSizeY-Mon',
            'Projection': ['image1:ArrayData', 'ImgSizeX-Mon'],
        }
    ],
    'ROI': [
        (1, 1, 2, 2),
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
        (3, 1, 4, 1),
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
        (3, 2, 4, 1),
        {
            'Min': 'ImgIntensityMin-Mon',
            'Max': 'ImgIntensityMax-Mon',
            'Beam Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB',
            ],
            'With Beam': 'ImgIsWithBeam-Mon',
            'Saturated': 'ImgIsSaturated-Mon',
        }
    ],
    'Fit': [
        (7, 1, 2, 2),
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
        (9, 0, 1, 3),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}

DVF_STATUS = "ImgDVFStatus-Mon"

PVS_DVF = {
    'ROI Control': [
        (1, 0, 1, 3),
        {
            'X': {
                'Size': [
                    'ROI1:SizeX', 'ROI1:SizeX_RBV'
                ],
                'Min': [
                    'ROI1:MinX', 'ROI1:MinX_RBV'
                ]
            },
            'Y': {
                'Size': [
                    'ROI1:SizeY', 'ROI1:SizeY_RBV'
                ],
                'Min': [
                    'ROI1:MinY', 'ROI1:MinY_RBV'
                ]
            }
        }
    ],
}
