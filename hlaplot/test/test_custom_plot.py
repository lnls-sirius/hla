
import unittest
import hlaplot.custom_plot as custom_plot


class TestDefaults(unittest.TestCase):

    def setUp(self):
        self.plot = custom_plot.CustomPlot()

    def test_default_background_color(self):
        color = custom_plot.DEFAULT_BACKGROUND_COLOR
        self.assertEqual(self.plot.background_color, color,
                         'background color not set to default')

    def test_default_axis_background_color(self):
        color = custom_plot.DEFAULT_AXIS_BACKGROUND_COLOR
        self.assertEqual(self.plot.axis_background_color, color,
                         'axis background color not set to default')

    def test_default_axis_elements_color(self):
        color = custom_plot.DEFAULT_AXIS_ELEMENTS_COLOR
        self.assertEqual(self.plot.axis_elements_color, color,
                         'axis elements color not set to default')


class TestScaleBounds(unittest.TestCase):

    def setUp(self):
        self.plot = custom_plot.CustomPlot()
        self.plot.add_line('line')
        self.plot.line('line').x = [-1, 4]
        self.plot.line('line').y = [-2, 3]


    def test_scale_x_bounds_min(self):
        self.plot.x_axis_extra_spacing = (0.5, 1.5)
        self.plot.update_plot()
        axis_min, _ = self.plot.x_axis
        self.assertAlmostEqual(axis_min, -3.5, 2,
                         'wrong value for new axis bound')

    def test_scale_x_bounds_max(self):
        self.plot.x_axis_extra_spacing = (0.5, 1.5)
        self.plot.update_plot()
        _, axis_max = self.plot.x_axis
        self.assertAlmostEqual(axis_max, 11.5, 2,
                         'wrong value for new axis bound')

    def test_scale_y_bounds_min(self):
        self.plot.y_axis_extra_spacing = (0.5, 1.5)
        self.plot.update_plot()
        axis_min, _ = self.plot.y_axis
        self.assertAlmostEqual(axis_min, -4.5, 2,
                         'wrong value for new axis bound')

    def test_scale_y_bounds_max(self):
        self.plot.y_axis_extra_spacing = (0.5, 1.5)
        self.plot.update_plot()
        _, axis_max = self.plot.y_axis
        self.assertAlmostEqual(axis_max, 10.5, 2,
                         'wrong value for new axis bound')


class TestScaleBoundsEmpty(unittest.TestCase):

    def setUp(self):
        self.plot = custom_plot.CustomPlot()
        self.plot.add_line('line')

    def test_scale_x_bounds_empty(self):
        self.plot.update_plot()
        axis_bounds = self.plot.x_axis
        self.assertEqual(axis_bounds, (0.0, 1.0),
                         'default bounds not set for empty axis data')

    def test_scale_y_bounds_empty(self):
        self.plot.update_plot()
        axis_bounds = self.plot.y_axis
        self.assertEqual(axis_bounds, (0.0, 1.0),
                         'default bounds not set for empty axis data')


def defaults_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDefaults)
    return suite


def scale_bounds_empty_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScaleBoundsEmpty)
    return suite


def scale_bounds_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScaleBounds)
    return suite


def suite():
    suite_list = []
    suite_list.append(defaults_suite())
    suite_list.append(scale_bounds_suite())
    return unittest.TestSuite(suite_list)
