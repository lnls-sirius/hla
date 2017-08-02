"""Test injection class."""
import epics
import unittest
from unittest import mock
from InjectionController import InjectionController


class InjectionControllerTest(unittest.TestCase):
    """Test if injection controller requirements are met."""

    @mock.patch.object(epics.Device, "add_callback", autospec=True)
    @mock.patch.object(epics.Device, "get", autospec=True)
    def setUp(self, mock_get, mock_cb):
        """Executed before every test."""
        self.injection = InjectionController()

    def test_setup(self):
        """Test inital values."""
        self.assertEqual(self.injection.initial_bucket, 1)
        self.assertEqual(
            self.injection.final_bucket, InjectionController.Harmonic)
        self.assertEqual(self.injection.step, 75)
        self.assertEqual(self.injection.mode, InjectionController.MultiBand)
        self.assertEqual(self.injection.cycles, 0)

        # self.assertEqual(self.injection.bucket_list, list())

    def test_set_inital_bucket(self):
        """Set initial bucket to 1."""
        self.injection.initial_bucket = 1
        self.assertEqual(self.injection.initial_bucket, 1)

    def test_set_final_bucket(self):
        """Set final bucket to 500."""
        self.injection.final_bucket = 500
        self.assertEqual(self.injection.final_bucket, 500)

    def test_set_step(self):
        """Set step to 75."""
        self.injection.step = 75
        self.assertEqual(self.injection.step, 75)

    def test_set_injection_mode(self):
        """Set injection mode to single band."""
        self.injection.mode = InjectionController.SingleBand
        self.assertEqual(self.injection.mode, InjectionController.SingleBand)

    def test_set_injection_cycles(self):
        """Set injection cycles to 10."""
        self.injection.cycles = 10
        self.assertEqual(self.injection.cycles, 10)

    def test_build_bucket_list(self):
        """Test building a bucket list."""
        expected_list = [1, 81, 161, 241, 321, 401, 481, 561, 641, 721, 801]

        self.injection.initial_bucket = 1
        self.injection.final_bucket = 864
        self.injection.step = 80

        self.injection._build_bucket_list()

        self.assertEqual(self.injection.bucket_list, expected_list)

    def test_build_bucket_list_with_gap(self):
        """Test building a bucket list with a gap."""
        expected_list = [1, 91, 181, 271, 361, 451, 541]

        self.injection.initial_bucket = 1
        self.injection.final_bucket = 600
        self.injection.step = 90

        self.assertEqual(self.injection.bucket_list, expected_list)

    @mock.patch.object(epics.Device, 'put', autospec=True)
    def test_put_bucket_list(self, mock_put):
        """Test putting bucket list."""
        self.injection._injecting = False
        self.injection.step = 90
        self.injection.put_bucket_list()
        mock_put.assert_called_with(
            self.injection._timing,
            InjectionController.BucketList,
            [1, 91, 181, 271, 361, 451, 541, 631, 721, 811])

    @mock.patch.object(epics.Device, 'put', autospec=True)
    def test_put_injection_mode(self, mock_put):
        """Test putting injection mode."""
        self.injection._injecting = False
        self.injection.put_injection_mode()
        mock_put.assert_called_with(self.injection._timing,
                                    InjectionController.InjectionMode,
                                    self.injection._mode)

    @mock.patch.object(epics.Device, 'put', autospec=True)
    def test_put_cycles(self, mock_put):
        """Test putting cycles."""
        self.injection._injecting = False
        self.injection.put_cycles()
        mock_put.assert_called_with(self.injection._timing,
                                    InjectionController.InjectionCycles,
                                    self.injection._cycles)

    @mock.patch.object(epics.Device, 'put', autospec=True)
    def test_start_injection(self, mock_put):
        """Test start injection command. Explicitly end injection loop."""
        self.injection._injecting = False
        self.injection.start_injection()
        mock_put.assert_called_with(self.injection._timing,
                                    InjectionController.InjectionToggle, 1)

    @mock.patch.object(epics.Device, 'put', autospec=True)
    def test_stop_injection(self, mock_put):
        """Test stop injection behaviour."""
        self.injection.stop_injection()
        mock_put.assert_called_with(self.injection._timing,
                                    InjectionController.InjectionToggle, 0)

    # def test_start_injection_no_connection(self):
    #     """Assert that when there's no connection an exception is raised."""
    #     self.assertRaises(PVConnectionError, self.injection.start_injection)
    #
    # def test_stop_injection_no_connection(self):
    #     """Assert that when there's no connection an exception is raised."""
    #     self.assertRaises(PVConnectionError, self.injection.stop_injection)

    def test_max_current_reached(self):
        """Call stop injection when current is 250."""
        pass


if __name__ == "__main__":
    unittest.main()
