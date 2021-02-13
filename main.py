from time import sleep, time
import rfid_com as rfid
import spotify_api as spotify
import hw_com as gpio

volume = None
tmp_vol = volume
vol_thread_active = False

def main():
    global volume
    print("Scan the learn-card to add a Playlist to the system.")
    print("Scan the setup-card to assign the current playing device as default.")
    sleep(0.5)
    refresh_shuffle_led()
    volume = spotify.get_volume()
    print("Waiting for RFID Signal...")
# =====Main Loop=====
    while True:
        uid, str_uid = rfid.check_once(10)
        # timeout controlls refresh time for e.g. shuffle refresh
        refresh_shuffle_led()
        volume = spotify.get_volume()
        if uid == -1:
            continue

# =====Checking uids for detected Card=====
        print("UID: ",str_uid)
        # Device Learning
        if str_uid == spotify.device_card_uid:
            device_id, device_name = spotify.current_device()
            if device_id != -1:
                spotify.set_config_value("DEVICE", "device_id", str(device_id))
                print("Set {} as new device. ID:{}".format(device_name, device_id))
                gpio.blink_ok()
                sleep(2)
                continue
            print("No playback detected, can't set device.")
            gpio.blink_error()
            sleep(2)

        # Starting Card-Writing
        elif str_uid == spotify.learn_card_uid:
            if write_card() == -1:
                print("Something went wrong writing the new Music-Card.")
                gpio.blink_error()
            sleep(2)

        # read data and play
        else:
            uri = rfid.read_uri(uid)
            if uri == -1:
                print("Make sure you already added this Card.")
                gpio.blink_error()
                sleep(1)
                continue

            print("Found Music-Card.")
            if spotify.play_context_URI(uri) == -1:  # play uri playlist at device
                gpio.blink_error()
                print(
                    "Current device unavailable, please select an available device."
                )  # maybe use fallback device?
                print(
                    "This can happen if you use a Phone or PC that is not always online."
                )
                sleep(1)
                continue

            print("Playing now!")
            spotify.playstate = True
            gpio.blink_ok()
            sleep(1)


def write_card():
    #shuffle_before = gpio.get_led_state(gpio.shuffle_led_pin)
    gpio.set_button_led(gpio.skip_led, True, 0)
    gpio.set_button_led(gpio.shuffle_led, True, 0)
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

    sleep(2)
    print("Scan and hold the card you want to learn now.")
    print("Scan the learn-card again to abort.")
    str_uid = rfid.wait_for_uid()[1]
    gpio.set_button_led(gpio.skip_led, False, 150)
    gpio.set_button_led(gpio.shuffle_led, False, 150)
    if str_uid == spotify.learn_card_uid or str_uid == spotify.device_card_uid:
        print(" >Can't write uri to learn or device card. Arborting!")
        return -1

    if rfid.write_uri(uri) == -1:
        print(" >Error while writing.")
        return -1

    print("Successfully leaned!")
    gpio.blink_ok()


def shuffle_press(channel):
    state = spotify.get_shuffle_state()
    if state is False:
        new_state = True
        gpio.set_button_led(gpio.shuffle_led, True, 500)
    elif state is True:
        new_state = False
        gpio.set_button_led(gpio.shuffle_led, False, 500)
    else:
        return -1
    spotify.set_shuffle_state(new_state)
    # sleep(0.7)
    # gpio.set_button_led(gpio.shuffle_led, spotify.get_shuffle_state())


def playpause_press(channel):  # currently only pauses
    spotify.playpause()
    gpio.blink_ok()


def skip_press(channel):
    print("Skipping...")
    spotify.sp.next_track()
    gpio.set_button_led(gpio.skip_led, True, 150)
    gpio.set_button_led(gpio.skip_led, False, 150)


def refresh_shuffle_led():
    if not vol_thread_active:   #so volume pwm doesn't get interrupted
        shufflestate = spotify.get_shuffle_state()
        if gpio.get_led_state(gpio.shuffle_led_pin) != int(shufflestate):    #only set led of neccesary
            gpio.set_button_led(gpio.shuffle_led, shufflestate , 300)


def volume_thread():
    global tmp_vol, volume, vol_thread_active
    vol_thread_active = True
    start = time()

    shuffle_before = gpio.get_led_state(gpio.shuffle_led_pin)
    skip_before = gpio.get_led_state(gpio.skip_led_pin)

    prev_vol = volume
    while True:
        sleep(0.1)
        gpio.set_led_dc(gpio.shuffle_led, volume)
        gpio.set_led_dc(gpio.skip_led, volume)
        elapsed = time() - start
        """
        if volume < 33:
            gpio.set_button_led(gpio.skip_led, False)
            gpio.set_button_led(gpio.shuffle_led, False)
        elif volume > 33 and volume < 66:
            gpio.set_button_led(gpio.skip_led, True)
            gpio.set_button_led(gpio.shuffle_led, False)
        elif volume > 66:
            gpio.set_button_led(gpio.skip_led, True)
            gpio.set_button_led(gpio.shuffle_led, True)
        """
        if volume != prev_vol:
            start = time()
            prev_vol = volume
        elif elapsed > 1.2:
            spotify.set_volume(volume)
            vol_thread_active = False
            gpio.set_button_led(gpio.skip_led, skip_before, 0)
            gpio.set_button_led(gpio.shuffle_led, shuffle_before, 0)
            return


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            print("CRASHED! Restarting in 10 seconds")
            gpio.set_button_led(gpio.skip_led, False, 0)
            gpio.set_button_led(gpio.shuffle_led, False, 0)
            for i in range(7):
                gpio.set_button_led(gpio.skip_led, True, 150)
                gpio.set_button_led(gpio.shuffle_led, True, 150)
                # led rot an
                sleep(0.5)
                gpio.set_button_led(gpio.skip_led, False, 150)
                gpio.set_button_led(gpio.shuffle_led, False, 150)
                # led rot aus
                sleep(0.5)
            gpio.set_button_led(gpio.skip_led, False, 0)
            gpio.set_button_led(gpio.shuffle_led, False, 0)
