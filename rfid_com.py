import csv
import time
import board
import busio
from digitalio import DigitalInOut
from spotify_api import look_for_URI, device_card_uid, learn_card_uid
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
pn532.SAM_configuration()
pn532.listen_for_passive_target()


def wait_for_uid():
    print("Waiting for RFID Signal...")
    uid = pn532.read_passive_target(timeout=10)
    while(uid is None):
        uid = pn532.read_passive_target(timeout=10)
        print(".", end='')
    str_uid = ''.join(format(x, '0x') for x in uid)
    return uid, str_uid


def look_for_URI(hexstring: str):
    with open("connections.csv", "r") as f:
        data = f.readlines()
        data = [x.strip() for x in data]
        data = [x.split(";") for x in data]
        uri = [x for x in data if hexstring in x]
        if uri == []:
            return -1
        else:
            return uri[0][1]


def learn_card(current_playback):
    try:
        print("")
        print("Playing a playlist containing: {}, by {}.".format(
            current_playback[1], current_playback[2]))
        uri = current_playback[0]
    except TypeError:
        print('''
        >Please play a track out of the playlist you want to learn.
        >Can't be \"Liked Songs\" or Podcast-Shows.
        >Aborting Learning.
        ''')
        return -1
    time.sleep(2)  # wait to avoid double scanning

    print("Scan and hold the card you want to learn now.")
    print("Scan the learn-card again to abort.")
    uid, str_uid = wait_for_uid()
    if str_uid == learn_card_uid or str_uid == device_card_uid:
        print("Can't learn the device or learn card. Arborting!")
        return -1

    else:
        print("Got UID: {}".format(str_uid))
        time.sleep(0.5)
        print("Scan learn-card again to confirm...")
        str_tmp = wait_for_uid()[1]
        if str_tmp != learn_card_uid:
            print(">Scanned card was not the learn-card.")
            print(">Aborting Learning.")
            return -1
        elif str_tmp == learn_card_uid:
            # Save UID and URI in CSV
            if look_for_URI(uid) == -1:  #test if UID already in use
                line = uid + ";" + uri + '\n'
                with open('connections.csv', 'a') as f:
                    f.write(line)
                print("Successfully leaned!")
                # LED 2sec green
                return 0
            else:
                print(">UID already in use.")
                print(">Aborting Learning.")
                return -1
        else:
            return -1



if __name__ == "__main__":

    while(1):
        print("Scan and hold the card you want to learn now.")
        uid = wait_for_uid()
        print("UID-Found:{}".format(uid))
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
