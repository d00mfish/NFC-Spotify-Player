from time import sleep
import rfid_com as rfid
import spotify_api as spotify
import hw_com as gpio


print("Scan the learn-card to add a Playlist to the system.")
print("Scan the setup-card to assign the current playing device as default.")


def main():
    print("Waiting for RFID Signal...")
    while True:
        uid, str_uid = rfid.check_once(20)  # timeout controlls refresh time for e.g. shuffle refresh

        gpio.set_button_led(gpio.shuffle_led, spotify.get_shuffle_state())
        if uid == -1:
            continue

        # Device Learning
        if str_uid == spotify.device_card_uid:
            device_id, device_name = spotify.current_device()
            if device_id != -1:  # set device id if id sucessfull retrieved
                spotify.set_config_value("DEVICE", "device_id", str(device_id))
                print("Set {} as new device. ID:{}".format(device_name, device_id))
                sleep(2)
                continue
            print("No playback detected, can't set device.")
            sleep(2)

        # Starting Card-Writing
        elif str_uid == spotify.learn_card_uid:
            if write_card() == -1:
                print("Something went wrong writing the new Music-Card.")
            sleep(2)

        # read data and play
        else:
            uri = rfid.read_uri(uid)
            if uri == -1:
                print("Make sure you already added this Card.")
                sleep(1)
                continue

            print("Found Music-Card.")
            if spotify.play_context_URI(uri) == -1:  # play uri playlist at device
                print(
                    "Current device unavailable, please select an available device."
                )  # maybe use fallback device?
                print(
                    "This can happen if you use a Phone or PC that is not always online."
                )
                sleep(1)
                continue

            print("Playing now!")
            sleep(1)


def write_card():
    # Get current playlist uri and playing song info
    try:
        current = spotify.current_playback()
    except TypeError:
        print(
            """
        >Please play a track out of the playlist you want to learn.
        >Can't be \"Liked Songs\" or Podcast-Shows.
        >Aborting Learning.
        """
        )
        return -1
    print("")
    print("Playing a playlist containing: {}, by {}.".format(current[1], current[2]))
    uri = current[0]

    sleep(3)

    print("Scan and hold the card you want to learn now.")
    print("Scan the learn-card again to abort.")
    str_uid = rfid.wait_for_uid()[1]
    if str_uid == spotify.learn_card_uid or str_uid == spotify.device_card_uid:
        print(" >Can't write uri to learn or device card. Arborting!")
        return -1

    if rfid.write_uri(uri) == -1:
        print(" >Error while writing.")
        return -1

    print("Successfully leaned!")


def shuffle_press(channel):
    print("Shuffle Press.")
    state = spotify.get_shuffle_state()
    if state is False:
        new = True
    elif state is True:
        new = False
    else:
        return -1
    spotify.set_shuffle(new)
    sleep(0.7)
    gpio.set_button_led(gpio.shuffle_led, spotify.get_shuffle_state())
    

def playpause_press(channel):   #currently only pauses
    print("Pause Press.")
    spotify.pause()

def skip_press(channel)


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            print("CRASHED! Restarting in 10 seconds")
            for i in range(10):
                gpio.set_button_led(gpio.playpause_led, True)
                # led rot an
                sleep(0.5)
                gpio.set_button_led(gpio.playpause_led, False)
                # led rot aus
                sleep(0.5)