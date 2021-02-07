import configparser
import RPi.GPIO as GPIO
import main
from time import sleep

config = configparser.ConfigParser(allow_no_value=True)
config.read("config.cfg")

#in config
shuffle_led = 16  # config['PINS'][shuffle_led]
playpause_led = 20  # config['PINS'][playpause_led]

shuffle_in = 19  # config['PINS'][shuffle_in]
playpause_in = 26  # config['PINS'][playpause_in]

R_led = 17
G_led = 27
B_led = 22
# config['PINS'][R_led], config['PINS'][G_led],config['PINS'][B_led]

GPIO.setmode(GPIO.BCM)
GPIO.setup([shuffle_led,playpause_led], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup([R_led, G_led, B_led], GPIO.OUT, initial=GPIO.LOW)
GPIO.setup([shuffle_in,playpause_in], GPIO.IN,pull_up_down=GPIO.PUD_UP)

v1 = GPIO.add_event_detect(shuffle_in, GPIO.FALLING, 
    callback=main.shuffle_press, bouncetime=600)
v2 = GPIO.add_event_detect(playpause_in, GPIO.FALLING, 
        callback=main.playpause_press, bouncetime=600)
#Button setup and inizialisation


def set_button_led(channel: int, state):
        GPIO.output(channel, state)
        
def blink_error():
    for _ in range(3):
        GPIO.GPIO.output(R_led, True)
        sleep(0.5)
        GPIO.GPIO.output(R_led, False)
        sleep(0.5)

def blink_ok():
    for _ in range(2):
        GPIO.GPIO.output(G_led, True)
        sleep(0.1)
        GPIO.GPIO.output(G_led, False)
        sleep(0.1)