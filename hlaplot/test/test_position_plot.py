
import unittest
import hlaplot.position_plot as position_plot


class TestInit(unittest.TestCase):

    def test_init_wrong_interval_bounds(self):
        args = {}
        args['interval_min'] = 1
        args['interval_max'] = 0
        self.assertRaises(position_plot.IntervalBoundsError,
                          position_plot.PositionPlot,
                          **args)


class TestDefineTicks(unittest.TestCase):

    def setUp(self):
        self.plot = position_plot.PositionPlot()

    def test_define_ticks_different_lengths(self):
        names = ['a', 'b']
        pos = [0.0]
        self.assertRaises(position_plot.LengthError,
                          self.plot.define_ticks,
                          names, pos)

    def test_define_and_get_ticks(self):
        ticks = {'a': 0.0, 'b': 1.0}
        names = ticks.keys()
        pos = ticks.values()
        self.plot.define_ticks(names, pos)
        result = self.plot.ticks
        self.assertEqual(result, ticks,
                         'set ticks not returned')


class TestSelectTicks(unittest.TestCase):

    def setUp(self):
        self.plot = position_plot.PositionPlot()
        self.names = ['a', 'b']
        pos = [0.0, 1.0]
        self.plot.define_ticks(self.names, pos)

    def test_select_ticks_wrong_name(self):
        self.names.append('c')
        self.assertRaises(KeyError,
                          self.plot.select_ticks,
                          self.names)

    def test_select_and_get_ticks(self):
        self.plot.select_ticks(self.names)
        result = self.plot.selected_ticks
        self.assertEqual(result, self.names,
                         'selected ticks not returned')


class TestInterval(unittest.TestCase):

    def setUp(self):
        self.plot = position_plot.PositionPlot(interval_min=0.0,
                                              interval_max=1.0)

    def test_scale_x_bounds(self):
        self.plot.update_plot()
        min_, max_ = self.plot.x_axis
        self.assertEqual((min_, max_), (0.0, 1.0),
                         'wrong value for x bounds')

    def test_scale_x_bounds_with_extra_spacing(self):
        self.plot.x_axis_extra_spacing = 1.0
        self.plot.update_plot()
        min_, max_ = self.plot.x_axis
        self.assertEqual((min_, max_), (-1.0, 2.0),
                         'wrong value for x bounds with extra spacing')


def init_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    return suite


def define_ticks_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDefineTicks)
    return suite


def select_ticks_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSelectTicks)
    return suite


def interval_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInterval)
    return suite


def suite():
    suite_list = []
    suite_list.append(init_suite())
    suite_list.append(define_ticks_suite())
    suite_list.append(select_ticks_suite())
    suite_list.append(interval_suite())
    return unittest.TestSuite(suite_list)
