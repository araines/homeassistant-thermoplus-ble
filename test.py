from struct import pack, unpack
from collections import namedtuple

HCI_EVENT = b'\x04'
LE_ADVERTISING_REPORT = b'\x02'
MAC = b'\x27\x16\x00\x00\x88\x06'

TYPE_DEVICE_NAME = b'\x09'
TYPE_MANUFACTURER_SPECIFIC = b'\xFF'

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
    print(mac)

    # Extract RSSI
    (rssi,) = unpack("<b", data[-1:])

    # Extract Advertising Data
    ad_data = data[14:-2]

    entries = []

    while (len(ad_data) > 0):
        (length, ) = unpack("<b", ad_data[0:1])
        data_type = ad_data[1:2]
        end = length + 1
        entries.append({
          'data_type': data_type,
          'length': length,
          'value': ad_data[2:end],
        })
        ad_data = ad_data[end:]

    print(entries)

    for entry in entries:
        if entry.get('data_type') == TYPE_DEVICE_NAME:
            device_name = entry.get('value')
            print(device_name.decode('utf-8'))
        if entry.get('data_type') == TYPE_MANUFACTURER_SPECIFIC:
            if len(entry.get('value')) != 19:
                continue
            Payload = namedtuple('Payload', 'battery temperature humidity')
            payload = Payload._make(unpack('<HHH', entry.get('value')[10:16]))
            print("mac: %s" % mac)
            print("Payload: %d %.2f %.2f %d" % (payload.battery, payload.temperature/16, payload.humidity/16, rssi))

    # Extract Payload
#    Payload = namedtuple('Payload', 'battery temperature humidity')
#    payload = Payload._make(unpack('<HHH', ad_data[19:25]))


raw1 = bytes.fromhex('043e29020100002716000088061d0201060302f0ff15ff110000002716000088063c0c8f01a103b9d70300c8')
raw2 = bytes.fromhex('043e2b020100002716000088061f0201060302f0ff17ff11000000271600008806fa019817000054014e730200d6')
raw3 = bytes.fromhex('043e2302010400271600008806170d09546865726d6f426561636f6e051218003801020a00d9')


print("\nRAW1 (Med packet - 44 bytes)")
process(raw1)
print("\nRAW2 (Long packet - 46 bytes)")
process(raw2)
print("\nRAW3 (Short packet - 38 bytes)")
process(raw3)


# Med packet
#RAW1 (Short packet - 44 bytes)
#('06:88:00:00:16:27',)
#mac: 06:88:00:00:16:27
#Payload: 3132 24.94 58.06 -56
