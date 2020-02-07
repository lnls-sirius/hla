from qtpy.QtGui import QColor

marker_color = {
    'Mark': {
        'H': {
            '1': 'blue',
            '2': 'darkBlue',
            '3': 'cyan',
            '4': 'darkCyan',
        },
        'V': {
            '1': 'red',
            '2': 'darkRed',
            '3': 'magenta',
            '4': 'darkMagenta',
        },
    },
    'DMark': {
        'H': {
            '1': 'green',
            '2': 'darkGreen',
            '3': 'gray',
            '4': 'darkGray',
        },
        'V': {
            '1': QColor(255, 153, 102),
            '2': QColor(255, 77, 77),
            '3': QColor(255, 153, 0),
            '4': QColor(204, 51, 0),
        },
    }
}
