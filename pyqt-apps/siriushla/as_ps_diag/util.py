"""Util module."""

from siriuspy.namesys import SiriusPVName

# Constants

LINAC_PS = (
    'LI-01:PS-LensRev',
    'LI-01:PS-Lens-1',
    'LI-01:PS-Lens-2',
    'LI-01:PS-Lens-3',
    'LI-01:PS-Lens-4',
    'LI-01:PS-CV-1',
    'LI-01:PS-CH-1',
    'LI-01:PS-CV-2',
    'LI-01:PS-CH-2',
    'LI-01:PS-CV-3',
    'LI-01:PS-CH-3',
    'LI-01:PS-CV-4',
    'LI-01:PS-CH-4',
    'LI-01:PS-CV-5',
    'LI-01:PS-CH-5',
    'LI-01:PS-CV-6',
    'LI-01:PS-CH-6',
    'LI-01:PS-CV-7',
    'LI-01:PS-CH-7',
    'LI-01:PS-Slnd-1',
    'LI-01:PS-Slnd-2',
    'LI-01:PS-Slnd-3',
    'LI-01:PS-Slnd-4',
    'LI-01:PS-Slnd-5',
    'LI-01:PS-Slnd-6',
    'LI-01:PS-Slnd-7',
    'LI-01:PS-Slnd-8',
    'LI-01:PS-Slnd-9',
    'LI-01:PS-Slnd-10',
    'LI-01:PS-Slnd-11',
    'LI-01:PS-Slnd-12',
    'LI-01:PS-Slnd-13',
    'LI-Fam:PS-Slnd-14',
    'LI-Fam:PS-Slnd-15',
    'LI-Fam:PS-Slnd-16',
    'LI-Fam:PS-Slnd-17',
    'LI-Fam:PS-Slnd-18',
    'LI-Fam:PS-Slnd-19',
    'LI-Fam:PS-Slnd-20',
    'LI-Fam:PS-Slnd-21',
    'LI-Fam:PS-QF1',
    'LI-Fam:PS-QF2',
    'LI-01:PS-QF3',
    'LI-01:PS-QD1',
    'LI-01:PS-QD2',
    'LI-01:PS-Spect')

LINAC_PS = [SiriusPVName(text) for text in LINAC_PS]

sec2label = {'LI': 'Linac',
             'TB': 'LTB',
             'BO': 'Booster'}
#              'TS': 'BTS',
#              'SI': 'Storage Ring'}
# # TODO: discomment to use TS and SI


lips2labels = {':PS-Lens.*': 'Lens',
               ':PS-(CH|CV).*': 'Correctors',
               ':PS-Slnd.*': 'Solenoids',
               ':PS-(QF|QD).*': 'Quadrupoles',
               ':PS-Spect.*': 'Spectrometer'}

asps2labels = {'B.*': 'Dipoles',
               'Q(F|D|[1-4]).*': 'Quadrupoles',
               'QS.*': 'Skew Quadrupoles ',
               'S.*': 'Sextupoles',
               'C(H|V).*': 'Slow Correctors ',
               'FC(H|V).*': 'Fast Correctors ',
               '(Inj|Eje).*': 'Pulsed Magnets'}

sips2labels = {'Dipoles Families': {'sec': 'SI', 'dev': 'B.*'},
               'Quadrupoles Families': {'sec': 'SI', 'sub': 'Fam',
                                        'dev': 'Q(F|D|[1-4]).*'},
               'Sextupoles Families': {'sec': 'SI', 'dev': 'S.*'},
               'Slow Vertical Correctors ': {'sec': 'SI', 'dev': 'CV.*'},
               'Slow Horizontal Correctors ': {'sec': 'SI', 'dev': 'CH.*'},
               'Trims': {'sec': 'SI', 'sub': '[0-2][0-9].*',
                         'dev': 'Q(F|D|[1-4]).*'},
               'Skew Quadrupoles ': {'sec': 'SI', 'dev': 'QS.*'},
               'Fast Vertical Correctors ': {'sec': 'SI', 'dev': 'FCV.*'},
               'Fast Horizontal Correctors ': {'sec': 'SI', 'dev': 'FCH.*'}}
