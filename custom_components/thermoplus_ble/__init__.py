"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .ble import BLEScanner
from .const import DOMAIN, CONF_PERIOD, DEFAULT_PERIOD

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            {
                vol.Required(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
            },
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up the Thermoplus BLE component."""
    if config.get(DOMAIN) is not None:
        period = config[DOMAIN].get(CONF_PERIOD)

    hass.data[DOMAIN] = {
        "ble": BLEScanner(),
    }

    return True
