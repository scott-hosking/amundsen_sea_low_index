"""Amundsen Sea Low detection from mean sea level pressure fields."""

# Import the asli class here for nicer namespace
from .asli import ASLICalculator

from . import data, plot, utils

from .params import CALCULATION_VERSION, ASL_REGION, SOFTWARE_VERSION

import os, logging
logging.getLogger("asli").addHandler(logging.NullHandler())
logging.basicConfig(level=os.environ.get('ASLI_LOGLEVEL', 'INFO').upper())
