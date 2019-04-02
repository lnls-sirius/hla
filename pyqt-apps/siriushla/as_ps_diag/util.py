"""Util module."""

from siriuspy.namesys import SiriusPVName


# Constants

LINAC_PS = [SiriusPVName(text) for text in (
            'LA-CN:H1MLPS-1', 'LA-CN:H1MLPS-2', 'LA-CN:H1MLPS-3',
            'LA-CN:H1MLPS-4', 'LA-CN:H1RCPS-1',
            'LA-CN:H1SCPS-1', 'LA-CN:H1SCPS-2', 'LA-CN:H1SCPS-3',
            'LA-CN:H1SCPS-4', 'LA-CN:H1LCPS-1', 'LA-CN:H1LCPS-2',
            'LA-CN:H1LCPS-3', 'LA-CN:H1LCPS-4', 'LA-CN:H1LCPS-5',
            'LA-CN:H1LCPS-6', 'LA-CN:H1LCPS-7', 'LA-CN:H1LCPS-8',
            'LA-CN:H1LCPS-9', 'LA-CN:H1LCPS-10',
            'LA-CN:H1SLPS-1', 'LA-CN:H1SLPS-2', 'LA-CN:H1SLPS-3',
            'LA-CN:H1SLPS-4', 'LA-CN:H1SLPS-5', 'LA-CN:H1SLPS-6',
            'LA-CN:H1SLPS-7', 'LA-CN:H1SLPS-8', 'LA-CN:H1SLPS-9',
            'LA-CN:H1SLPS-10', 'LA-CN:H1SLPS-11', 'LA-CN:H1SLPS-12',
            'LA-CN:H1SLPS-13', 'LA-CN:H1SLPS-14', 'LA-CN:H1SLPS-15',
            'LA-CN:H1SLPS-16', 'LA-CN:H1SLPS-17', 'LA-CN:H1SLPS-18',
            'LA-CN:H1SLPS-19', 'LA-CN:H1SLPS-20', 'LA-CN:H1SLPS-21',
            'LA-CN:H1FQPS-1', 'LA-CN:H1FQPS-2', 'LA-CN:H1FQPS-3',
            'LA-CN:H1DQPS-1', 'LA-CN:H1DQPS-2', 'LA-CN:H1DPPS-1')]


sec2label = {'LI': 'Linac',
             'TB': 'LTB',
             'BO': 'Booster'}
#              'TS': 'BTS',
#              'SI': 'Storage Ring'}
# # TODO: discomment to use TS and SI


lips2labels = {'H1(ML|RC).*': 'Lens',
               'H1(SC|LC).*': 'Correctors',
               'H1SL.*': 'Solenoids',
               'H1(F|D)Q.*': 'Quadrupoles',
               'H1DP.*': 'Spectrometer'}

asps2labels = {'B.*': 'Dipoles',
               'Q(F|D|[1-4]).*': 'Quadrupoles',
               'QS.*': 'Skew Quadrupoles ',
               'S.*': 'Sextupoles',
               'C(H|V).*': 'Slow Correctors ',
               'FC(H|V).*': 'Fast Correctors '}

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
