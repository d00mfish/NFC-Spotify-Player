import main
import configparser
import threading
from time import sleep
import pigpio
from pyky040 import pyky040


# =====Getting config values=====
config = configparser.ConfigParser(allow_no_value=True)
config.read("config.cfg")
shuffle_led = int(config["PINS"]["shuffle_led"])
skip_led = int(config["PINS"]["skip_led"])
shuffle_in = int(config["PINS"]["shuffle_in"])
skip_in = int(config["PINS"]["skip_in"])
playpause_in = int(config["PINS"]["rotary_sw"])
rotary_clk = int(config["PINS"]["rotary_clk"])
rotary_dt = int(config["PINS"]["rotary_dt"])

# =====Button setup and inizialisation=====
pi = pigpio.pi()
#pi.set_mode(shuffle_led, pigpio.OUTPUT)
#pi.set_mode(skip_led, pigpio.OUTPUT)
pi.set_mode(shuffle_in, pigpio.INPUT)
pi.set_mode(skip_in, pigpio.INPUT)
pi.set_mode(playpause_in, pigpio.INPUT)
pi.set_pull_up_down(shuffle_in, pigpio.PUD_UP)
pi.set_pull_up_down(skip_in, pigpio.PUD_UP)
# Init PWM
#pi.set_PWM_range(shuffle_led_pin, 100)
#pi.set_PWM_range(skip_led_pin, 100)
pi.hardware_PWM(shuffle_led, 100, 0)
pi.hardware_PWM(skip_led, 100, 0)
# =====Interrupt listener init=====
pi.callback(shuffle_in, 0, main.shuffle_press)
pi.callback(skip_in, 0, main.skip_press)
pi.callback(playpause_in, 0, main.playpause_press)
#debounce 1000 1000 500 ?

# =====Rotary setup and inizialisation=====
def volume_callback(scale_position):
    main.volume = scale_position
    if not main.vol_thread_active:
        threading.Thread(target=main.volume_thread).start()

rotary_encoder = pyky040.Encoder(
    CLK=rotary_clk, DT=rotary_dt, SW=playpause_in
)  # not needed if device added in boot
rotary_encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=volume_callback)
rotary_thread = threading.Thread(target=rotary_encoder.watch)
rotary_thread.start()

# =====Functions=====
def convert_value(inputval, maxinput, maxoutput):




def get_led_state(channel):
    return pi.read(channel)


def set_button_led(channel: int, state: bool, speed_ms: int):
    # needs a solution to prevent flickering if led is already at on state and gets set to True and vice versa
    # easies way would be to read the current state but doesn't work
    startval = get_led_state(channel)
    print("Current LED Value:", startval)
    if speed_ms == 0:
        pi.hardware_PWM(channel, 100, int(state)*1000000)   #1mio should be 100% at 100Hz
    elif state:
        for dc in range(1, 101, 1):
            pi.hardware_PWM(channel, 100, dc*10000) #making 100 to 1mio and 0 to 0
            sleep(speed_ms / 100 / 1000)
    else:
        for dc in range(100, -1, -1):
            pi.hardware_PWM(channel, 100, dc*10000)
            sleep(speed_ms / 100 / 1000)


def set_led_dc(channel: object, dc):
    pi.hardware_PWM(channel, 100, dc*1000*1000)


def blink_error():
    def blink_err_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        for _ in range(3):
            set_button_led(skip_led, False, 300)
            sleep(0.2)
            set_button_led(shuffle_led, False, 300)
            sleep(0.2)
        if shuffle_before:
            set_button_led(shuffle_led, shuffle_before, 300)
        if skip_before:
            set_button_led(skip_led, skip_before, 300)

    threading.Thread(target=blink_err_thread).start()


def blink_ok():
    def blink_ok_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        set_button_led(skip_led, False, 0)
        set_button_led(shuffle_led, False, 0)
        sleep(0.1)
        set_button_led(skip_led, True, 100)
        set_button_led(skip_led, False, 0)
        set_button_led(shuffle_led, True, 100)
        set_button_led(shuffle_led, False, 0)
        set_button_led(skip_led, True, 100)
        set_button_led(skip_led, False, 0)
        if skip_before:
            set_button_led(skip_led, skip_before, 100)
        if shuffle_before:
            set_button_led(shuffle_led, shuffle_before, 100)

    threading.Thread(target=blink_ok_thread).start()
