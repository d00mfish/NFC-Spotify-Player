import time
import rfid_com as rfid
from spotify_api import device_card_uid, learn_card_uid, current_device, set_config_value, look_for_URI, play_context_URI, shuffle_on

# SPI connection:
print("Scan the learn-card to add a Playlist to the system.")
print("Scan the setup-card to assign the current playing device as default.")
print("Waiting for RFID Signal...")

while(True):
    uid = rfid.RFID_read()
    if uid is None:
        time.sleep(0.5)
        continue

    elif uid == device_card_uid:  # check for set-device-id card
        device_data = current_device()
        if device_data != -1:  # set device id if id sucessfull retrieved
            set_config_value('AUTH','device_id',str(device_data[0]))
            print("Set {} as new device.".format(device_data[1]))
            time.sleep(2)
        else:
            print("No playback detected, can't set device.")
            time.sleep(1)
            print("Waiting for RFID Signal...")

    elif uid == learn_card_uid:
        ret = rfid.RFID_learn()
        if ret == 0:
            time.sleep(1)
            print("Waiting for RFID Signal...")
        elif ret == -1:
            print("Something went wrong learning the new Music-Card.")
            time.sleep(1)
            print("Waiting for RFID Signal...")

    else:
        uri = look_for_URI(uid)  # get matching uri from csv
        if uri == -1:
            print("UID not found in Database. Make sure you already added this Card.")
            time.sleep(1)
            print("Waiting for RFID Signal...")
        else:
            print("Found Music-Card.")
            if play_context_URI(uri) != -1:  # play uri playlist at device
                print("Playing now!")
                time.sleep(1)
                print("Waiting for RFID Signal...")
            else:
                print("Current device unavailable, please select an available device.") #maybe use fallback device afterwards?
                print("This can happen if you use a Phone or PC that is not always online.")
                time.sleep(1)
                print("Waiting for RFID Signal...")
