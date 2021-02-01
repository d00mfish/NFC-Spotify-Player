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


def RFID_read(uid, block, read_key):
    if read_key == 'A':
        key = key_a
        key_type = MIFARE_CMD_AUTH_A
    elif read_key == 'B':
        key = key_b
        key_type = MIFARE_CMD_AUTH_B
    else:
        raise Exception("read_key must be 'A' or 'B'")

    authenticated = pn532.mifare_classic_authenticate_block(uid, block, key_type, key)
    if not authenticated:
        print("Read Authentication failed!")
        return -1
    else:
        return pn532.mifare_classic_read_block(block)


def read_uri(uid):
    b1 = RFID_read(uid, 16, 'A')
    b2 = RFID_read(uid, 17, 'A')
    b3 = RFID_read(uid, 18, 'A')
    b4 = RFID_read(uid, 20, 'A')
    if -1 in (b1, b2, b3, b4):
        print("Something went wrong reading.")
        return -1
    return (b1+b2+b3+b4).decode('utf-8').strip('\x00')


def write_block(uid, block, data, write_key):  # Writekey must be A or B
    if write_key == 'A':
        key = key_a
        key_type = MIFARE_CMD_AUTH_A
    elif write_key == 'B':
        key = key_b
        key_type = MIFARE_CMD_AUTH_B
    else:
        raise Exception("write_key must be 'A' or 'B'")

    authenticated = pn532.mifare_classic_authenticate_block(uid, block, key_type, key)
    if not authenticated:
        print("Write Authentication failed!")
        return -1
    else:
        if pn532.mifare_classic_write_block(block, data) is False:
            return -1


def write_card(current):
    # Get current playlist uri and playing song info
    try:
        print("")
        print("Playing a playlist containing: {}, by {}.".format(
            current[1], current[2]))
        uri = current[0]
    except TypeError:
        print('''
        >Please play a track out of the playlist you want to learn.
        >Can't be \"Liked Songs\" or Podcast-Shows.
        >Aborting Learning.
        ''')
        return -1

    # preparing uri into byte arrays
    parts = [uri[i:i+16] for i in range(0, len(uri), 16)]
    # making bytearrays with 16bytes of size, no matter what
    b1 = bytearray(parts[0], 'utf-8')+bytearray(16-len(parts[0]))
    b2 = bytearray(parts[1], 'utf-8')+bytearray(16-len(parts[1]))
    b3 = bytearray(parts[2], 'utf-8')+bytearray(16-len(parts[2]))
    b4 = bytearray(parts[3], 'utf-8')+bytearray(16-len(parts[3]))

    time.sleep(3)

    print("Scan and hold the card you want to learn now.")
    print("Scan the learn-card again to abort.")
    uid, str_uid = wait_for_uid()
    if str_uid == learn_card_uid or str_uid == device_card_uid:
        print("Can't write uri to learn or device card. Arborting!")
        return -1
    
    r1 = write_block(uid, 16, b1, 'A')
    r2 = write_block(uid, 17, b2, 'A')
    r3 = write_block(uid, 18, b3, 'A')
    r4 = write_block(uid, 20, b4, 'A')

    if -1 in (r1, r2, r3, r4):
        print("Something went wrong writing.")
        return -1
    print("Successfully leaned!")


if __name__ == "__main__":

    while(1):
        print("Scan and hold the card you want to learn now.")
        uid = wait_for_uid()
        print("UID-Found:{}".format(uid))
        
        
        
        
        play_context_URI(uri)
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
