import cv2 as cv
import numpy as np
# from skimage.measure import compare_ssim
from BCOLOURS import bcolors


def thresholding(difference_image, debug=False):
    """
    Takes the `difference_image` from the last stage and applies a threshold to remove
    as much artifacts as possible, while keeping all defects.
    
    
    @returns: None

    @output: threshold.jpg
    """
    print(f"{bcolors.HEADER}Stage 2{bcolors.ENDC}")
    
    try:
        diff = cv.imread(difference_image)
        # raising an AttributeError if the image cannot be found, this is handles below
        if diff.any() == None:
            raise AttributeError
        
        cv.imshow("diff1", diff)
        diff = cv.medianBlur(diff,11)
        cv.imshow("diff2", diff)

        # ret3,out = cv.threshold(diff,80,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C)
        ret3,out = cv.threshold(diff,65,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C)

        cv.imwrite("Assets/threshold.png", out)

        if (debug==True):
            #NOTE: creating a trackbar for the window
            max_thres = 255
            trackbar_name = "Threshold Value:"
            window_title = "output"

            def on_trackbar(val):
                thres = val
                ret3,out = cv.threshold(diff,thres,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C)
                cv.imshow(window_title,out)

            cv.namedWindow(window_title, cv.WINDOW_GUI_NORMAL)
            cv.createTrackbar(trackbar_name, window_title, 0, max_thres, on_trackbar)

            on_trackbar(0)

            cv.waitKey(0)
            cv.destroyAllWindows

        print(f"{bcolors.OKBLUE} Written threshold.png to Assets directory.\n \
            Proceeding to next stage... {bcolors.ENDC}")

    except AttributeError as e:
        print(f"{bcolors.FAIL}FAIL! One or more images not found, Exiting...{bcolors.ENDC}")

if __name__ == "__main__":
    cv.namedWindow("diff1", cv.WINDOW_GUI_NORMAL)
    cv.namedWindow("diff2", cv.WINDOW_GUI_NORMAL)
    thresholding("Assets/difference.png", False)
    cv.waitKey(0)