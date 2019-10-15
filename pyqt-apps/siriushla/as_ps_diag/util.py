"""Util module."""

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

sips2filters = {'B': {'sec': 'SI', 'sub': '.*', 'dev': 'B.*'},
                'Q': {'sec': 'SI', 'sub': 'Fam', 'dev': 'Q(F|D|[1-4]).*'},
                'S': {'sec': 'SI', 'sub': '.*', 'dev': 'S.*'},
                'PM': {'sec': 'SI', 'sub': '.*', 'dev': '(Inj|Eje).*'},
                # 'CV': {'sec': 'SI', 'sub': '.*', 'dev': 'CV.*'},
                # 'CH': {'sec': 'SI', 'sub': '.*', 'dev': 'CH.*'},
                # 'Trims': {'sec': 'SI', 'sub': '[0-2][0-9].*',
                #           'dev': 'Q(F|D|[1-4]).*'},
                # 'QS': {'sec': 'SI', 'sub': '.*', 'dev': 'QS.*'},
                # 'FCV ': {'sec': 'SI', 'sub': '.*', 'dev': 'FCV.*'},
                # 'FCH ': {'sec': 'SI', 'sub': '.*', 'dev': 'FCH.*'}}
                }
