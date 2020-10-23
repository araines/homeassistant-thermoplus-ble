"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
import asyncio
from collections import namedtuple
from datetime import timedelta
import logging
import struct
from time import sleep
from threading import Thread

import aioblescan as aiobs

from homeassistant.const import (
  DEVICE_CLASS_TEMPERATURE,
  TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util import dt

DOMAIN = "thermoplus_ble" 
HCI_EVENT = b'\x04'
LE_ADVERTISING_REPORT = b'\x02'

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
  """Set up the sensor platform."""
  _LOGGER.debug("Starting")
  scanner = BLEScanner()
  processor = Processor(hass, scanner, add_entities)
  hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
  scanner.start()
  sleep(1)
  processor.update(dt.utcnow())
  return True

class ScannerThread(Thread):
  """Scanner Thread."""

  def __init__(self, hci_events, interface=0):
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

  def start(self):
    """Start scanning for devices."""
    _LOGGER.debug("Starting scanner thread")
    self.hci_events.clear()
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

class Processor:
  """Bluetooth data processor."""

  def __init__(self, hass, scanner, add_entities, period=60):
    self._hass = hass
    self._scanner = scanner
    self._add_entities = add_entities
    self._period = period
    self._sensors = {}

  def update(self, now):
    """Schedule & process the scanner data."""
    _LOGGER.debug("Update")
    try:
      self.process()
    except RuntimeError as error:
      _LOGGER.error("Error updating BLE data: %s", error)
    track_point_in_utc_time(
      self._hass, self.update, dt.utcnow() + timedelta(seconds=self._period)
    )

  def process(self):
    _LOGGER.debug("Processing scanner data")
    stopped = self._scanner.stop()
    if stopped is False:
      _LOGGER.error("Scanner thread did not stop, aborting data processing")
      return []
    events = [*self._scanner.hci_events] # fastest way to copy to minimise delay
    self._scanner.start()
    _LOGGER.info("%d HCI events received", len(events))
    for event in events:
      data = self.parse_event(event)
      if data is None:
        continue
      _LOGGER.debug("Processing: %s", data)
      sensor_data = self.parse_sensor(data)
      if sensor_data is None:
        continue
      mac = sensor_data.get('mac')
      if mac not in self._sensors:
        _LOGGER.info("Creating sensor: %s", sensor_data)
        # create
        sensor = TemperatureSensor(mac)
        self._sensors[mac] = sensor
      sensor = self._sensors.get(mac)
      _LOGGER.info("Update sensor data: %s", sensor_data)
      sensor.update_temp(sensor_data.get('temperature'))
      self._add_entities(list(self._sensors.values()))
    _LOGGER.info("%d known sensors", len(self._sensors))

  def parse_event(self, event):
    # Ensure HCI Event packet
    if event[:1] != HCI_EVENT:
      return None
    # Ensure LE Advertising Report
    if event[3:4] != LE_ADVERTISING_REPORT:
      return None
    # Extract mac and rssi
    reversed_mac = event[7:13]
    mac = ':'.join('{:02X}'.format(x) for x in reversed_mac[::-1])
    (rssi,) = struct.unpack("<b", event[-1:])
    # Extract advertising data
    advertising_data = event[14:-2]
    return {
      "mac": mac,
      "rssi": rssi,
      "data": advertising_data,
    }

  def parse_sensor(self, data):
    advertising_data = data.get('data')
    _LOGGER.debug("Advertising data length: %d", len(advertising_data))
    if len(advertising_data) != 28:
      return None
    Payload = namedtuple('Payload', 'battery temperature humidity')
    payload = Payload._make(struct.unpack('<HHH', advertising_data[19:25]))
    return {
      "mac": data.get('mac'),
      "rssi": data.get('rssi'),
      "battery": "%d" % payload.battery,
      "temperature": "%.2f" % (payload.temperature / 16),
      "humidity": "%.2f" % (payload.humidity / 16),
    }


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

  def update_temp(self, temp):
    """Update the temperature."""
    self._state = temp
