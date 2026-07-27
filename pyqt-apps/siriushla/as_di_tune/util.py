from qtpy.QtGui import QColor

marker_color = {
    'Mark': {
        'H': {
            '1': QColor('blue'),
            '2': QColor('darkBlue'),
            '3': QColor('cyan'),
            '4': QColor('darkCyan'),
        },
        'V': {
            '1': QColor('red'),
            '2': QColor('darkRed'),
            '3': QColor('magenta'),
            '4': QColor('darkMagenta'),
        },
    },
    'DMark': {
        'H': {
            '1': QColor('green'),
            '2': QColor('darkGreen'),
            '3': QColor('gray'),
            '4': QColor('darkGray'),
        },
        'V': {
            '1': QColor(255, 153, 102),
            '2': QColor(255, 77, 77),
            '3': QColor(255, 153, 0),
            '4': QColor(204, 51, 0),
        },
    },
}
