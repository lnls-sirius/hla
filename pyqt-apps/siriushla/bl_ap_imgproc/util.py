IMG_PVS = ['Projection']

LED_PVS = [
    'Saturated', 'With Beam'
]

SPRB_LED_PV = 'Update'

LOG_PV = ['Log']

PVS = {
    'IOC':  [
        (1, 1, 1, 1),
        {
            'Boot Time': 'ImgTimestampBoot-Cte',
            'Update Time': 'ImgTimestampUpdate-Mon'
        }
    ],
    'Img': [
        (1, 2, 1, 8),
        {
            'Size X': 'ImgSizeX-Cte',
            'Size Y': 'ImgSizeY-Cte',
            'Projection': [
                'ImgProjX-Mon', 'ImgProjY-Mon'
            ],
            'Intensity Min': 'ImgIntensityMin-Mon',
            'Intensity Max': 'ImgIntensityMax-Mon',
            'Intensity Threshold': [
                'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB'
            ],
            'Saturated': 'ImgIsSaturated-Mon',
            'With Beam': 'ImgIsWithBeam-Mon'
        }
    ],
    'ROI': [
        (2, 1, 2, 3),
        {
            'ROI X': [
                'ImgROIX-SP', 'ImgROIX-RB'
            ],
            'ROI Y': [
                'ImgROIY-SP', 'ImgROIY-RB'
            ],
            'ROI X Center': 'ImgROIXCenter-Mon',
            'ROI Y Center': 'ImgROIYCenter-Mon',
            'ROI X FWHM': 'ImgROIXFWHM-Mon',
            'ROI Y FWHM': 'ImgROIYFWHM-Mon'
        }
    ],
    'ROI Update': [
        (2, 4, 2, 1),
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
        (2, 5, 2, 4),
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
        (2, 9, 2, 1),
        {
            'Log': 'ImgLog-Mon'
        }
    ]
}