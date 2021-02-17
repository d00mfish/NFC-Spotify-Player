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
# pi.set_mode(shuffle_led, pigpio.OUTPUT)
# pi.set_mode(skip_led, pigpio.OUTPUT)
pi.set_mode(shuffle_in, pigpio.INPUT)
pi.set_mode(skip_in, pigpio.INPUT)
pi.set_mode(playpause_in, pigpio.INPUT)
pi.set_pull_up_down(shuffle_in, pigpio.PUD_UP)
pi.set_pull_up_down(skip_in, pigpio.PUD_UP)
# Init PWM
# pi.set_PWM_range(shuffle_led_pin, 100)
# pi.set_PWM_range(skip_led_pin, 100)
pi.hardware_PWM(shuffle_led, 100, 0)
pi.hardware_PWM(skip_led, 100, 0)
# =====Interrupt listener init=====

def shuffle_callback(a,b,c):
    print("shuffle press")

def skip_callback(a,b,c):
    print("skip press")

def playpause_callback(a,b,c):
    print("playpause press")


pi.callback(shuffle_in, 0, shuffle_callback)
pi.callback(skip_in, 0, skip_callback)
pi.callback(playpause_in, 0, playpause_callback)
# debounce 1000 1000 500 ?


# =====Functions=====
def convert_value(inputval, maxinput, maxoutput):
    return 0


def get_led_state(channel):
    return pi.read(channel)*100


def set_led_dc(channel: object, dc):
    correction_table = (
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        5,
        5,
        6,
        6,
        6,
        7,
        7,
        8,
        8,
        9,
        9,
        10,
        10,
        11,
        11,
        12,
        13,
        13,
        14,
        15,
        16,
        16,
        17,
        18,
        19,
        20,
        21,
        21,
        22,
        23,
        24,
        25,
        26,
        28,
        29,
        30,
        31,
        32,
        33,
        35,
        36,
        37,
        39,
        40,
        42,
        43,
        44,
        46,
        48,
        49,
        51,
        53,
        54,
        56,
        58,
        60,
        61,
        63,
        65,
        67,
        69,
        71,
        73,
        76,
        78,
        80,
        82,
        85,
        87,
        89,
        92,
        94,
        97,
        99,
        100,
    )
    pi.hardware_PWM(channel, 100, correction_table[dc] * 10000)
      # making 100 to 1mio and 0 to 0


def set_button_led(channel: int, state: bool, speed_ms: int):
    dc = int(state)*100 #dc in percent
    if get_led_state(channel) != dc:
        if speed_ms == 0:
            set_led_dc(channel, dc)
        elif state:
            for dc in range(1, 101, 1):
                set_led_dc(channel, dc)
                sleep(speed_ms / 100 / 1000)
        else:
            for dc in range(100, -1, -1):
                set_led_dc(channel, dc)
                sleep(speed_ms / 100 / 1000)


def blink_error():
    def blink_err_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        for _ in range(3):
            set_button_led(skip_led, True, 0)
            set_button_led(skip_led, False, 150)
            sleep(0.3)
            set_button_led(shuffle_led, True, 0)
            set_button_led(shuffle_led, False, 150)
            sleep(0.3)
        set_button_led(shuffle_led, shuffle_before, 50)
        set_button_led(skip_led, skip_before, 50)

    threading.Thread(target=blink_err_thread).start()


def blink_ok():
    shuffle_before = get_led_state(shuffle_led)
    skip_before = get_led_state(skip_led)
    set_button_led(skip_led, False, 0)
    set_button_led(shuffle_led, False, 0)
    sleep(0.1)
    set_button_led(skip_led, True, 70)
    set_button_led(skip_led, False, 0)
    set_button_led(shuffle_led, True, 70)
    set_button_led(shuffle_led, False, 0)
    set_button_led(skip_led, True, 70)
    set_button_led(skip_led, False, 0)
    sleep(0.1)
    set_button_led(skip_led, skip_before, 100)
    set_button_led(shuffle_led, shuffle_before, 100)


if __name__ == "__main__":
    while(1):
        set_button_led(shuffle_led, True, 500) 
        set_button_led(skip_led, True, 500) 
        set_button_led(shuffle_led, False, 500)
        set_button_led(skip_led, True, 500) 

        '''
        for dc in range(1,101,1):
            set_led_dc(shuffle_led, dc)
            set_led_dc(skip_led, dc)
        sleep(4)  
        for dc in range(100,-1,-1):
            set_led_dc(shuffle_led, dc)
            set_led_dc(skip_led, dc)
        '''