from .deprecate import deprecate
from telegram.contrib.botan import Botan as Bo

Botan = deprecate(Bo, 'telegram.utils.botan', 'telegram.contrib.botan')
