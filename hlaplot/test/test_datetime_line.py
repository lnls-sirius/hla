
import datetime
import unittest
import numpy
import matplotlib.backends.backend_qt5agg as backend
import matplotlib.figure
import hlaplot.datetime_line as datetime_line


class TestEmptyLine(unittest.TestCase):

    def setUp(self):
        self.figure = matplotlib.figure.Figure()
        self.canvas = backend.FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(1, 1, 1)

        self.line, = self.axes.plot_date(x=[], y=[], xdate=True)
        self.datetime_line = datetime_line.DateTimeLine(self.line)

    def test_get_length_empty(self):
        result = self.datetime_line.length
        self.assertEqual(result, 0,
                         'length not empty')


class TestSetGet(unittest.TestCase):

    def setUp(self):
        self.figure = matplotlib.figure.Figure()
        self.canvas = backend.FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(1, 1, 1)

        self.line, = self.axes.plot_date(x=[], y=[], xdate=True)
        self.datetime_line = datetime_line.DateTimeLine(self.line,
                                                       max_data_length=10)

        t0 = datetime.datetime(2000, 1, 1, 0, 0, 0)
        self.t = [t0 + datetime.timedelta(hours=i) for i in range(10)]
        self.y = [i for i in range(len(self.t))]
        self.datetime_line.x = self.t
        self.datetime_line.y = self.y

    def test_get_length(self):
        result = self.datetime_line.length
        self.assertEqual(result, 10,
                         'length not equal to input length')

    def test_get_max_length(self):
        result = self.datetime_line.max_length
        self.assertEqual(result, 10,
                         'wrong value for max length')

    def test_get_x(self):
        result = self.datetime_line.x
        self.assertEqual(result, self.t,
                         'returned different x')

    def test_get_y(self):
        result = self.datetime_line.y
        self.assertEqual(result, self.y,
                         'returned different y')

    def test_set_x_larger_than_max_length(self):
        self.t.append(datetime.datetime(2000, 1, 2, 0, 0, 0))
        result = False
        try:
            self.datetime_line.x = self.t
        except datetime_line.DateTimeLengthError:
            result = True
        self.assertTrue(result,
                        'DateTimeLengthError not raised')

    def test_set_y_larger_than_max_length(self):
        self.y.append(10)
        result = False
        try:
            self.datetime_line.y = self.y
        except datetime_line.DateTimeLengthError:
            result = True
        self.assertTrue(result,
                        'DateTimeLengthError not raised')

    def test_clear(self):
        self.datetime_line.clear()
        result = self.datetime_line.length
        self.assertEqual(result, 0,
                         'length not zero after clear')

    def test_add_xy(self):
        t1 = datetime.datetime(2000, 1, 2, 0, 0, 0)
        y1 = 10
        self.datetime_line.add_xy(t1, y1)
        new_t = self.datetime_line.x
        new_y = self.datetime_line.y
        self.assertEqual((new_t[-1], new_y[-1]), (t1, y1),
                         'wrong value for added (x,y)')

    def test_add_y(self):
        y1 = 10
        self.datetime_line.add_y(y1)
        new_y = self.datetime_line.y
        self.assertEqual(new_y[-1], y1,
                         'wrong value for added y')


class TestFullArray(unittest.TestCase):

    def setUp(self):
        self.figure = matplotlib.figure.Figure()
        self.canvas = backend.FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(1, 1, 1)

        self.line, = self.axes.plot_date(x=[], y=[], xdate=True)
        self.datetime_line = datetime_line.DateTimeLine(self.line,
                                                       max_data_length=10)

        t0 = datetime.datetime(2000, 1, 1, 0, 0, 0)
        self.t = [t0 + datetime.timedelta(hours=i) for i in range(10)]
        self.y = range(len(self.t))
        self.datetime_line.x = self.t
        self.datetime_line.y = self.y

        self.t1 = self.t[-1] + datetime.timedelta(hours=1)
        self.y1 = 10
        self.datetime_line.add_xy(self.t1, self.y1)

    def test_add_xy_full_array_get_x(self):
        new_t = self.datetime_line.x
        expected_t = numpy.append(numpy.delete(self.t, 0), self.t1)
        result = True
        for i in range(10):
            if not new_t[i] == expected_t[i]:
                result = False
        self.assertTrue(result, 'returned wrong x array')

    def test_add_xy_full_array_get_y(self):
        new_y = self.datetime_line.y
        expected_y = numpy.append(numpy.delete(self.y, 0), self.y1)

        result = True
        for i in range(10):
            if not new_y[i] == expected_y[i]:
                result = False
        self.assertTrue(result, 'returned wrong y array')

    def test_add_xy_full_array_get_length(self):
        result = self.datetime_line.length
        self.assertEqual(result, 10,
                         'length not equal to _max_data_length')


def empty_line_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEmptyLine)
    return suite


def set_get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSetGet)
    return suite


def full_array_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFullArray)
    return suite


def suite():
    suite_list = []
    suite_list.append(empty_line_suite())
    suite_list.append(set_get_suite())
    suite_list.append(full_array_suite())
    return unittest.TestSuite(suite_list)
