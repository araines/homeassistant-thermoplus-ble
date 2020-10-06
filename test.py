from struct import pack, unpack
from collections import namedtuple

HCI_EVENT = b'\x04'
LE_ADVERTISING_REPORT = b'\x02'
MAC = b'\x27\x16\x00\x00\x88\x06'

def process(data):
    # Ensure HCI Event Packet
    if data[:1] != HCI_EVENT:
        return None
    # Ensure LE Advertising Report
    if data[3:4] != LE_ADVERTISING_REPORT:
        return None

    # Extract Mac
    mac = data[7:13]
    if mac != MAC:
        return None

    mac = data[7:13]
    mac = pack('<6b', *unpack('>6b', data[7:13]))
    mac = ':'.join('{:02X}'.format(x) for x in data[7:13][::-1]),
    mac = ':'.join(data[7:13][::-1]),
    print(mac)

    # Extract RSSI
    (rssi,) = unpack("<b", data[-1:])

    # Ensure correct packet
    if len(data) != 44:
        return None

    ad_data = data[14:-2]

    # Extract Payload
    Payload = namedtuple('Payload', 'battery temperature humidity')
    #payload = Payload._make(unpack('<HHH', data[33:39]))
    payload = Payload._make(unpack('<HHH', ad_data[19:25]))

    print("mac: %s" % mac)
    print("Payload: %d %.2f %.2f %d" % (payload.battery, payload.temperature/16, payload.humidity/16, rssi))

raw1 = bytes.fromhex('043e29020100002716000088061d0201060302f0ff15ff110000002716000088063c0c8f01a103b9d70300c8')
raw2 = bytes.fromhex('043e2b020100002716000088061f0201060302f0ff17ff11000000271600008806fa019817000054014e730200d6')

process(raw1)
process(raw2)
