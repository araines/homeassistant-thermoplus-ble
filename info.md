[![hacs-badge][hacs-badge]][hacs-link]

# homeassistant-thermoplus-ble
Bluetooth adapter for Home Assistant compatible with Thermoplus (Sensor Blue) BLE thermometers.

This integration listens for the Bluetooth Low Energy packets being constantly emmitted by the sensors and therefore does not increase battery usage of the sensors.  The data received includes current temperature, humidity and battery level.

## Features

### Supported Sensors

- Smart Hygrometer
Rounded square body, LCD screen, broadcasts temperature, humidity and battery level.

![Smart Hygrometer][smart-hygrometer-image]

Available under different brands, e.g. [Brifit][smart-hygrometer-link]


## Known Issues

- Code isn't well tested at the moment
- Picks up more than just Thermoplus / ThermoBeacon sensors resulting in garbage data
- Currently does not support humidity
- Currently does not support battery level
- No way to map known sensors to "friendly" names

## Troubleshooting

Please raise a GitHub issue if you are experience issues with your sensors or have a different sensor type you would like supported.

## Installation

Use [HACS][hacs-site] to install this integration.  If you don't have HACS yet, install that first.  Currently you will need to add this as a custom repository.

Once you have installed, restart Home Assistant.  Add your configuration (see below), and restart Home Assistant again.

## Configuration

### Example

```yaml
sensor:
  - platform: thermoplus_ble
```

## Notes

TODO

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-link]: https://github.com/custom-components/hacs
[hacs-site]: https://hacs.xyz/
[smart-hygrometer-image]: https://github.com/araines/homeassistant-thermoplus-ble/raw/master/images/smart-hygrometer.jpg
[smart-hygrometer-link]: https://www.amazon.co.uk/Brifit-Thermometer-Hygrometer-Temperature-Greenhouse/dp/B08BHPS45S
