import picamera
import RPi.GPIO as GPIO
from Backlight import backlight, backlight_off
from Pcb_Lighting import pcb_lighting, pcb_lighting_off
import time
from Cleanup import cleanup
import time as t

initial_time = t.perf_counter()

def capture_image(ct, cs, user_input, bl=False):
    
    count_t = ct
    count_s = cs
        
    if bl==False:
        if user_input=="t":
            camera.capture("Template/template"+str(count_t)+".jpg")

        elif user_input=="s":
            camera.capture("Under_Test/scene"+str(count_s)+".jpg")
    else:
        if user_input=="t":
            camera.capture("Template/Backlight/template_bl"+str(count_t)+".jpg")
            count_t += 1

        elif user_input=="s":
            camera.capture("Under_Test/Backlight/scene_bl"+str(count_s)+".jpg")
            count_s += 1

    return count_t, count_s

camera = picamera.PiCamera()
# https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7
camera.resolution = (2592, 1944)
camera.framerate = 15

# runs cleanup function found in `Cleanup.py`, used to remove previous capture run.
cleanup()

# ***
prev_user_input = "t"
count_t = 0
count_s = 0
try:
    while (True): 
        user_input = input("Take Image?").lower()

        # Designed so that Enter Key, "t", "s", "yes" or "y" proceeds eveyting else will exit.
        if ((user_input=="t") or (user_input=="s") or (user_input=="yes") or (user_input=="y")):
            pass
        elif user_input=="":
            user_input = prev_user_input
        else:
            break

        # NOTE: `backlight` is an inverse function and the output turns the backlight off
        backlight()
        pcb_lighting()

        camera.brightness = 43
        # camera.brightness = 40
        camera.contrast = 35
        camera.image_effect = "none"
        camera.exposure_mode = "off"
        camera.exposure_compensation = 12
        camera.awb_mode = "off"
        camera.awb_gains = (1.661, 1.220)#(1.961, 1.520) # rg gain, bg gain
        # camera.awb_gains = (1.961, 1.520) # rg gain, bg gain
        
        # Allows camera gains (digital, analog) to settle
        time.sleep(2.5)
        _, _ = capture_image(count_t,count_s,user_input=user_input)
 
        backlight_off()
        pcb_lighting_off()

        time.sleep(2.5)
        count_t, count_s = capture_image(count_t, count_s, user_input=user_input,bl=True)
        
        prev_user_input = user_input

        final_time = t.perf_counter()

except Exception as e:
    print("{} \nCapture Ended With Raised, System-exiting Exception".format(e))
# https://www.geeksforgeeks.org/finally-keyword-in-python/
finally:
    print("\nExiting Capture...\n")
    camera.close()
    backlight_off()
    pcb_lighting_off()
    GPIO.cleanup()

    time_taken = final_time - initial_time

    print("Time taken: {}".format(time_taken))