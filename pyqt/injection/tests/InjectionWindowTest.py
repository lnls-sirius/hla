"""Test Injection window."""
import sys
import unittest
# import threading
import time
from unittest import mock
from unittest.mock import create_autospec
from InjectionWindow import InjectionWindow
from InjectionController import InjectionController
from pydm import PyDMApplication
# from PyQt5.QtTest import QTest

app = PyDMApplication(None, sys.argv)


class InjectionWindowTest(unittest.TestCase):
    """Test injection window behaviour."""

    def setUp(self):
        """Common setup for all tests."""
        self.mock_controller = create_autospec(InjectionController)
        self.form = InjectionWindow(self.mock_controller)

    def test_setup(self):
        """Test initial values."""
        self.assertEqual(self.form.multiBandRadio.isChecked(), True)
        self.assertEqual(self.form.singleBandRadio.isChecked(), False)
        self.assertEqual(self.form.initialBucketSpinBox.value(), 1)
        self.assertEqual(self.form.finalBucketSpinBox.value(),
                         InjectionController.Harmonic)
        self.assertEqual(self.form.stepSpinBox.value(), 75)
        self.assertEqual(self.form.cycleSpinBox.value(), 1)

    @mock.patch.object(InjectionWindow, 'setInjectionMode', autospec=True)
    def test_set_injection_mode(self, window_mock):
        """Test injection mode radios."""
        self.form.singleBandRadio.click()
        self.assertEqual(self.form.multiBandRadio.isChecked(), False)
        self.assertEqual(self.form.singleBandRadio.isChecked(), True)
        window_mock.assert_called_with(
            self.form, self.mock_controller.SingleBand)
        self.form.multiBandRadio.click()
        self.assertEqual(self.form.multiBandRadio.isChecked(), True)
        self.assertEqual(self.form.singleBandRadio.isChecked(), False)
        window_mock.assert_called_with(
            self.form, self.mock_controller.MultiBand)

    @mock.patch.object(InjectionWindow, "_setBucketProfile", autospec=True)
    def test_set_initial_bucket(self, window_mock):
        """Test set intial bucket value."""
        self.form.initialBucketSpinBox.setValue(40)
        self.assertEqual(self.form.initialBucketSpinBox.value(), 40)
        window_mock.assert_called_with(self.form)

    @mock.patch.object(InjectionWindow, "_setBucketProfile", autospec=True)
    def test_set_final_bucket(self, window_mock):
        """Test set final bucket value."""
        self.form.finalBucketSpinBox.setValue(800)
        self.assertEqual(self.form.finalBucketSpinBox.value(), 800)
        window_mock.assert_called_with(self.form)

    @mock.patch.object(InjectionWindow, "_setBucketProfile", autospec=True)
    def test_set_step(self, window_mock):
        """Test set step."""
        self.form.stepSpinBox.setValue(90)
        self.assertEqual(self.form.stepSpinBox.value(), 90)
        window_mock.assert_called_with(self.form)

    def test_set_cycles(self):
        """Test setting number of cycles."""
        self.form.cycleSpinBox.setValue(10)
        self.assertEqual(self.form.cycleSpinBox.value(), 10)

    # @mock.patch.object(InjectionWindow, '_startInjection', autospec=True)
    # def test_accept_start_injection(self, mock_injection):
    #     """Test clicking button to start injection and accept it."""
    #     self.mock_controller.injecting = False
    #     self.assertIsNone(self.form._dialog)
    #
    #     t = threading.Thread(target=self._accept_dialog)
    #     t.start()
    #     self.form.startInjectionBtn.click()
    #
    #     mock_injection.assert_called_with(self.form)
    #     # self.assertIsNone(self.form._dialog)

    # @mock.patch.object(InjectionWindow, '_startInjection', autospec=True)
    # def test_reject_start_injection(self, mock_injection):
    #     """Test clicking button to start injection and rejecting it."""
    #     self.mock_controller.injecting = False
    #     self.assertIsNone(self.form._dialog)
    #
    #     t = threading.Thread(target=self._reject_dialog)
    #     t.start()
    #     self.form.startInjectionBtn.click()
    #
    #     mock_injection.assert_not_called()
    #     # self.assertIsNone(self.form._dialog)

    # @mock.patch.object(InjectionWindow, '_stopInjection', autospec=True)
    # def test_accept_stop_injection(self, mock_injection):
    #     """Test clicking button to stop injection and accepting it."""
    #     self.mock_controller.injecting = True
    #     self.assertIsNone(self.form._dialog)
    #
    #     t = threading.Thread(target=self._accept_dialog)
    #     t.start()
    #     self.form.stopInjectionBtn.click()
    #
    #     mock_injection.assert_called_with(self.form)
    #     # self.assertIsNone(self.form._dialog)

    # @mock.patch.object(InjectionWindow, '_stopInjection', autospec=True)
    # def test_reject_stop_injection(self, mock_injection):
    #     """Test clicking button to stop injection and rejecting."""
    #     self.form.controller._injecting = True
    #     self.assertIsNone(self.form._dialog)
    #
    #     t = threading.Thread(target=self._reject_dialog)
    #     t.start()
    #     self.form.stopInjectionBtn.click()
    #
    #     mock_injection.assert_not_called()
    #     # self.assertIsNone(self.form._dialog)

    def _accept_dialog(self):
        time.sleep(0.2)
        # self.assertIsNotNone(self.form._dialog)
        self.form._dialog.accept()

    def _reject_dialog(self):
        time.sleep(0.2)
        # self.assertIsNotNone(self.form._dialog)
        self.form._dialog.reject()


if __name__ == "__main__":
    unittest.main()
