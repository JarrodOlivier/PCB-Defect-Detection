import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

def backlight(main=False):
    try:
        if main==True:
            while True:
                GPIO.output(23,1)
        else:
            GPIO.output(23,1)

    except Exception:
        backlight_off()

def backlight_off():
    GPIO.output(23,0)
    

if __name__ == "__main__":
    backlight(True)
    GPIO.cleanup()
    