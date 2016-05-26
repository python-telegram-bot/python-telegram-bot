from .deprecate import deprecate
from telegram.ext.botan import Botan as Bo

Botan = deprecate(Bo, 'telegram.utils.botan', 'telegram.ext.botan')
