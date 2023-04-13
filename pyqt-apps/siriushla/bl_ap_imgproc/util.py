IMG_PVS = ['Projection']

LED_PVS = [
    'Saturated', 'With Beam'
]

LOG_PV = ['Log']

PVS = {
    'IOC':  [
        (1, 1, 3, 1),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon'
        }
    ],
    'Img': [
        (1, 2, 3, 6),
        {
            'Size X': 'ImgSizeX-Cte',
            'Size Y': 'ImgSizeY-Cte',
            'Projection': 'image1:ArrayData',
            'Saturated': 'ImgIsSaturated-Mon',
            'With Beam': 'ImgIsWithBeam-Mon'
        }
    ],
    'Intensity': [
        (1, 8, 3, 1),
        {
            'Min': 'ImgIntensityMin-Mon',
            'Max': 'ImgIntensityMax-Mon',
            'Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB'
            ]
        }
    ],
    'ROI': [
        (4, 1, 2, 3),
        {
            'X Min Max': [
                'ImgROIX-SP', 'ImgROIX-RB'
            ],
            'Y Min Max': [
                'ImgROIY-SP', 'ImgROIY-RB'
            ],
            'X Center': 'ImgROIXCenter-Mon',
            'Y Center': 'ImgROIYCenter-Mon',
            'X FWHM': 'ImgROIXFWHM-Mon',
            'Y FWHM': 'ImgROIYFWHM-Mon'
        }
    ],
    'ROI Update': [
        (4, 4, 2, 1),
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
    'Fit': [
        (4, 5, 2, 4),
        {
            'ROI X Mean': 'ImgROIXFitMean-Mon',
            'ROI Y Mean': 'ImgROIYFitMean-Mon',
            'ROI X Sigma': 'ImgROIXFitSigma-Mon',
            'ROI Y Sigma': 'ImgROIYFitSigma-Mon',
            'ROI X Error': 'ImgROIXFitError-Mon',
            'ROI Y Error': 'ImgROIYFitError-Mon',
            'Angle': 'ImgFitAngle-Mon'
        }
    ],
    'Log': [
        (1, 9, 5, 1),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}
