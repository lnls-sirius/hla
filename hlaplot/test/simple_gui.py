#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
simple_gui
    Show custom_plot.
"""

import sys
import datetime
import collections
import numpy
from PyQt5 import QtWidgets, QtCore
import hlaplot.custom_plot as custom_plot
import hlaplot.datetime_plot as datetime_plot
import hlaplot.position_plot as position_plot
import hlaplot.custom_toolbar as custom_toolbar


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        """
        Return a plot window with

        window background: dark green
        plot background: light blue
        plot elements: dark red
        """
        super(Window, self).__init__(parent)

        args = {}
        args['background_color'] = (0, 100, 0, 255) # dark green
        args['axis_background_color'] = (155, 155, 255, 255) # light blue
        args['axis_elements_color'] = (100, 0, 0, 255) # dark red

        self.plot = custom_plot.CustomPlot(**args)
        self.plot_datetime = datetime_plot.DateTimePlot(**args)

        args['interval_min'] = -1
        args['interval_max'] = 10
        self.plot_position = position_plot.PositionPlot(**args)

        self.toolbar = custom_toolbar.CustomToolbar(self.plot_datetime, self)

        self.plot.show_x_grid('green', line_style='-', line_width=1.5)
        self.plot.show_y_grid('yellow', line_style='-', line_width=1.0)
        self.plot.hide_y_grid()

        self.plot_datetime.y_ticks_side = 'right'

        self.label = QtWidgets.QLabel("FPS")

        self.button = QtWidgets.QPushButton("&Clear")
        self.button.clicked.connect(self.clear)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_datetime)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot)
        layout.addWidget(self.plot_datetime)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_position)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # CustomPlot

        self.plot.set_spacing(left=0.2, bottom=0.1, top=0.7, right=0.9)

        self.plot.y_label = '$y = f(x)$'
        self.plot.title = 'Título do gráfico'
        self.plot.y_scale = 'log'
        self.plot.x_label = '$x$'

        self.plot.add_line('line1')
        self.plot.add_line('line2')
        self.plot.add_line('line3')

        x = numpy.linspace(1, 100, 50)
        y3 = 10 + numpy.sin(2*numpy.pi*x)
        self.plot.line('line3').x = x
        self.plot.line('line3').y = y3

        self.plot.line('line2').x = x
        y2 = 10 + numpy.random.normal(size=len(x))
        self.plot.line('line2').y = y2

        self.plot.remove_line('line1')
        self.plot.line('line2').color = 'white'
        print(self.plot.line('line2').color)
        self.plot.line('line2').line_style = '--'
        self.plot.line('line3').color = 'yellow'
        self.plot.line('line3').line_width = 2.0
        self.plot.line('line3').marker = 's'

        self.plot.x_axis_extra_spacing = 0
        self.plot.y_axis_extra_spacing = (0.1, 0.1)

        self.plot.update_plot()

        # DateTimePlot

        self.x = numpy.linspace(0, 2*numpy.pi, 100)
        self.x_index = 0

        self.plot_datetime.title = 'Title'
        self.plot_datetime.x_label = 'Time'
        self.plot_datetime.y_label = 'Data'
        self.plot_datetime.y_autoscale = False
        self.plot_datetime.y_axis = (0.0, 5.0)
        self.plot_datetime.x_ticks_label_format = '%H:%M'
        self.plot_datetime.x_tick_label_rotation = 0
        self.plot_datetime.datetime_coord_format = '%H:%M:%S'

        delta0 = datetime.timedelta(seconds=0)
        delta1 = datetime.timedelta(seconds=0)
        self.plot_datetime.x_axis_extra_spacing = (delta0, delta1)
        self.plot_datetime.y_axis_extra_spacing = 0.1
        self.plot_datetime.set_ticker('linear', 4)
        self.plot_datetime.interval = datetime.timedelta(seconds=600)
        self.plot_datetime.show_interval = True

        self.plot_datetime.add_line('line1', 3600)
        self.plot_datetime.line('line1').color = 'yellow'
        self.plot_datetime.add_line('line2', 3600)
        self.plot_datetime.line('line2').color = 'red'
        self.plot_datetime.add_line('line3', 3600)
        self.plot_datetime.line('line3').color = 'green'

        t0 = datetime.datetime.now() - datetime.timedelta(seconds=3600)
        t = [t0 + datetime.timedelta(seconds=i) for i in range(3600)]
        y1 = numpy.random.normal(size=len(t))
        y2 = numpy.random.normal(size=len(t))
        y3 = numpy.random.normal(size=len(t))

        self.plot_datetime.line('line1').x = t
        self.plot_datetime.line('line1').y = y1
        self.plot_datetime.line('line2').x = t
        self.plot_datetime.line('line2').y = y2
        self.plot_datetime.line('line3').x = t
        self.plot_datetime.line('line3').y = y3

        self.update_times = collections.deque(maxlen=10)
        self.last_update = datetime.datetime.now()
        self.timer.start(100)

        # PositionPlot

        self.plot_position.show_y_grid()

        size = 10
        names = ['AMP' + str(5+i)+'A' for i in range(size)]
        pos = range(size)
        values = numpy.random.normal(size=len(pos))

        self.plot_position.title = 'Posição'
        self.plot_position.x_label = 'x'
        self.plot_position.y_label = 'Valor'

        self.plot_position.define_ticks(names, pos)
        self.plot_position.x_axis_extra_spacing = 0.01
        self.plot_position.y_axis_extra_spacing = 0.05
        selected_ticks = names[0:-1:2]
        self.plot_position.select_ticks(selected_ticks)
        self.plot_position.add_line('line', interpolate=True)
        self.plot_position.add_line('markers', interpolate=False)
        self.plot_position.line('line').x = pos
        self.plot_position.line('line').y = values
        self.plot_position.line('markers').x = pos
        self.plot_position.line('markers').y = values
        self.plot_position.line('markers').marker = 's'
        self.plot_position.line('markers').line_style = ''
        self.plot_position.line('markers').marker_fill = 'left'
        self.plot_position.line('markers').marker_color = 'blue'
        self.plot_position.line('markers').marker_edge_color = 'blue'
        self.plot_position.line('markers').marker_face_color = 'blue'
        print(self.plot_position.selected_ticks)
        self.plot_position.x_tick_label_rotation = 10
        self.plot_position.set_spacing(bottom=0.25, right=0.95)

        self.plot_position.update_plot()

    def update_plot_datetime(self):
        i = self.x_index
        s = numpy.sin(self.x[i % 100])
        self.x_index += 1
        t = datetime.datetime.now()
        y1 = numpy.random.normal()
        y2 = 2 + s + numpy.random.normal(0, 0.05)
        y3 = numpy.random.normal(3, 0.25)
        self.plot_datetime.line('line1').add_xy(t, y1)
        self.plot_datetime.line('line2').add_xy(t, y2)
        self.plot_datetime.line('line3').add_xy(t, y3)
        self.plot_datetime.update_plot()

        delta = datetime.datetime.now() - self.last_update
        self.update_times.append(delta)
        sum_seconds = 0
        for t in self.update_times:
            sum_seconds += t.seconds + t.microseconds / 1e6
        fps = len(self.update_times) / sum_seconds
        value = '{0:3.1f}'.format(fps)
        self.label.setText("FPS: " + value)
        self.last_update = datetime.datetime.now()

    def clear(self):
        self.plot_datetime.clear()
        self.plot_datetime.update_plot()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())
