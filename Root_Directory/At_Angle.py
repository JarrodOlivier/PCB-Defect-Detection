import cv2 as cv
import numpy as np

def angle_processing(img, angle, square):
    
    img_name = img
    x0 = "x0"
    y0 = "y0"
    x1 = "x1"
    y1 = "y1"

    img = cv.imread(img)
    height, width, _ = img.shape
    diagonal = int(np.ceil(np.hypot(height, width)))
    # offset values to place img in new image
    # https://stackoverflow.com/questions/58248121/opencv-python-how-to-overlay-an-image-into-the-centre-of-another-image
    (ho, wo) = (round((diagonal-height)/2), round((diagonal-width)/2))
    # Create a square image, the size of the diagonals of the original image
    image = np.zeros((diagonal,diagonal,3), np.uint8)
    # Place the original image in the center of the new square image
    # image[int(ho-10.5/7):int((ho+height)+10.5/7), int(wo-10.5/7):int((wo+width)-10.5/7)]# = iut
    image[int(ho):int(ho+height), int(wo):int(wo+width)]  = img
    
    ih, iw, _ = image.shape
    image_center = (ih//2,iw//2)
    # https://stackoverflow.com/questions/9041681/opencv-python-rotate-image-by-x-degrees-around-specific-point
    rot_mat = cv.getRotationMatrix2D(image_center,angle,1.0)
    # integer division

    coords = (int(((ho+height) - ((ho+height)/np.sqrt(2)))/2), int(((wo+width) - ((wo+width)/np.sqrt(2)))/2))
    rotate_image = cv.warpAffine(image, rot_mat, image.shape[1::-1],flags=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT )
    # Note: resing won't work on components that are not square
    # This is what this check does
    if square:
        x0 = wo + coords[1]
        y0 = ho + coords[0]
        x1 = int((wo+width)/np.sqrt(2)) + coords[1]
        y1 = int((ho+height)/np.sqrt(2)) + coords[0]
        resize_image = rotate_image[y0:y1, x0:x1]
        cv.imwrite(img_name, rotate_image)
        # cv.imwrite(img_name, resize_image)
        # return [x0,y0,x1,y1]
    else:
        # x0 = wo + coords[1]
        # y0 = ho + coords[0]
        # x1 = int(wo+width) + coords[1]
        # y1 = int(ho+height) + coords[0]
        resize_image = rotate_image[ho:int(ho+height), wo:int(wo+width)]
        # cv.imwrite(img_name, resize_image)
        cv.imwrite(img_name, rotate_image)
        # return None

def at_angle(iut, tmp, angle=45, square=False):
    scn_name = iut
    tmp_name = tmp
    angle_processing(scn_name,angle,square)
    angle_processing(tmp_name,angle,square)
    iut = cv.imread(iut)
    tmp = cv.imread(tmp)
 
if __name__ == "__main__":
    # at_angle("POI/0.png",0, sqaure=True)
    at_angle("COM/0.png", "POI/0.png", 45, square=True)
