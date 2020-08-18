"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
import logging
from time import sleep

from homeassistant.const import (
  DEVICE_CLASS_TEMPERATURE,
  TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity

from bluetooth.ble import DiscoveryService

DOMAIN = "thermoplus_ble" 

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
  """Set up the sensor platform."""
  _LOGGER.debug("Starting")
#  scanner = BLEScanner()
#  hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
#  scanner.start(config)
  svc = DiscoveryService()
  discovery = svc.discover(10)
  for u, n in dev_ble.items():
    print(u, n)
  sleep(1)

class BLEScanner:
  """Bluetooth Low Energy Scanner."""

  dumpthread = None

  def start(self, config):
    """Start scanning for devices."""
    _LOGGER.debug("Starting HCIdump thread")
    self.dumpthread = HCIdump(
      dumplist=self.hcidump_data,
      interface=0,
    )
    self.dumpthread.start()

  def stop(self):
    """Stop scanning for devices."""
    _LOGGER.debug("Stopping HCIdump thread")
    if self.dumpthread is None:
      return True
    if self.dumpthread.isAlive():
      self.dumpthread.join()
      if self.dumpthread.isAlive():
        _LOGGER.error("Waiting for HCIdump thread took too long")
        return False
      else:
        self.dumpthread = None
    return True

  def shutdown_handler(self, event):
    """Shutdown threads."""
    _LOGGER.debug("Shutting down: %s", event)
    self.stop()
    


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
