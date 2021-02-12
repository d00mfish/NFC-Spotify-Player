import main
import configparser
import threading
from time import sleep
import RPi.GPIO as GPIO
from pyky040 import pyky040


# =====Getting config values=====
config = configparser.ConfigParser(allow_no_value=True)
config.read("config.cfg")
shuffle_led_pin = int(config["PINS"]["shuffle_led"])
skip_led_pin = int(config["PINS"]["skip_led"])
shuffle_in = int(config["PINS"]["shuffle_in"])
skip_in = int(config["PINS"]["skip_in"])
playpause_in = int(config["PINS"]["rotary_sw"])
rotary_clk = int(config["PINS"]["rotary_clk"])
rotary_dt = int(config["PINS"]["rotary_dt"])

# =====Button setup and inizialisation=====
GPIO.setmode(GPIO.BCM)
GPIO.setup([shuffle_led_pin, skip_led_pin], GPIO.OUT)
GPIO.setup([shuffle_in, skip_in], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(playpause_in, GPIO.IN)
# Init PWM
shuffle_led = GPIO.PWM(shuffle_led_pin, 200)
skip_led = GPIO.PWM(skip_led_pin, 200)
shuffle_led.start(0)
skip_led.start(0)
# Interrupt listener init
GPIO.add_event_detect(
    shuffle_in, GPIO.FALLING, callback=main.shuffle_press, bouncetime=1000
)
GPIO.add_event_detect(skip_in, GPIO.FALLING, callback=main.skip_press, bouncetime=1000)
GPIO.add_event_detect(
    playpause_in, GPIO.FALLING, callback=main.playpause_press, bouncetime=500
)

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
def get_led_state(channel):
    return GPIO.input(channel)


def set_button_led(channel: object, state: bool, speed_ms: int):
#needs a solution to prevent flickering if led is already at on state and gets set to True and vice versa
    if speed_ms == 0:
        channel.ChangeDutyCycle(int(state) * 100)
    elif state:
        for dc in range(1, 101, 1):
            set_led_dc(channel, dc)
            sleep(speed_ms / 100 / 1000)
    else:
        for dc in range(100, -1, -1):
            set_led_dc(channel, dc)
            sleep(speed_ms / 100 / 1000)


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
    channel.ChangeDutyCycle(correction_table[dc])


def blink_error():
    def blink_err_thread():
        shuffle_before = get_led_state(shuffle_led_pin)
        playpause_before = get_led_state(skip_led_pin)
        for _ in range(3):
            set_button_led(skip_led, False,500)
            sleep(0.2)
            set_button_led(shuffle_led, False,500)
            sleep(0.2)
        set_button_led(skip_led, playpause_before, 100)
        set_button_led(shuffle_led, shuffle_before, 100)

    threading.Thread(target=blink_err_thread).start()


def blink_ok():
    def blink_ok_thread():
        shuffle_before = get_led_state(shuffle_led_pin)
        playpause_before = get_led_state(skip_led_pin)
        set_button_led(skip_led, False, 0)
        set_button_led(shuffle_led, False, 0)
        sleep(0.1)
        set_button_led(skip_led, True, 100)
        set_button_led(skip_led, False, 0)
        set_button_led(shuffle_led, True, 100)
        set_button_led(shuffle_led, False, 0)
        set_button_led(skip_led, True, 100)
        set_button_led(skip_led, False, 0)
        set_button_led(skip_led, playpause_before, 100)
        set_button_led(shuffle_led, shuffle_before, 100)

    threading.Thread(target=blink_ok_thread).start()
