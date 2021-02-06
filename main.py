import time
import rfid_com as rfid
import spotify_api as spotify


print("Scan the learn-card to add a Playlist to the system.")
print("Scan the setup-card to assign the current playing device as default.")

def main():
    print("Waiting for RFID Signal...")
    while(True):
        uid, str_uid = rfid.check_once(0.5)#timeout controlls refresh time for loop
        #get_shuffle_state()
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
            if write_card() == -1:
                print("Something went wrong writing the new Music-Card.")
            time.sleep(2)
            
        #read data and play
        else:
            uri = rfid.read_uri(uid)
            if uri == -1:
                print("Make sure you already added this Card.")
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




def write_card():
    # Get current playlist uri and playing song info
    try:
        current = spotify.current_playback()
    except TypeError:
        print('''
        >Please play a track out of the playlist you want to learn.
        >Can't be \"Liked Songs\" or Podcast-Shows.
        >Aborting Learning.
        ''')
        return -1
    print("")
    print("Playing a playlist containing: {}, by {}.".format(
        current[1], current[2]))
    uri = current[0]

    # preparing uri into byte arrays
    parts = [uri[i:i+4] for i in range(0, len(uri), 4)]
    print("Number of Parts: {}".format(len(parts)))
    # making bytearrays with 16bytes of size, no matter what
    data_arrays = [bytearray(i, 'utf-8')+bytearray(4-len(i)) for i in parts]
    print(data_arrays)

    time.sleep(3)

    print("Scan and hold the card you want to learn now.")
    print("Scan the learn-card again to abort.")
    str_uid = rfid.wait_for_uid()[1]
    if str_uid == spotify.learn_card_uid or str_uid == spotify.device_card_uid:
        print("Can't write uri to learn or device card. Arborting!")
        return -1
    
    for i in range(len(data_arrays)):
        if rfid.write_block(i+10, data_arrays[i]) == -1:
            print("Something went wrong writing.")
            return -1
            
    print("Successfully leaned!")




if __name__ == '__main__':
    main()