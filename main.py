from time import sleep, time
import rfid_com as rfid
import spotify_api as spotify
import hw_com as gpio
import threading


volume = spotify.default_volume
tmp_vol = volume
vol_thread_active = False


def main():
    global volume
    refresh_shuffle_led()
    volume = spotify.get_volume()
    print("Scan the learn-card to add a Playlist to the system.")
    print("Scan the setup-card to assign the current playing device as default.")
    sleep(0.5)
    print("Waiting for RFID Signal...")
    while True:
        uid, str_uid = rfid.check_once(10)
        # timeout controlls refresh time for e.g. shuffle refresh
        refresh_shuffle_led()

        if uid == -1:
            continue

        # Device Learning
        if str_uid == spotify.device_card_uid:
            device_id, device_name = spotify.current_device()
            if device_id != -1:  # set device id if id sucessfull retrieved
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
            playstate = True
            gpio.blink_ok()
            sleep(1)


def write_card():
    gpio.set_button_led(gpio.skip_led, 1)
    gpio.set_button_led(gpio.shuffle_led, 1)
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
    gpio.set_button_led(gpio.skip_led, 0)
    gpio.set_button_led(gpio.shuffle_led, 0)
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
        gpio.set_button_led(gpio.shuffle_led, 1)
    elif state is True:
        new_state = False
        gpio.set_button_led(gpio.shuffle_led, 0)
    else:
        return -1
    spotify.set_shuffle_state(new_state)
    # sleep(0.7)
    # gpio.set_button_led(gpio.shuffle_led, spotify.get_shuffle_state())


def playpause_press(channel):  # currently only pauses
    spotify.playpause()


def skip_press(channel):
    print("Skipping...")
    spotify.sp.next_track()
    gpio.set_button_led(gpio.skip_led, 1)
    sleep(0.2)
    gpio.set_button_led(gpio.skip_led, 0)
    return


def refresh_shuffle_led():
    if not vol_thread_active:
        gpio.set_button_led(gpio.shuffle_led, spotify.get_shuffle_state())


def volume_thread():
    global tmp_vol, volume, vol_thread_active
    vol_thread_active = True
    start = time()

    shuffle_before = gpio.GPIO.input(gpio.shuffle_led)
    playpause_before = gpio.GPIO.input(gpio.skip_led)
    gpio.set_button_led(gpio.skip_led, False)
    gpio.set_button_led(gpio.shuffle_led, False)

    prev_vol = volume
    while True:
        sleep(0.1)
        gpio.set_duty_cycle(gpio.shuffle_pwm, volume)
        gpio.set_duty_cycle(gpio.skip_pwm, volume)
        elapsed = time() - start
        '''
        if volume < 33:
            gpio.set_button_led(gpio.skip_led, False)
            gpio.set_button_led(gpio.shuffle_led, False)
        elif volume > 33 and volume < 66:
            gpio.set_button_led(gpio.skip_led, True)
            gpio.set_button_led(gpio.shuffle_led, False)
        elif volume > 66:
            gpio.set_button_led(gpio.skip_led, True)
            gpio.set_button_led(gpio.shuffle_led, True)
        '''
        if volume != prev_vol:
            start = time()
            prev_vol = volume
        elif elapsed > 1.2:
            spotify.set_volume(volume)
            vol_thread_active = False
            gpio.set_button_led(gpio.skip_led, playpause_before)
            gpio.set_button_led(gpio.shuffle_led, shuffle_before)
            return


if __name__ == "__main__":
    print("Rotary Thread is alive: ",gpio.rotary_thread.is_alive())
    while True:
        try:
            main()
        except:
            print("CRASHED! Restarting in 10 seconds")
            for i in range(10):
                gpio.set_button_led(gpio.skip_led, True)
                gpio.set_button_led(gpio.shuffle_led, False)
                # led rot an
                sleep(0.5)
                gpio.set_button_led(gpio.skip_led, False)
                gpio.set_button_led(gpio.shuffle_led, True)
                # led rot aus
                sleep(0.5)
            gpio.set_button_led(gpio.skip_led, False)
            gpio.set_button_led(gpio.shuffle_led, False)