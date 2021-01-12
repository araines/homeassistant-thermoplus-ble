"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .ble import BLEScanner
from .const import DOMAIN, CONF_HCI_INTERFACE, CONF_HCI_DUMP, DEFAULT_HCI_INTERFACE, DEFAULT_HCI_DUMP

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            {
                vol.Optional(CONF_HCI_INTERFACE, default=DEFAULT_HCI_INTERFACE): cv.positive_int,
                vol.Optional(CONF_HCI_DUMP, default=DEFAULT_HCI_DUMP): cv.boolean,
            },
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up the Thermoplus BLE component."""
    if DOMAIN not in config:
        hass.data[DOMAIN] = {
            CONF_HCI_INTERFACE: DEFAULT_HCI_INTERFACE,
            CONF_HCI_DUMP: DEFAULT_HCI_DUMP,
        }
    else:
        hass.data[DOMAIN] = {
            CONF_HCI_INTERFACE: config[DOMAIN].get(CONF_HCI_INTERFACE),
            CONF_HCI_DUMP: config[DOMAIN].get(CONF_HCI_DUMP),
        }

    return True
