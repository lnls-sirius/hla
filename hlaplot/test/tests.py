
import unittest
import test_color_conversion
import test_custom_plot
import test_datetime_plot
import test_position_plot
import test_datetime_line


suite_list = []
suite_list.append(test_color_conversion.suite())
suite_list.append(test_custom_plot.suite())
suite_list.append(test_datetime_plot.suite())
suite_list.append(test_position_plot.suite())
suite_list.append(test_datetime_line.suite())

tests = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(tests)
