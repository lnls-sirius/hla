"""Define a class to control the injection.

The controller can:
    start the injection
    end the injection
For this, parameters such as inital bucket, final bucket, injection step,
injection mode and number of injections are used to configure the injection
behaviour.
"""

import epics
import threading
from CustomExceptions import PVConnectionError


class InjectionController:
    """Class that controls the injection."""

    SingleBunch, MultiBunch = range(2)
    MultiBunchSpan = 75
    Harmonic = 864
    MaxCurrent = 250

    TimingPrefix = "VAG-AS-Glob:TI-EVG"
    LifeTimePrefix = "lifetime"

    # Timing Attrs
    BucketList = "BucketList-SP"
    InjectionToggle = "InjectionState-Sel"
    InjectionMode = "InjectionMode"
    InjectionCycles = "InjectionCycles"

    TimingAttrs = (BucketList, InjectionToggle, InjectionMode, InjectionCycles)

    # Lifetime Attrs
    Current = "current"

    def __init__(self):
        """Class constructor."""
        self._mode = InjectionController.MultiBunch
        self._initial_bucket = 1
        self._final_bucket = InjectionController.Harmonic
        self._step = 75
        self._cycles = 0

        self._bucket_list = list()

        # try connecting
        self._timing = epics.Device(self.TimingPrefix, delim=':',
                                    attrs=self.TimingAttrs)
        self._lifetime = epics.Device(self.LifeTimePrefix, delim=':',
                                      attrs='')

        # add injection status callback
        self._timing.add_callback(self.InjectionToggle, self._injection_status)

        self._injecting = self._timing.get(self.InjectionToggle)

    # Public methods
    def put_bucket_list(self):
        """Set bucket list via epics."""
        if self._injecting:
            return
        self._put(self._timing, self.BucketList, self.bucket_list)

    def put_injection_mode(self):
        """Set injection mode via epics."""
        if self._injecting:
            return
        self._put(self._timing, self.InjectionMode, self._mode)

    def put_cycles(self):
        """Set cycles via epics."""
        if self._injecting:
            return
        self._put(self._timing, self.InjectionCycles, self._cycles)

    def start_injection(self):
        """Communicate with timing system to start injecting."""
        if self._injecting:
            return
        self._put(self._timing, self.InjectionToggle, 1)

    def stop_injection(self):
        """Communicate with timing system to stop injecting."""
        self._put(self._timing, self.InjectionToggle, 0)

    # Private methods
    def _put(self, device, attr, value):
        if device.put(attr, value) is None:
            raise PVConnectionError(
                "Connection with '{}' PV failed".format(attr))

    def _build_bucket_list(self):
        """Build bucket list based on initial, final buckets and step."""
        self._bucket_list.clear()
        steps = range(self._initial_bucket, self._final_bucket + 1, self._step)
        for i in steps:
            self._bucket_list.append(i)

    def _injection_status(self, pvname, value, **kwargs):
        """CA callback."""
        self._injecting = value

    def _current_value(self, pvname, value, **kwargs):
        if value == self.MaxCurrent:
            t = threading.Thread(target=self.stop_injection())
            t.start()

    # Properties getters and setters
    @property
    def mode(self):
        """Mode getter."""
        return self._mode

    @mode.setter
    def mode(self, value):
        if value in range(2):
            self._mode = value

    @property
    def initial_bucket(self):
        """Initial bucket getter."""
        return self._initial_bucket

    @initial_bucket.setter
    def initial_bucket(self, value):
        self._initial_bucket = value

    @property
    def final_bucket(self):
        """Final bucket getter."""
        return self._final_bucket

    @final_bucket.setter
    def final_bucket(self, value):
        self._final_bucket = value

    @property
    def step(self):
        """Step getter."""
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def cycles(self):
        """Cycle getter."""
        return self._cycles

    @cycles.setter
    def cycles(self, value):
        self._cycles = value

    @property
    def bucket_list(self):
        """Bucket list getter."""
        self._build_bucket_list()
        return self._bucket_list

    @bucket_list.setter
    def bucket_list(self, values):
        raise AttributeError("Bucket list does not support assignment.")

    @property
    def injecting(self):
        """Return injection status."""
        return self._injecting
