"""Util module."""
from copy import deepcopy as _dcopy
from siriuspy.search import PSSearch

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


def get_label2devices(sec):
    data = dict()
    if sec == 'LI':
        ps2filt = lips2filters
    elif sec == 'BO':
        ps2filt = bops2filters
    elif sec == 'SI':
        ps2filt = sips2filters
    else:
        ps2filt = asps2filters

    for ps, filt in ps2filt.items():
        filt.update(sec=sec)
        data[ps] = PSSearch.get_psnames(filters=filt)
    return data


SEC2LABEL2SECPOS = {
    'LI': {
        'Spect': (0, 0, 1, 1),
        'Q': (0, 1, 1, 1),
        'Lens': (0, 2, 1, 1),
        'Slnd': (1, 0, 1, 3),
        'CH/CV': (2, 0, 1, 3),
    },
    'TB': {
        'B': (0, 0, 1, 2),
        'Q': (1, 0, 1, 4),
        'PM': (0, 2, 1, 2),
        'CH/CV': (2, 0, 1, 4),
    },
    'BO': {
        'B': (0, 0, 1, 1),
        'Q': (0, 1, 1, 1),
        'S': (1, 0, 1, 1),
        'QS': (1, 1, 1, 1),
        'PM': (2, 0, 1, 1),
        'CH': (0, 2, 3, 3),
        'CV': (0, 5, 3, 3),
    },
    'TS': {
        'B': (0, 0, 1, 2),
        'Q': (1, 0, 1, 4),
        'PM': (0, 2, 1, 2),
        'CH/CV': (2, 0, 1, 4),
    },
    'SI': {
        'B': (0, 1, 1, 1),
        'PM': (0, 2, 1, 1),
        'ID-CH': (0, 3, 1, 1),
        'ID-CV': (0, 4, 1, 1),
        'Q': (0, 5, 1, 1),
        'S': (0, 6, 1, 1),
        'QS': (1, 1, 1, 2),
        'CH': (1, 3, 1, 2),
        'CV': (1, 5, 1, 1),
        'Trims': (1, 6, 1, 2),
    },
}


def get_sec2dev_laypos(sec, label):
    return SEC2LABEL2SECPOS[sec][label]


def get_col2dev_count(sec, label):
    if label == 'QS':
        return 5
    elif label == 'CH':
        return 5 if sec != 'SI' else 6
    elif label == 'CV':
        return 5 if sec != 'SI' else 8
    elif 'Trims' in label:
        return 14
    elif label == 'S':
        return 11
    elif label == 'Q':
        return 10 if sec != 'SI' else 6
    elif label == 'CH/CV':
        return 20 if sec == 'BO' else 14
    elif label == 'Slnd':
        return 11
    elif label in ['ID-CH', 'ID-CV']:
        return 2
    else:
        return 10


def get_dev2sub_labels(label):
    sub2labels = {
        'QS': ('M1', 'M2', 'C1', 'C2', 'C3'),
        'CH': ('M1', 'M2', 'C1', 'C2', 'C3', 'C4'),
        'CV': ('M1', 'M2', 'C1', 'C2', ' ', 'C3', ' ', 'C4'),
        'Trims': ('M1', ' ', ' ', 'M2', ' ', ' ', 'C1', ' ',
                  'C2', ' ', 'C3', ' ', 'C4', ' ')}
    return sub2labels[label]
