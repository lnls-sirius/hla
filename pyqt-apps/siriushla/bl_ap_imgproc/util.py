IMG_PVS = ['Projection']

LED_PVS = [
    'Saturated', 'With Beam'
]

LOG_PV = ['Log']

PVS = {
    'IOC':  [
        (0, 0, 3, 1),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon'
        }
    ],
    'Img': [
        (0, 1, 3, 7),
        {
            'Size X': 'ImgSizeX-Cte',
            'Size Y': 'ImgSizeY-Cte',
            'Projection': 'image1:ArrayData',
            'Saturated': 'ImgIsSaturated-Mon',
            'With Beam': 'ImgIsWithBeam-Mon'
        }
    ],
    'ROI': [
        (3, 0, 2, 3),
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
        (3, 3, 1, 2),
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
        (4, 3, 1, 2),
        {
            'Min': 'ImgIntensityMin-Mon',
            'Max': 'ImgIntensityMax-Mon',
            'Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB'
            ]
        }
    ],
    'Fit': [
        (3, 5, 2, 3),
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
        (0, 8, 5, 1),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}
