"""Thermoplus Bluetooth (BLE) hydrometer / thermometer sensor integration."""
from collections import namedtuple
from datetime import timedelta
import logging
import struct
from time import sleep

from homeassistant.const import (
  ATTR_BATTERY_LEVEL,
  DEVICE_CLASS_TEMPERATURE,
  TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util import dt

from .ble import BLEScanner

DOMAIN = "thermoplus_ble"
HCI_EVENT = b'\x04'
LE_ADVERTISING_REPORT = b'\x02'
TYPE_DEVICE_NAME = b'\x09'
TYPE_MANUFACTURER_SPECIFIC = b'\xff'
DEVICE_NAME = "ThermoBeacon"

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

    # Work through events
    for event in events:
      data = self.parse_event(event)
      if data is None:
        continue
      _LOGGER.debug("Processing: %s", data)

      self.find_new_sensors(data)

      if data.get('mac') not in self._sensors:
        continue

      sensor_data = self.parse_sensor(data)
      if sensor_data is None:
        continue
      mac = sensor_data.get('mac')
      sensor = self._sensors.get(mac)
      _LOGGER.info("Update sensor data: %s", sensor_data)
      sensor.update_data(sensor_data)
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
    # Extract advertising data & entries
    advertising_data = event[14:-2]
    entries = []
    while (len(advertising_data) > 0):
        (length,) = struct.unpack("<b", advertising_data[0:1])
        data_type = advertising_data[1:2]
        end = length + 1
        entries.append({
          'data_type': data_type,
          'length': length,
          'value': advertising_data[2:end],
        })
        advertising_data = advertising_data[end:]

    return {
      "mac": mac,
      "rssi": rssi,
      "entries": entries,
    }

  def find_new_sensors(self, data):
    for entry in data.get('entries'):
      if entry.get('data_type') != TYPE_DEVICE_NAME:
        continue
      if entry.get('value').decode('utf-8') != DEVICE_NAME:
        continue
      mac = data.get('mac')
      if mac not in self._sensors:
        _LOGGER.info("Found new %s sensor at %s", DEVICE_NAME, mac)
        sensor = TemperatureSensor(mac)
        self._sensors[mac] = sensor
        self._add_entities([sensor])

  def parse_sensor(self, data):
    for entry in data.get('entries'):
      if entry.get('data_type') != TYPE_MANUFACTURER_SPECIFIC:
        continue
      value = entry.get('value')
      if len(value) != 19:
        continue
      Payload = namedtuple('Payload', 'battery temperature humidity')
      payload = Payload._make(struct.unpack('<HHH', value[10:16]))
      return {
        "mac": data.get('mac'),
        "rssi": data.get('rssi'),
        "battery": int("%d" % payload.battery),
        "temperature": float("%.2f" % (payload.temperature / 16)),
        "humidity": float("%.2f" % (payload.humidity / 16)),
      }
    return None


class TemperatureSensor(Entity):
  """Representation of a Temperature Sensor."""

  def __init__(self, mac):
    """Initialize the sensor."""
    self._state = None
    self._mac = mac
    self._unique_id = f"t_{mac}"
    self._data = {}

  def update_data(self, data):
    """Update the sensor data."""
    self._data = data

  @property
  def unique_id(self):
    """Return the unique id."""
    return self._unique_id

  @property
  def name(self):
    """Return the name of the sensor."""
    return f"Thermoplus {self._mac}"

  @property
  def state(self):
    """Return the state of the sensor."""
    return self._data.get('temperature')

  @property
  def unit_of_measurement(self):
    """Return the unit of measurement."""
    return TEMP_CELSIUS

  @property
  def device_class(self):
    """Return the device class."""
    return DEVICE_CLASS_TEMPERATURE

  @property
  def device_info(self):
    return {
      "identifiers": {
          # Serial numbers are unique identifiers within a specific domain
          (DOMAIN, self.unique_id)
      },
      "name": self.name,
      "manufacturer": "Thermoplus",
      "via_device": (DOMAIN, self._mac),
    }

  def _get_battery_level(self):
    voltage = self._data.get('battery', 0)
    if voltage >= 3000:
      return 100
    elif voltage >= 2800:
      return 80
    elif voltage >= 2600:
      return 60
    elif voltage >= 2500:
      return 40
    elif voltage >= 2450:
      return 20
    else:
      return 0

  @property
  def device_state_attributes(self):
    """Return the state attributes."""
    return {
      **self._data,
      ATTR_BATTERY_LEVEL: self._get_battery_level(),
    }
