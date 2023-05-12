IMG_PVS = ['Projection']

LED_PVS = [
    'Saturated', 'With Beam'
]

LOG_PV = ['Log']

PVS = {
    'IOC':  [
        (1, 0, 1, 1),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon'
        }
    ],
    'Img': [
        (2, 0, 6, 1),
        {
            'Size X': 'ImgSizeX-Cte',
            'Size Y': 'ImgSizeY-Cte',
            'Projection': ['image1:ArrayData', 'ImgSizeX-Cte'],
            'Saturated': 'ImgIsSaturated-Mon',
            'With Beam': 'ImgIsWithBeam-Mon'
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
        (3, 1, 3, 1),
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
        (3, 2, 3, 1),
        {
            'Min': 'ImgIntensityMin-Mon',
            'Max': 'ImgIntensityMax-Mon',
            'Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB'
            ]
        }
    ],
    'Fit': [
        (6, 1, 2, 2),
        {
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
            'Angle': 'ImgFitAngle-Mon'
        }
    ],
    'Log': [
        (8, 0, 1, 3),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}
