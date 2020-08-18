"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
from homeassistant.const import (
  DEVICE_CLASS_TEMPERATURE,
  TEMP_CELSIUS,
)
import logging
from time import sleep

DOMAIN = "thermoplus_ble" 

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
  """Set up the sensor platform."""
  _LOGGER.debug("Starting")
  scanner = BLEScanner()
  hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
  scanner.start(config)
  sleep(1)

class TemperatureSensor(Entity):
  """Representation of a Temperature Sensor."""

  def __init__(self, mac):
    """Initialize the sensor."""
    self._state = None
    self._unique_id = f"t_{mac}"

  @property
  def name(self):
    """Return the name of the sensor."""
    return f"Thermoplus {self._unique_id}"

  @property
  def state(self):
    """Return the state of the sensor."""
    return self._state

  @property
  def unit_of_measurement(self):
    """Return the unit of measurement."""
    return TEMP_CELSIUS

  @property
  def device_class(self):
    """Return the device class."""
    return DEVICE_CLASS_TEMPERATURE
