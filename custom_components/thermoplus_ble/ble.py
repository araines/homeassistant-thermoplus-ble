"""Bluetooth Low Energy Scanner."""
import asyncio
import logging
import struct
from collections import namedtuple
from datetime import timedelta
from threading import Thread
from time import sleep

import aioblescan as aiobs
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util import dt

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

HCI_EVENT = b'\x04'
LE_ADVERTISING_REPORT = b'\x02'

class BLEActiveScanRequester(aiobs.BLEScanRequester):
  """Active scanning version of the BLEScanRequester"""

  def connection_made(self, transport):
        self.transport = transport
        command=aiobs.HCI_Cmd_LE_Set_Scan_Params(0x1)
        self.transport.write(command.encode())

class BLEScanner:
  """Bluetooth Low Energy Scanner."""

  hci_events = []
  thread = None

  def __init__(self, interface):
    self._interface = interface

  def start(self):
    """Start scanning for devices."""
    _LOGGER.info("Starting scanner thread on interface %s", self._interface)
    self.hci_events.clear()
    self.thread = ScannerThread(
      hci_events=self.hci_events,
      interface=self._interface,
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
      socket, BLEActiveScanRequester, None, None)
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
