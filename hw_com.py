import configparser
import RPi.GPIO as GPIO
import main

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



def shuffle_press(channel):
    print("shuffle", end='')
    
def playpause_press(channel):
    print("playpause", end='')
    
def set_button_led(channel: int, state: int):
        GPIO.output(channel, state)
        
def signal_handler(sig, frame):
    GPIO.cleanup()
    
def button_listener():
    v1 = GPIO.add_event_detect(shuffle_in, GPIO.FALLING, 
        callback=shuffle_press, bouncetime=600)
    v2 = GPIO.add_event_detect(playpause_in, GPIO.FALLING, 
          callback=playpause_press, bouncetime=600)
    return v1, v2