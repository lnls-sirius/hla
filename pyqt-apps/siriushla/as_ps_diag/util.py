"""Util module."""

from siriuspy.search import PSSearch

# Constants

lips2filters = {'Lens': {'sec': 'LI', 'sub': '.*', 'dev': 'Lens.*'},
                'CH': {'sec': 'LI', 'sub': '.*', 'dev': 'CH'},
                'CV': {'sec': 'LI', 'sub': '.*', 'dev': 'CV'},
                'Slnd': {'sec': 'LI', 'sub': '.*', 'dev': 'Slnd.*'},
                'Q': {'sec': 'LI', 'sub': '.*', 'dev': '(QF|QD).*'},
                'Spect': {'sec': 'LI', 'sub': '.*', 'dev': 'Spect.*'},
                }

asps2filters = {'B': {'sub': '.*', 'dev': 'B.*'},
                'Q': {'sub': '.*', 'dev': 'Q(F|D|[1-4]).*'},
                'QS': {'sub': '.*', 'dev': 'QS.*'},
                'S': {'sub': '.*', 'dev': 'S.*'},
                'CH': {'sub': '.*', 'dev': 'CH'},
                'CV': {'sub': '.*', 'dev': 'CV'},
                'PM': {'sub': '.*', 'dev': '(Inj|Eje).*'},
                }

sips2filters = {'B': {'sec': 'SI', 'sub': '.*', 'dev': 'B.*'},
                'Q': {'sec': 'SI', 'sub': 'Fam', 'dev': 'Q(F|D|[1-4]).*'},
                'S': {'sec': 'SI', 'sub': '.*', 'dev': 'S.*'},
                'CV': {'sec': 'SI', 'sub': '.*(M|C).*', 'dev': 'CV.*'},
                'CH': {'sec': 'SI', 'sub': '.*(M|C).*', 'dev': 'CH.*'},
                'ID-CH/CV/QS/CC': {'sec': 'SI', 'sub': '.*S(A|B|P)',
                                'dev': '(LCH|CH|CV|CC|QS)'},
                'FFCH/FFCV': {'sec': 'SI', 'dev': 'FFC.*'},
                'Trims': {'sec': 'SI', 'sub': '[0-2][0-9].*',
                          'dev': 'Q(F|D|[1-4]).*'},
                'QS': {'sec': 'SI', 'sub': '[0-2][0-9](M|C).*', 'dev': 'QS'},
                'PM': {'sec': 'SI', 'sub': '.*', 'dev': '.*(Kckr|Sept)',
                       'propty_name': '(?!:CCoil).*'},
                'FCH': {'sec': 'SI', 'sub': '(?!01M).*', 'dev': 'FCH'},
                'FCV': {'sec': 'SI', 'sub': '(?!01M).*', 'dev': 'FCV'},
                }


def get_label2devices(sec):
    data = dict()
    if sec == 'LI':
        ps2filt = lips2filters
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
        'CH': (1, 0, 1, 2),
        'CV': (1, 2, 1, 1),
        'Slnd': (2, 0, 1, 5),
    },
    'TB': {
        'B': (0, 0, 1, 2),
        'Q': (1, 0, 1, 4),
        'PM': (0, 2, 1, 2),
        'CH': (2, 0, 1, 2),
        'CV': (2, 2, 1, 2),
    },
    'BO': {
        'B': (0, 0, 1, 1),
        'Q': (0, 1, 1, 1),
        'S': (1, 0, 1, 1),
        'QS': (1, 1, 1, 1),
        'PM': (2, 0, 1, 1),
        'CH': (0, 2, 3, 2),
        'CV': (0, 4, 3, 2),
    },
    'TS': {
        'B': (0, 0, 1, 2),
        'Q': (1, 0, 1, 5),
        'PM': (0, 2, 1, 3),
        'CH': (2, 0, 1, 2),
        'CV': (2, 2, 1, 3),
    },
    'SI': {
        'B': (0, 1, 1, 1),
        'PM': (0, 2, 1, 1),
        'FFCH/FFCV': (0, 3, 1, 1),
        'Q': (0, 4, 1, 1),
        'S': (0, 5, 1, 1),
        'ID-CH/CV/QS/CC': (0, 7, 1, 2),
        'QS': (1, 1, 1, 2),
        'CH': (1, 3, 1, 1),
        'CV': (1, 4, 1, 1),
        'Trims': (1, 5, 1, 2),
        'FCH': (1, 7, 1, 1),
        'FCV': (1, 8, 1, 1),
    },
}


def get_sec2dev_laypos(sec, label):
    return SEC2LABEL2SECPOS[sec][label]


def get_col2dev_count(sec, label):
    if label == 'QS':
        return 5
    if label == 'CH':
        return 6 if sec == 'SI' else 5 if sec == 'BO' else 7
    if label == 'CV':
        return 8 if sec == 'SI' else 5 if sec == 'BO' else 10
    if 'Trims' in label:
        return 14
    if 'FFC' in label:
        return 4
    if 'ID' in label:
        return 8
    if 'FC' in label:
        return 4
    if label == 'S':
        return 11
    if label == 'Q':
        return 10 if sec != 'SI' else 6
    if label == 'Slnd':
        return 21
    return 10


def get_dev2sub_labels(label):
    sub2labels = {
        'QS': ('M1', 'M2', 'C1', 'C2', 'C3'),
        'CH': ('M1', 'M2', 'C1', 'C2', 'C3', 'C4'),
        'CV': ('M1', 'M2', 'C1', 'C2', 'C2', 'C3', 'C3', 'C4'),
        'Trims': ('M1', 'M1', 'M1', 'M2', 'M2', 'M2', 'C1', 'C1',
                  'C2', 'C2', 'C3', 'C3', 'C4', 'C4'),
        'FCH': ('M1', 'M2', 'C2', 'C3'),
        'FCV': ('M1', 'M2', 'C2', 'C3'),
    }
    return sub2labels[label]
