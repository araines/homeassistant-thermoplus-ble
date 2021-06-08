[![hacs-badge][hacs-badge]][hacs-link]

***Please note:** I'm recommending that people use ble_monitor (https://github.com/custom-components/ble_monitor) from this point forwards.  The maintainers there have kindly integrated support for Thermoplus sensors as of version 3.1, as well as many other great features!*

# homeassistant-thermoplus-ble

Bluetooth adapter for Home Assistant compatible with Thermoplus (Sensor Blue) BLE thermometers.

This integration listens for the Bluetooth Low Energy packets being constantly emmitted by the sensors and therefore does not increase battery usage of the sensors. The data received includes current temperature, humidity and battery level.

In order to use this integration your host will need Bluetooth 4.0+ capability, either through native hardware (e.g. on the RaspberryPi 4) or through a USB dongle.

## Features

### Supported Sensors

- Smart Hygrometer
  Rounded square body, LCD screen, broadcasts temperature, humidity and battery level.

![Smart Hygrometer][smart-hygrometer-image]

Available under different brands, e.g. [Brifit][smart-hygrometer-link]

- Lanyard Hygrometer

![Lanyard Hygrometer][lanyard-hygrometer-image]

Available under different brands, e.g. [Brifit][lanyard-hygrometer-link]

- Mini Hygrometer

![Mini Hygrometer][mini-hygrometer-image]

Available under different brands, e.g. [Brifit][mini-hygrometer-link]

## Known Issues

- Code isn't well tested at the moment
- Currently does not support humidity

## Troubleshooting

Read [troubleshooting][troubleshooting-link].

## Installation

Use [HACS][hacs-site] to install this integration. If you don't have HACS yet, install that first. Currently you will need to add this as a custom repository.

Once you have installed, restart Home Assistant. Add your configuration (see below), and restart Home Assistant again.

## Configuration

### Example

```yaml
sensor:
  - platform: thermoplus_ble
```

## Using your sensors

Each sensor will show up as an Entity starting "Thermoplus" followed by its unique MAC address.

## Notes

TODO

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-link]: https://github.com/custom-components/hacs
[hacs-site]: https://hacs.xyz/
[smart-hygrometer-image]: https://github.com/araines/homeassistant-thermoplus-ble/raw/master/images/smart-hygrometer.jpg
[smart-hygrometer-link]: https://www.amazon.co.uk/Brifit-Thermometer-Hygrometer-Temperature-Greenhouse/dp/B08BHPS45S
[lanyard-hygrometer-image]: https://github.com/araines/homeassistant-thermoplus-ble/raw/master/images/lanyard-hygrometer.jpg
[lanyard-hygrometer-link]: https://www.amazon.co.uk/Brifit-Thermometer-Hygrometer-Temperature-Notification/dp/B08MBPRMFZ
[mini-hygrometer-image]: https://github.com/araines/homeassistant-thermoplus-ble/raw/master/images/mini-hygrometer.jpg
[mini-hygrometer-link]: https://www.amazon.co.uk/Brifit-Thermometer-Hygrometer-Temperature-Greenhouse/dp/B085C963Y3
[troubleshooting-link]: https://github.com/araines/homeassistant-thermoplus-ble/blob/master/troubleshooting.md
