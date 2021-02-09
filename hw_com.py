import main
import configparser
import threading
from time import sleep
import RPi.GPIO as GPIO
from pyky040 import pyky040


# =====Getting config values=====
config = configparser.ConfigParser(allow_no_value=True)
config.read("config.cfg")
shuffle_led = config["PINS"]["shuffle_led"]
skip_led = config["PINS"]["skip_led"]
shuffle_in = config["PINS"]["shuffle_in"]
skip_in = config["PINS"]["skip_in"]
playpause_in = config["PINS"]["rotary_sw"]
rotary_clk = config["PINS"]["rotary_clk"]
rotary_dt = config["PINS"]["rotary_dt"]

# =====Button setup and inizialisation=====
GPIO.setmode(GPIO.BCM)
GPIO.setup([shuffle_led, skip_led], GPIO.OUT)
GPIO.setup([shuffle_in, skip_in], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(playpause_in, GPIO.IN)
# Reset LEDs
GPIO.output(shuffle_led, 0)
GPIO.output(skip_led, 0)
# Interrupt listener init
GPIO.add_event_detect(
    shuffle_in, GPIO.FALLING, callback=main.shuffle_press, bouncetime=1000
)
GPIO.add_event_detect(skip_in, GPIO.FALLING, callback=main.skip_press, bouncetime=1000)
GPIO.add_event_detect(
    skip_in, GPIO.FALLING, callback=main.playpause_press, bouncetime=500
)

# =====Rotary setup and inizialisation=====
def volume_callback(scale_position):
    main.volume = scale_position
    if not main.volume_thread.is_alive():
        main.volume_thread.start()

rotary_encoder = pyky040.Endcoder(
    CLK=rotary_clk, DT=rotary_dt, SW=playpause_in
)  # not needed if device added in boot
rotary_encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=volume_callback)
rotary_thread = threading.Thread(target=rotary_encoder.watch)
rotary_thread.start()


def set_button_led(channel: int, state):
    GPIO.output(channel, state)


def get_button_led_state(channel: int):
    return GPIO.input(channel)


def blink_error():
    shuffle_before = get_button_led_state(shuffle_led)
    playpause_before = get_button_led_state(skip_led)
    for _ in range(3):
        # GPIO.GPIO.output(R_led, True)
        set_button_led(skip_led, True)
        set_button_led(shuffle_led, True)
        sleep(0.5)
        # GPIO.GPIO.output(R_led, False)
        set_button_led(skip_led, False)
        set_button_led(shuffle_led, False)
        sleep(0.5)
    set_button_led(skip_led, playpause_before)
    set_button_led(shuffle_led, shuffle_before)


def blink_ok():
    shuffle_before = get_button_led_state(shuffle_led)
    playpause_before = get_button_led_state(skip_led)
    for _ in range(2):
        # GPIO.GPIO.output(R_led, True)
        set_button_led(skip_led, True)
        set_button_led(shuffle_led, True)
        sleep(0.1)
        # GPIO.GPIO.output(R_led, False)
        set_button_led(skip_led, False)
        set_button_led(shuffle_led, False)
        sleep(0.1)
    set_button_led(skip_led, playpause_before)
    set_button_led(shuffle_led, shuffle_before)