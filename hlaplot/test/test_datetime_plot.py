
import datetime
import unittest
import matplotlib.dates
import hlaplot.datetime_plot as datetime_plot


class TestScaleBounds(unittest.TestCase):

    def setUp(self):
        self.plot = datetime_plot.DateTimePlot()
        self.plot.show_interval = False
        self.plot.xy_autoscale = True
        self.plot.add_line('line')

        t0 = datetime.datetime(2000, 1, 1, 10)
        self.t = [t0 + datetime.timedelta(hours=i) for i in range(3)]
        self.y = range(len(self.t))
        self.plot.line('line').x = self.t
        self.plot.line('line').y = self.y

    def test_scale_x_bounds_min_one(self):
        self.plot.x_axis_extra_spacing = datetime.timedelta(minutes=30)
        self.plot.update_plot()
        new_min, _ = matplotlib.dates.num2date(self.plot.x_axis)
        tzinfo = new_min.tzinfo
        t_min = datetime.datetime(2000, 1, 1, 9, 30, tzinfo=tzinfo)
        self.assertEqual(new_min, t_min,
                         'wrong value for new minimum')

    def test_scale_x_bounds_max_one(self):
        self.plot.x_axis_extra_spacing = datetime.timedelta(minutes=30)
        self.plot.update_plot()
        _, new_max = matplotlib.dates.num2date(self.plot.x_axis)
        tzinfo = new_max.tzinfo
        t_max = datetime.datetime(2000, 1, 1, 12, 30, tzinfo=tzinfo)
        self.assertEqual(new_max, t_max,
                         'wrong value for new maximum')

    def test_scale_x_bounds_min_two(self):
        delta_t_min = datetime.timedelta(minutes=15)
        delta_t_max = datetime.timedelta(minutes=45)
        self.plot.x_axis_extra_spacing = (delta_t_min, delta_t_max)
        self.plot.x_axis = (self.t[0], self.t[-1])
        self.plot.update_plot()
        new_min, _ = matplotlib.dates.num2date(self.plot.x_axis)
        tzinfo = new_min.tzinfo
        t_min = datetime.datetime(2000, 1, 1, 9, 45, tzinfo=tzinfo)
        self.assertEqual(new_min, t_min,
                         'wrong value for new minimum')

    def test_scale_x_bounds_max_two(self):
        delta_t_min = datetime.timedelta(minutes=15)
        delta_t_max = datetime.timedelta(minutes=45)
        self.plot.x_axis_extra_spacing = (delta_t_min, delta_t_max)
        self.plot.x_axis = (self.t[0], self.t[-1])
        self.plot.update_plot()
        _, new_max = matplotlib.dates.num2date(self.plot.x_axis)
        tzinfo = new_max.tzinfo
        t_max = datetime.datetime(2000, 1, 1, 12, 45, tzinfo=tzinfo)
        self.assertEqual(new_max, t_max,
                         'wrong value for new maximum')

    def test_scale_y_bounds_min(self):
        self.plot.y_axis_extra_spacing = (0.5, 1.0)
        self.plot.y_axis = (self.y[0], self.y[-1])
        self.plot.update_plot()
        new_min, _ = self.plot.y_axis
        self.assertAlmostEqual(new_min, -1.0, 2,
                         'wrong value for new y minimum')

    def test_scale_y_bounds_max(self):
        self.plot.y_axis_extra_spacing = (0.5, 1.0)
        self.plot.y_axis = (self.y[0], self.y[-1])
        self.plot.update_plot()
        _, new_max = self.plot.y_axis
        self.assertAlmostEqual(new_max, 4.0, 2,
                         'wrong value for new y maximum')


def scale_bounds_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScaleBounds)
    return suite


def suite():
    suite_list = []
    suite_list.append(scale_bounds_suite())
    return unittest.TestSuite(suite_list)
