import numpy as np
from qtpy.QtCore import Slot
from pydm.widgets import PyDMImageView


class PyDMImageViewBase(PyDMImageView):

    @Slot(np.ndarray)
    def image_value_changed(self, image):
        if isinstance(image, np.ndarray):
            super().image_value_changed(image)