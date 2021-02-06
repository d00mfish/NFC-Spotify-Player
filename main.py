import time
import rfid_com as rfid
import spotify_api as spotify
import hw_com as gpio


print("Scan the learn-card to add a Playlist to the system.")
print("Scan the setup-card to assign the current playing device as default.")

while(True):
    uid, str_uid = rfid.check_once(0.5)
    gpio.set_shuffle_led(spotify.get_shuffle_state)





    if uid == -1:
        continue
    
    #Device Learning
    if str_uid == spotify.device_card_uid:
        device_id, device_name = spotify.current_device()
        if device_id != -1:  # set device id if id sucessfull retrieved
            spotify.set_config_value('AUTH','device_id',str(device_id))
            print("Set {} as new device.".format(device_name))
            time.sleep(2)
            continue
        print("No playback detected, can't set device.")
        time.sleep(2)
    
    #Starting Card-Writing
    elif str_uid == spotify.learn_card_uid:
        if rfid.learn_card(spotify.current_playback()) == -1:
            print("Something went wrong writing the new Music-Card.")
        time.sleep(2)


    else:
        uri = rfid.look_for_URI(uid)
        if uri == -1:
            print("Problem while reading. Make sure you already added this Card.")
            time.sleep(1)
            continue
        
        print("Found Music-Card.")
        if spotify.play_context_URI(uri) == -1:  # play uri playlist at device
            print("Current device unavailable, please select an available device.") #maybe use fallback device afterwards?
            print("This can happen if you use a Phone or PC that is not always online.")
            time.sleep(1)
            continue
            
        print("Playing now!")
        time.sleep(1)


