"""Util module."""
from copy import deepcopy as _dcopy

# Constants

lips2filters = {'Lens': {'sec': 'LI', 'sub': '.*', 'dev': 'Lens.*'},
                'CH/CV': {'sec': 'LI', 'sub': '.*', 'dev': '(CH|CV).*'},
                'Slnd': {'sec': 'LI', 'sub': '.*', 'dev': 'Slnd.*'},
                'Q': {'sec': 'LI', 'sub': '.*', 'dev': '(QF|QD).*'},
                'Spect': {'sec': 'LI', 'sub': '.*', 'dev': 'Spect.*'},
                }

asps2filters = {'B': {'sub': '.*', 'dev': 'B.*'},
                'Q': {'sub': '.*', 'dev': 'Q(F|D|[1-4]).*'},
                'QS': {'sub': '.*', 'dev': 'QS.*'},
                'S': {'sub': '.*', 'dev': 'S.*'},
                'CH/CV': {'sub': '.*', 'dev': 'C(H|V).*'},
                'PM': {'sub': '.*', 'dev': '(Inj|Eje).*'},
                }

bops2filters = _dcopy(asps2filters)
bops2filters.pop('CH/CV')
bops2filters['CH'] = {'sub': '.*', 'dev': 'CH.*'}
bops2filters['CV'] = {'sub': '.*', 'dev': 'CV.*'}

sips2filters = {'B': {'sec': 'SI', 'sub': '.*', 'dev': 'B.*'},
                'Q': {'sec': 'SI', 'sub': 'Fam', 'dev': 'Q(F|D|[1-4]).*'},
                'S': {'sec': 'SI', 'sub': '.*', 'dev': 'S.*'},
                'CV': {'sec': 'SI', 'sub': '.*(M|C).*', 'dev': 'CV.*'},
                'CH': {'sec': 'SI', 'sub': '.*(M|C).*', 'dev': 'CH.*'},
                'Trims': {'sec': 'SI', 'sub': '[0-2][0-9].*',
                          'dev': 'Q(F|D|[1-4]).*'},
                'QS': {'sec': 'SI', 'sub': '[0-2][0-9].*', 'dev': 'QS'},
                'PM': {'sec': 'SI', 'sub': '.*', 'dev': '(Inj|Eje).*'},
                'ID-CH': {'sec': 'SI', 'sub': '.*S(A|B|P)', 'dev': 'CH'},
                'ID-CV': {'sec': 'SI', 'sub': '.*S(A|B|P)', 'dev': 'CV'},
                # 'FCV ': {'sec': 'SI', 'sub': '.*', 'dev': 'FCV.*'},
                # 'FCH ': {'sec': 'SI', 'sub': '.*', 'dev': 'FCH.*'},
                }
