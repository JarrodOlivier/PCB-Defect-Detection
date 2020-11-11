import time
import board
import neopixel

pixel_pin = board.D18
num_pixels = 8 
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER)

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
OFF = (0,0,0)

def pcb_lighting(main=False):
    try:
        if main:
            while True:
                pixels.fill(WHITE)
                pixels.show()
        else:
            pixels.fill(WHITE)
            pixels.show()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        pcb_lighting_off()
        print("Lights off")
    except Exception:
        pcb_lighting_off()
        print("Error! Lights off")

def pcb_lighting_off():
    pixels.fill(OFF)
    pixels.show()

if __name__ == "__main__":
    pcb_lighting(True)