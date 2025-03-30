"""Init file"""

from importlib.metadata import version

from .protocol import *
from .utils import *
from .general import *
from .low_level import *
from .mid_level import *
from .dyscom import *

from .device import Device
from .layer import Layer
from .device_p24 import DeviceP24
from .device_i24 import DeviceI24

__version__ = version("science_mode_4")
