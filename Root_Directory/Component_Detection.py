import cv2 as cv
import pytesseract as pt

def comp_morpohology(img, h, w):
    """
    The morphological operations which resulted in the clearest (most accurate) text
    detection from the SMT components using Tesseract
    """
    # TODO: calibrate these values
    img = img[10:h-10, 30:w-30]
    img = cv.bitwise_not(img)
    img = cv.morphologyEx(img, cv.MORPH_OPEN, (9,9), iterations=2)

    return img

def component_detection(com, poi, debug=False):
    """
    Scans component (image) for text and stores the result in a csv of the value it captures.
    NOTE: The image is cropped in from the ROI/COM that it receives.

    @output: appening value to csv.
    """ 
    com = cv.imread(com,0)
    poi = cv.imread(poi,0)

    # Both com/ poi will have same dimensions
    h,w = com.shape
    # If component lies vertical relative to the image rotate 90deg as the Tesseract config
    # is not calibrated/trained for vertical text.
    if (h>w):
        com = cv.rotate(com, cv.ROTATE_90_CLOCKWISE)
        poi = cv.rotate(poi, cv.ROTATE_90_CLOCKWISE)
    # recapture image dimensions
    h,w = com.shape
    
    com = comp_morpohology(com, h, w)
    poi = comp_morpohology(poi, h, w)

    com_text = pt.image_to_string(com, lang='eng+equ', config="--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789")
    poi_text = pt.image_to_string(poi, lang='eng+equ', config="--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789")

    # if Tesseract cannot detect any text try again after rotating 180deg. 
    if com_text.split() == []:
        com = cv.rotate(com, cv.ROTATE_180)
        com_text = pt.image_to_string(com, lang='eng+equ', config="--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789")

    if poi_text.split() == []:
        poi = cv.rotate(poi, cv.ROTATE_180)
        poi_text = pt.image_to_string(poi, lang='eng+equ', config="--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789")


    if debug:
        cv.imshow("com", com)
        cv.imshow("poi", poi)
        print("COM:{}\nPOI:{}".format(com_text, poi_text))
        cv.waitKey(0)


    if poi_text.split() == com_text.split():
        return 7, poi_text, com_text
    else:
        return 8, poi_text, com_text

if __name__ == "__main__":
    component_detection("IS5/Under_Test/s3300.jpg","IS5/Template/t3300.jpg", True)