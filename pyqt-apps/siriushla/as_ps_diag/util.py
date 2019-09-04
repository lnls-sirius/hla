"""Util module."""

# Constants

lips2labels = {'Lens.*': 'Lens',
               '(CH|CV).*': 'CH/CV',
               'Slnd.*': 'Slnd',
               '(QF|QD).*': 'Q',
               'Spect.*': 'Spect'}

asps2labels = {'B.*': 'B',
               'Q(F|D|[1-4]).*': 'Q',
               'QS.*': 'QS',
               'S.*': 'S',
               'C(H|V).*': 'CH/CV',
               '(Inj|Eje).*': 'PM'}

sips2labels = {'B': {'sec': 'SI', 'dev': 'B.*'},
               'Q': {'sec': 'SI', 'sub': 'Fam',
                     'dev': 'Q(F|D|[1-4]).*'},
               'S': {'sec': 'SI', 'dev': 'S.*'},
               'CV': {'sec': 'SI', 'dev': 'CV.*'},
               'CH': {'sec': 'SI', 'dev': 'CH.*'},
               'Trims': {'sec': 'SI', 'sub': '[0-2][0-9].*',
                         'dev': 'Q(F|D|[1-4]).*'},
               'QS': {'sec': 'SI', 'dev': 'QS.*'}}
#               'FCV ': {'sec': 'SI', 'dev': 'FCV.*'},
#               'FCH ': {'sec': 'SI', 'dev': 'FCH.*'}}
