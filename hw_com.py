import configparser
import RPi.GPIO as GPIO
import main
from time import sleep

config = configparser.ConfigParser(allow_no_value=True)
config.read("config.cfg")

#in config
shuffle_led = 16  # config['PINS'][shuffle_led]
skip_led = 20  # config['PINS'][skip_led]

shuffle_in = 19  # config['PINS'][shuffle_in]
playpause_in = 26  # config['PINS'][playpause_in]

R_led = 17
G_led = 27
B_led = 22
# config['PINS'][R_led], config['PINS'][G_led],config['PINS'][B_led]

#Button setup and inizialisation
GPIO.setmode(GPIO.BCM)
GPIO.setup([shuffle_led,skip_led], GPIO.OUT)
GPIO.setup([R_led, G_led, B_led], GPIO.OUT)
GPIO.setup([shuffle_in,playpause_in], GPIO.IN,pull_up_down=GPIO.PUD_UP)

#Reset LEDs
GPIO.output(shuffle_led, 0)
GPIO.output(skip_led, 0)

#Interrupt listener init
v1 = GPIO.add_event_detect(shuffle_in, GPIO.FALLING, 
    callback=main.shuffle_press, bouncetime=600)
v2 = GPIO.add_event_detect(playpause_in, GPIO.FALLING, 
        callback=main.skip_press, bouncetime=600)

def set_button_led(channel: int, state):
        GPIO.output(channel, state)
        
def blink_error():
    shuffle_before = GPIO.input(shuffle_led)
    playpause_before = GPIO.input(skip_led)
    for _ in range(4):
        #GPIO.GPIO.output(R_led, True)
        set_button_led(skip_led, True)
        set_button_led(shuffle_led, True)
        sleep(0.6)
        #GPIO.GPIO.output(R_led, False)
        set_button_led(skip_led, False)
        set_button_led(shuffle_led, False)
        sleep(0.6)
    set_button_led(skip_led, playpause_before)
    set_button_led(shuffle_led, shuffle_before)

def blink_ok():
    shuffle_before = GPIO.input(shuffle_led)
    playpause_before = GPIO.input(skip_led)
    for _ in range(2):
        #GPIO.GPIO.output(R_led, True)
        set_button_led(skip_led, True)
        set_button_led(shuffle_led, True)
        sleep(0.1)
        #GPIO.GPIO.output(R_led, False)
        set_button_led(skip_led, False)
        set_button_led(shuffle_led, False)
        sleep(0.1)
    set_button_led(skip_led, playpause_before)
    set_button_led(shuffle_led, shuffle_before)