import csv
import time
import board
import busio
from digitalio import DigitalInOut
from spotify_api import current_playback, learn_card_uid, device_card_uid, look_for_URI
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()
pn532.listen_for_passive_target()
print("Waiting for NFC-card...")

def RFID_read():
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=10)
    #uid = RFID_read_test(7)
    if uid is None:
        retval = None
    else:
        retval = ''.join(format(x, '0x')
                         for x in uid)  # bytearray to hex string
        #print("Found UID:", retval)
    return retval


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


def RFID_learn():
    # Get current playlist uri and playing song info
    current = current_playback()
    try:
        print("Playing a playlist containing: {}, by {}.".format(current[1], current[2]))
        uri = current[0]
    except TypeError:
        print(">Please play a track out of the playlist you want to learn.")
        print(">Can't be \"Liked Songs\" or Podcast-Shows.")
        print(">Aborting Learning.")
        return -1

    time.sleep(1)  # wait to avoid double scanning

    print("Scan the card you want to learn now, scan the learn card again to abort.")
    uid = RFID_read()
    while uid is None:
        time.sleep(0.5)
        uid = RFID_read()
        continue
        # LED green blink 2Hz
    print("UID Found:", uid)    # LED green on
    time.sleep(1)

    if uid == learn_card_uid:
        print(">Tried to use the learn-card as new card, that is not possible.")
        print(">Aborting Learning.")
        return -1
    
    else:
        print("Scan learn-card again to confirm...")
        tmp = RFID_read()
        while tmp is None:  # Wait for learning card
            time.sleep(0.5)
            tmp = RFID_read()
            continue
        if tmp != learn_card_uid:
            print(">Scanned card was not the learn-card.")
            print(">Aborting Learning.")
            return -1
        elif tmp == learn_card_uid:
            # Save UID and URI in CSV
            if look_for_URI(uid) == -1:  #test if UID already in use
                line = uid + ";" + uri + '\n'
                with open('learned.csv', 'a') as f:
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
