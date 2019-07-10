"""Util module."""

# Constants

sec2label = {'LI': 'Linac',
             'TB': 'LTB',
             'BO': 'Booster'}
#              'TS': 'BTS',
#              'SI': 'Storage Ring'}
# # TODO: discomment to use TS and SI


lips2labels = {'Lens.*': 'Lens',
               '(CH|CV).*': 'Correctors',
               'Slnd.*': 'Solenoids',
               '(QF|QD).*': 'Quadrupoles',
               'Spect.*': 'Spectrometer'}

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
