import picamera
from Backlight import backlight, backlight_off
from Pcb_Lighting import pcb_lighting, pcb_lighting_off
import time

camera = picamera.PiCamera()
# https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7
camera.resolution = (2592, 1944)
camera.framerate = 15

prev_user_input = "t"

count_t = 0
count_s = 0
while (True): 
    user_input = input("Take Image?")

    if user_input == "n":
        break
        camera.close()

    # backlight()
    # pcb_lighting()

    time.sleep(2)
    # camera.brightness = 50
    camera.brightness = 40
    camera.contrast = 60
    camera.image_effect = "none"
    camera.exposure_mode = "off"
    camera.awb_mode = "off"
    camera.awb_gains = (1.961, 1.520) # rg gain, bg gain (Calibrated from GUI)
    

    if user_input=="":
        user_input = prev_user_input
    
    if user_input=="t":
        camera.capture("Template/Backlight/template"+str(count_t)+".jpg")
        count_t += 1

    elif user_input=="s":
        camera.capture("Under_Test/Backlight/scene"+str(count_s)+".jpg")
        count_s += 1
    
    
    # backlight_off()
    # pcb_lighting_off()

    prev_user_input = user_input

