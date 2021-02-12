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
def set_button_led(channel: object, state: bool, speed_ms: int):
    if speed_ms == 0:
        channel.ChangeDutyCycle(int(state))
    elif state:
        low = 1
        high = 101
        incr = 1
    else:
        low = 100
        high = -1
        incr = -1
    for dc in (low, high, incr):
        channel.ChangeDutyCycle(dc)
        sleep(speed_ms / 100 / 1000)


def blink_error():
    shuffle_before = GPIO.input(shuffle_led)
    playpause_before = GPIO.input(skip_led)
    for _ in range(3):
        set_button_led(skip_led, True, 100)
        set_button_led(shuffle_led, True, 100)
        sleep(0.5)
        set_button_led(skip_led, False, 100)
        set_button_led(shuffle_led, False, 100)
        sleep(0.5)
    set_button_led(skip_led, playpause_before, 100)
    set_button_led(shuffle_led, shuffle_before, 100)


def blink_ok():
    shuffle_before = GPIO.input(shuffle_led)
    playpause_before = GPIO.input(skip_led)
    for _ in range(2):
        set_button_led(skip_led, True, 100)
        set_button_led(shuffle_led, True, 100)
        sleep(0.1)
        set_button_led(skip_led, False, 100)
        set_button_led(shuffle_led, False, 100)
        sleep(0.1)
    set_button_led(skip_led, playpause_before, 100)
    set_button_led(shuffle_led, shuffle_before, 100)
