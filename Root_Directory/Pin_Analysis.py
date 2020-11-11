from PIL import Image
import cv2 as cv
import numpy as np

def grab_pins(ic):
    """
    Adds extra pixles to COM/POI image under analysis such that pins are included.
    This and following function provide analysis of solder joint of multipin components
    
    @input: ic (row from dict)
    @output: writes images (with pins) to Assets dir
    """
    center_x = (int(ic["x0"]) + int(ic["x1"]))/2
    center_y = (int(ic["y0"]) + int(ic["y1"]))/2

    height = abs(int(ic["y1"]) - int(ic["y0"]))
    width = abs(int(ic["x1"]) - int(ic["x0"]))

    # Dimension of LQFP32 with extra width to allow for wider solder pads
    D = 10.5
    D1 = 7 
    height_outer = (D/D1) * height
    width_outer = (D/D1) * width

    # offset values from center
    ic["ox0"] = int(center_x - width_outer/2)
    ic["ox1"] = int(center_x + width_outer/2)
    ic["oy0"] = int(center_y - height_outer/2)
    ic["oy1"] = int(center_y + height_outer/2)

    scn = Image.open("Assets/scn_masked.png")
    tmp = Image.open("Assets/tmp_masked.png")

    scn.crop((ic["ox0"], ic["oy0"], ic["ox1"], ic["oy1"])).save("Assets/scn_pins.png")
    tmp.crop((ic["ox0"], ic["oy0"], ic["ox1"], ic["oy1"])).save("Assets/tmp_pins.png")

def pin_analysis(iut, tmp, debug=False):
    """
    Analysis of multipin component pins, specifically looking for solder joints
    """
    scn = cv.imread(iut,0)
    tmp = cv.imread(tmp,0)

    try:
        # b, g, r = cv.split(scn)
        # _, _, rt = cv.split(tmp)
        h, w, _ = tmp.shape
    except Exception as _:
        h, w = tmp.shape

    # tweaking/morphology
    diff = cv.absdiff(scn,tmp)
    _, threshold = cv.threshold(diff, 80, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C)
    # defect = diff
    defect = cv.bitwise_not(threshold)
    # defect = cv.morphologyEx(threshold, cv.MORPH_ERODE, (9,9), iterations=2)
    # defect = cv.morphologyEx(defect, cv.MORPH_CLOSE, (9,9), iterations=2) 
    defect = cv.morphologyEx(defect, cv.MORPH_DILATE, (9,9), iterations=2)
    # defect = cv.morphologyEx(defect, cv.MORPH_CLOSE, (9,9), iterations=2)

    contours, _ = cv.findContours(defect, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

    rects = []
    for i in range(len(contours)):
        rect = cv.boundingRect(contours[i])
        rects.append(rect)

    D = 10.5
    D1 = 7 
    defects = [] #bridges
    out = np.zeros((defect.shape[0], defect.shape[1], 3), dtype=np.uint8)
    for rect in rects:
        # a rough check to see if defects are larger than 3x3 pixels
        if rect[2] > 3 and rect[3] > 3:
            # left and right edge of image
            if ( rect[1] < 0.3*w) or ( rect[1] > 0.7*w ):
                # height defect greater than value
                if rect[2] > (0.45/D)*w:
                    # print(rect)
                    defects.append(rect)
                    cv.rectangle(out,rect, color=(0,255,255), thickness=2)
            # Remaining defects
            else:
                # width of defect > value
                if rect[3] > (0.45/D)*w:
                    # print(rect)
                    defects.append(rect)
                    cv.rectangle(out,rect, color=(0,255,255), thickness=2)
    print(rects)
    if debug:
        cv.imshow("scn", scn)
        cv.imshow("tmp", tmp)
        # cv.imshow("thres", thres)
        cv.imshow("defect", defect)
        cv.namedWindow("out", cv.WINDOW_GUI_EXPANDED)
        cv.imshow("out", out)

        cv.waitKey(0)

    if len(defects) > 0:
        return 10
    else:
        return 9

    

if __name__ == "__main__":
    # pin_analysis("IS4/tmpR1.jpg", "IS4/tmpR2.jpg", False)
    pin_analysis("POI/0.png", "COM/0.png", True)
