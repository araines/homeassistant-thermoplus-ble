# Troubleshooting

## Installation Issues

### Insufficient Python Permissions

Python needs root access to access the HCI interface. If Python doesn't have root access, you may get an error message in Home Assistant similar to this:

```
PermissionError: [Errno 1] Operation not permitted
```

This is usually only needed for alternative installations of Home Assistant that only install Home Assistant core.

To grant Python the capability to access to the HCI interface:

```shell
sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
```

Verify this worked as expected:

```shell
sudo getcap `readlink -f \`which python3\``
```

The command will return the path to Python and looks like (can vary based on your Python version):

```shell
/usr/bin/python3.7 = cap_net_admin,cap_net_raw+eip
```

Ensure you stop and start Home Assisant once complete, restarting Home Assistant is not enough as the python process does not exit upon restart. If in doubt, restart the system.

If you have multiple Python versions, make sure it refers to the same version which is used by Home Assistant. If Home Assistant is using a different version, e.g. python3.6, run the following command to set the correct version (adjust it to your own version if needed).

```shell
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3.6
```

### Incorrect HCI Interface

On systems where multiple HCI interfaces are available, it may be that the default/first interface (0) is not the one you wish to use.

To determine which HCI interface you need, run the following (on the host):

```shell
hcitool dev
```

The command will return the HCI interface number and mac address.

```shell
Devices:
        hci0    B8:27:EB:77:75:50
```

You can configure the HCI interface within the `configuration.yaml`:

```
thermoplus_ble:
  hci_interface: 0

```
