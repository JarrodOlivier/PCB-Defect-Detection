import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from BCOLOURS import bcolors


def feature_matching(algorithm, iut, tmp):
    min_match = 10
    kp1, des1 = algorithm.detectAndCompute(iut,None)
    kp2, des2 = algorithm.detectAndCompute(tmp, None)

    bf = cv.BFMatcher()
    # k is number of best matches 
    matches = bf.knnMatch(des1,des2, k=2)

    good_matches = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good_matches.append(m)

    if len(good_matches)>min_match:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
        M, mask = cv.findHomography(src_pts, dst_pts, cv.LMEDS, 5.0, confidence=0.95)
    
    # Unbound to force an error if M cannot be generated out of "good_matches" matches
    return M

def resize(img, scale, interpolation=cv.INTER_AREA):
    """
    @param1 = image source\n
    @param2 = scale factor, between 0 and 1\n
    @param3 = interpolation method (default = cv2.INTER_AREA)\n

    @return resized image
    """
    height = int(img.shape[0]*scale)
    width = int(img.shape[1]*scale)

    dim = (width, height)
    resize_img = cv.resize(img,dim,interpolation=interpolation)
    return resize_img

def image_prepartion(
    image_under_test, 
    template_image, 
    scale=1, 
    min_match=10,
    resize_img=False,
    ):
    """
    Given a template PCB image and a similar scene image or "image under test", 
    the two images  are compared and matching features are identified.
    
    
    @returns: None

    @output: transformed image_under_test, difference `absdiff` image (two png's)
    """

    print(f"{bcolors.HEADER}Stage 1{bcolors.ENDC}")

    scene_img = cv.imread(image_under_test)
    template_img = cv.imread(template_image)

    # Cannot load image
    if scene_img.any() == None or template_img.any() == None:
        raise FileNotFoundError
    # scene_img = resize(scene_img,scale)
    # template_img = resize(template_img,scale)

    
    try:
        brisk = cv.BRISK_create()
        M = feature_matching(brisk, scene_img, template_img)
    except Exception as e:
        print(e)
        print("Trying SIFT algorithm")
        sift = cv.SIFT_create()
        M = feature_matching(sift, scene_img, template_img)
    
    # Get dimensions, depending on image type (RGB, grayscale)
    try:
        # RGB Images (3 Channel)
        h,w,_ = template_img.shape
    except ValueError as e:
        print(f"{bcolors.WARNING}Warning: {e}, trying 2 values {bcolors.ENDC}")
        # Greyscale Images (1 Channel)
        h,w = template_img.shape
        print(f"{bcolors.OKGREEN}Success, Continuing... {bcolors.ENDC}")

    out = cv.warpPerspective(scene_img,M,(w,h))
    # The aligned *image under test* board to template board
    cv.imwrite("Assets/scnCOM.png", out)

    out = cv.absdiff(template_img,out)

    cv.imwrite("Assets/difference.png", out)
    print(f"{bcolors.OKBLUE} Written scnCOM.png and difference.png to Assets directory.\n \
        Proceeding to next stage... {bcolors.ENDC}")

if __name__ == "__main__":
    i1 = "IS1\\ICa.jpg"
    i2 = "IS1\\IC_defect.jpg" 
    image_prepartion(i2,i1)