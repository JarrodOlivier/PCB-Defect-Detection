# https://docs.opencv.org/3.4/df/d0d/tutorial_find_contours.html
import cv2 as cv
import numpy as np
# https://docs.python.org/3/library/csv.html
import csv
from BCOLOURS import bcolors


def components_and_contours(threshold_image, debug=False):
    """
    Draws contours around all artfifacts in threshold image, further obtaining bounding rectangles
    in addition writes the coordinates of the bounding rectangles to a `rects.csv` and `rects.png`
    
    @returns: len(contours)
    @output: rects.csv, rects.png
    """ 
    print(f"{bcolors.HEADER}Stage 3{bcolors.ENDC}")
    
    scn = cv.imread(threshold_image,0)

    _, out = cv.threshold(scn,254,255,cv.THRESH_BINARY)
    out = cv.bitwise_not(out)

    # cv.namedWindow("Inv", cv.WINDOW_GUI_EXPANDED)
    # cv.namedWindow("Mor", cv.WINDOW_GUI_EXPANDED)
    # cv.imshow("Inv", out)
    out = cv.dilate(out,(9,9), iterations=3)
    # cv.imshow("Mor", out)

    contours, _ = cv.findContours(out, cv.RETR_EXTERNAL ,cv.CHAIN_APPROX_SIMPLE)

    # Creates a black image to draw contours onto. 
    out = np.zeros((out.shape[0], out.shape[1], 3), dtype=np.uint8)
    out = cv.imread("Assets/scnCOM.png")
    if len(contours) > 0:
        # Writes to csv while drawing to file
        with open("Files/rects.csv","w",newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["x0"]+["y0"]+["x1"]+["y1"])
            for i in range(len(contours)):
                rect = cv.boundingRect(contours[i])
                writer.writerow([rect[0]]+[rect[1]]+[rect[0]+rect[2]]+[rect[1]+rect[3]])

                # https://stackoverflow.com/questions/23398926/drawing-bounding-box-around-given-size-area-contour
                # NOTE: draws yellow rectanle around contour
                cv.rectangle(out,rect, color=(0,255,255), thickness=2)

        if (debug == True):
            cv.namedWindow("out", cv.WINDOW_GUI_EXPANDED)
            cv.imshow("out", out)
            cv.waitKey(0)
            cv.destroyAllWindows()

        cv.imwrite("Assets/rects.png",out)

        print(f"{bcolors.OKBLUE} Written rects.png and rects.csv to Assets, Files directories respectively.\n \
            Proceeding to next stage... {bcolors.ENDC}")

    else:
        print(f"{bcolors.OKGREEN} NO DEFECTS DETECTED, Proceeding to next stage...{bcolors.ENDC}")


    return len(contours)

if __name__ == "__main__":
    components_and_contours("Assets/threshold.png", False)
    cv.waitKey(0)