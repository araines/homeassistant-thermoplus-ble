"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
import asyncio
import logging
from time import sleep
from threading import Thread

import aioblescan as aiobs

from homeassistant.const import (
  DEVICE_CLASS_TEMPERATURE,
  TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity

DOMAIN = "thermoplus_ble" 

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
  """Set up the sensor platform."""
  _LOGGER.debug("Starting")
  scanner = BLEScanner()
  hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
  scanner.start(config)
  sleep(1)

class ScannerThread(Thread):
  """Scanner Thread."""

  def __init(self, hci_events, interface=0):
    """Initiate scanner thread."""
    Thread.__init__(self)
    _LOGGER.debug("Scanner thread: init")
    self._hci_events = hci_events
    self._interface = interface
    self._event_loop = None

  def run(self):
    """Run scanner thread."""
    _LOGGER.debug("Scanner thread: run")
    try:
      socket = aiobs.create_bt_socket(self._interface)
    except OSError as error:
      _LOGGER.error("Scanner thread: OS error: %s", error)
      return

    _LOGGER.debug("Scanner thread: creating connection")
    self._event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self._event_loop)
    fac = self._event_loop._create_connection_transport(
      socket, aiobs.BLEScanRequester, None, None)
    conn, btctrl = self._event_loop.run_until_complete(fac)
    _LOGGER.debug("Scanner thread: connection established")

    btctrl.process = self.process_events
    btctrl.send_scan_request()
    _LOGGER.debug("Scanner thread: start event loop")
    try:
      self._event_loop.run_forever()
    finally:
      _LOGGER.debug("Scanner thread: event loop stopped, cleaning up")
      btctrl.stop_scan_request()
      conn.close()
      self._event_loop.run_until_complete(asyncio.sleep(0))
      self._event_loop.close()
      _LOGGER.debug("Scanner thread: Run finished")

  def join(self, timeout=10):
    """Join scanner thread."""
    _LOGGER.debug("Scanner thread: join")
    try:
      self._event_loop.call_soon_threadsafe(
        self._event_loop.stop
      )
    except AttributeError as error:
      _LOGGER.debug("%s", error)
    finally:
      Thread.join(self, timeout)
      _LOGGER.debug("Scanner thread: joined")

  def process_events(self, data):
    """Collect HCI events."""
    self._hci_events.append(data)

class BLEScanner:
  """Bluetooth Low Energy Scanner."""

  hci_events = []
  thread = None

  def start(self, config):
    """Start scanning for devices."""
    _LOGGER.debug("Starting scanner thread")
    self.thread = ScannerThread(
      hci_events=self.hci_events,
    )
    self.thread.start()

  def stop(self):
    """Stop scanning for devices."""
    _LOGGER.debug("Stopping scanner thread")
    if self.thread is None:
      return True
    if self.thread.isAlive():
      self.thread.join()
      if self.thread.isAlive():
        _LOGGER.error("Waiting for scanner thread took too long")
        return False
      else:
        self.thread = None
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
