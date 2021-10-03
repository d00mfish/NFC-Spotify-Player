import main
import configparser
import threading
from time import sleep
import pigpio
from pyky040 import pyky040

ON = 100
OFF = 0

#Device Overlay is more reliable
#for help see: https://github.com/raphaelyancey/pyKY040#should-i-use-the-gpio-polling-or-the-device-overlay
use_device_overlay = True
rotary_encoder_device = "/dev/input/event0"


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
pi.set_mode(shuffle_in, pigpio.INPUT)
pi.set_mode(skip_in, pigpio.INPUT)
pi.set_mode(playpause_in, pigpio.INPUT)
pi.set_pull_up_down(shuffle_in, pigpio.PUD_UP)
pi.set_pull_up_down(skip_in, pigpio.PUD_UP)
# Init PWM
pi.hardware_PWM(shuffle_led, 100, 0)
pi.hardware_PWM(skip_led, 100, 0)
# =====Callback listener inizialisation=====
pi.set_glitch_filter(shuffle_in, 70000)
pi.set_glitch_filter(skip_in, 70000)
pi.set_glitch_filter(playpause_in, 70000)
sleep(0.3)  # Wait for pullup to pull up
pi.callback(shuffle_in, pigpio.FALLING_EDGE, main.shuffle_press)
pi.callback(skip_in, pigpio.FALLING_EDGE, main.skip_press)
pi.callback(playpause_in, pigpio.FALLING_EDGE, main.playpause_press)

# =====Rotary setup and inizialisation=====
def volume_callback(scale_position):
    main.volume = scale_position
    if not main.vol_thread_active:
        threading.Thread(target=main.volume_thread).start()

if use_device_overlay:
    rotary_encoder = pyky040.Encoder(device=rotary_encoder_device)
else:
    rotary_encoder = pyky040.Encoder(CLK=rotary_clk,DT=rotary_dt,)
rotary_encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=volume_callback)
rotary_thread = threading.Thread(target=rotary_encoder.watch)
rotary_thread.start()


# =====Functions=====
def convert_value(inputval, maxinput, maxoutput):
    return 0


def get_led_state(channel):
    return int(pi.get_PWM_dutycycle(channel) / 10000)


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
        100,
    )
    # print("Dutycycle:",dc)
    pi.hardware_PWM(channel, 100, correction_table[dc] * 10000)


def set_button_led(channel: int, dc: int, speed_ms: int):
    dc_before = get_led_state(channel)
    if dc_before != dc:
        if speed_ms == 0:
            set_led_dc(channel, dc)
        elif dc_before < dc:
            def animation_up(channel, dc , speed_ms):
                sleeptime = speed_ms / (dc - dc_before) / 1000
                for dc_step in range(dc_before, dc + 1, 1):
                    set_led_dc(channel, dc_step)
                    sleep(sleeptime)
            threading.Thread(target=animation_up, args=(channel, dc , speed_ms)).start()
        elif dc_before > dc:
            def animation_down(channel, dc , speed_ms):
                sleeptime = speed_ms / (dc_before - dc) / 1000
                for dc_step in range(dc_before, dc - 1, -1):
                    set_led_dc(channel, dc_step)
                    sleep(sleeptime)
            threading.Thread(target=animation_down, args=(channel, dc , speed_ms)).start()


def blink_error():
    def blink_error_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        set_button_led(skip_led, OFF, 0)
        set_button_led(shuffle_led, OFF, 0)
        for _ in range(3):
            set_button_led(skip_led, ON, 150)
            set_button_led(shuffle_led, ON, 150)
            sleep(0.3)
            set_button_led(skip_led, OFF, 150)
            set_button_led(shuffle_led, OFF, 150)
            sleep(0.3)
        set_button_led(shuffle_led, shuffle_before, 50)
        set_button_led(skip_led, skip_before, 50)

    threading.Thread(target=blink_error_thread).start()

def blink_ok():
    def blink_ok_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        set_button_led(skip_led, ON, 0)
        set_button_led(shuffle_led, ON, 0)
        set_button_led(skip_led, OFF, 800)
        set_button_led(shuffle_led, OFF, 800)
        sleep(1)
        set_button_led(skip_led, skip_before, 50)
        set_button_led(shuffle_led, shuffle_before, 50)

    threading.Thread(target=blink_ok_thread).start()


def blink_ok2():
    def blink_ok_thread():
        shuffle_before = get_led_state(shuffle_led)
        skip_before = get_led_state(skip_led)
        set_button_led(skip_led, OFF, 0)
        set_button_led(shuffle_led, OFF, 0)
        set_button_led(skip_led, ON, 0)
        sleep(0.07)
        set_button_led(skip_led, OFF, 0)
        sleep(0.07)
        set_button_led(shuffle_led, ON, 0)
        sleep(0.07)
        set_button_led(shuffle_led, OFF, 0)
        sleep(0.07)
        set_button_led(skip_led, ON, 0)
        sleep(0.07)
        set_button_led(skip_led, OFF, 0)
        sleep(0.07)
        set_button_led(skip_led, skip_before, 50)
        set_button_led(shuffle_led, shuffle_before, 50)

    threading.Thread(target=blink_ok_thread).start()


if __name__ == "__main__":
    blink_ok()
