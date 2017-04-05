
import unittest
import hlaplot.color_conversion as color_conversion


MAX_RGB = color_conversion.MAX_RGB


class TestConversion(unittest.TestCase):

    def test_normalize_color_zeros(self):
        result = color_conversion.normalize_color((0, 0, 0, 0))
        self.assertEqual(result, (0.0, 0.0, 0.0, 0.0),
                         'wrong normalization')

    def test_normalize_color_max(self):
        m = MAX_RGB
        result = color_conversion.normalize_color((m, m, m, m))
        self.assertEqual(result, (1.0, 1.0, 1.0, 1.0),
                         'wrong normalization')

    def test_normalize_color(self):
        m = float(MAX_RGB)
        result = color_conversion.normalize_color((55, 153, 202, 4))
        self.assertEqual(result, (55.0/m, 153.0/m, 202.0/m, 4.0/m),
                         'wrong normalization')

    def test_denormalize_color_zeros(self):
        result = color_conversion.denormalize_color((0.0, 0.0, 0.0, 0.0))
        self.assertEqual(result, (0, 0, 0 ,0),
                         'wrong denormalization')

    def test_denormalize_color_max(self):
        m = MAX_RGB
        result = color_conversion.denormalize_color((1.0, 1.0, 1.0, 1.0))
        self.assertEqual(result, (m, m, m, m),
                         'wrong denormalization')

    def test_denormalize_color(self):
        m = MAX_RGB
        result = color_conversion.denormalize_color((0.12, 0.32, 1.00, 0.79))
        expected_result = (round(m * 0.12), round(m * 0.32),
                           round(m * 1.00), round(m * 0.79))
        self.assertEqual(result, expected_result,
                         'wrong denormalization')

    def test_normalize_out_of_range_negative(self):
        self.assertRaises(color_conversion.RgbRangeException,
                          color_conversion.normalize_color,
                          (0, 0, -1, 0))

    def test_normalize_out_of_range_positive(self):
        w = MAX_RGB + 1
        self.assertRaises(color_conversion.RgbRangeException,
                          color_conversion.normalize_color,
                          (0, w, 0, 0))

    def test_denormalize_out_of_range_negative(self):
        self.assertRaises(color_conversion.RgbRangeException,
                          color_conversion.denormalize_color,
                          (0.0, 0.0, -0.1, 0.0))

    def test_denormalize_out_of_range_positive(self):
        self.assertRaises(color_conversion.RgbRangeException,
                          color_conversion.denormalize_color,
                          (0.0, 1.1, 0.0, 0.0))

    def test_normalize_color_string_equal(self):
        s_in = 'string'
        s_out = color_conversion.normalize_color(s_in)
        self.assertTrue(s_out == s_in,
                        'output string not equal to input')

    def test_denormalize_color_string_equal(self):
        s_in = 'string'
        s_out = color_conversion.denormalize_color(s_in)
        self.assertTrue(s_out == s_in,
                        'output string not equal to input')


class TestReturnType(unittest.TestCase):

    def test_normalize_color_tuple(self):
        t_in = (0, 50, 100, 150)
        t_out = color_conversion.normalize_color(t_in)
        self.assertTrue(isinstance(t_out, tuple),
                        'tuple not returned')

    def test_normalize_color_string_type(self):
        s_in = 'string'
        s_out = color_conversion.normalize_color(s_in)
        self.assertTrue(isinstance(s_out, str),
                        'string not returned')

    def test_denormalize_color_tuple(self):
        t_in = (0.0, 0.2, 0.4, 0.8)
        t_out = color_conversion.denormalize_color(t_in)
        self.assertTrue(isinstance(t_out, tuple),
                        'tuple not returned')

    def test_denormalize_color_string_type(self):
        s_in = 'string'
        s_out = color_conversion.denormalize_color(s_in)
        self.assertTrue(isinstance(s_out, str),
                        'string not returned')


def conversion_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConversion)
    return suite


def return_type_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReturnType)
    return suite


def suite():
    suite_list = []
    suite_list.append(conversion_suite())
    suite_list.append(return_type_suite())
    return unittest.TestSuite(suite_list)
