import time
import board
import busio
from digitalio import DigitalInOut
from spotify_api import device_card_uid, learn_card_uid
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_B, MIFARE_CMD_AUTH_A
from adafruit_pn532.spi import PN532_SPI

#RFID-Setup
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
pn532.SAM_configuration()
pn532.listen_for_passive_target()

#RFID-Key Config
key_a = b"\xFF\xFF\xFF\xFF\xFF\xFF"
key_b = b"\xFF\xFF\xFF\xFF\xFF\xFF"
write_key = 'A'
read_key = 'A'


def wait_for_uid():
    print("Waiting for RFID Signal...")
    uid = pn532.read_passive_target(timeout=10)
    while(uid is None):
        uid = pn532.read_passive_target(timeout=10)
        print(".", end='')
    str_uid = ''.join(format(x, '0x') for x in uid)
    return uid, str_uid


def check_once(timeout):
    uid = pn532.read_passive_target(timeout=timeout)
    if uid is not None:
        str_uid = ''.join(format(x, '0x') for x in uid)
        return uid, str_uid
    return -1, -1


def RFID_read(block):
    data = pn532.ntag2xx_read_block(block)
    if data is None:
        return -1
    return data


def read_uri(uid):
    data_arrays = []
    #while(data_arrays[-1] != bytearray(4)):
    for i in range(10, 31):
        array = RFID_read(i)
        if array == bytearray(4):
            return ''.join([x.decode('utf-8').strip('\x00') for x in data_arrays])
        else:
            data_arrays.append(array)


def write_block(block, data):
    if pn532.ntag2xx_write_block(block, data) is False:
        return -1


if __name__ == "__main__":

    while(1):
        print("Scan and hold the card you want to learn now.")
        uid, str_uid = wait_for_uid()
        print("UID-Found:{}".format(uid))
        uri = read_uri(uid)
        if uri == '':
            print("Card empty.")
        else:
            print(uri)
        
        
        
        
        time.sleep(5)

    '''
    while(1):
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:
            continue
        else:
            print(uid)
    '''


''' Only used for testing
def RFID_read_test(uidlenght=4):
    try:
        import random
    except ImportError:
        pass

    if uidlenght == 0:
        uid = None
    else:
        uid = bytearray([random.randint(0, 255) for _ in range(uidlenght)])
    return uid
'''
