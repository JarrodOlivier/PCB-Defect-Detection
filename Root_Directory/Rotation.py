import cv2 as cv
import numpy as np
from BCOLOURS import bcolors
# *********************************************

def rotation_angle(com, poi, debug=False, case=-1):
    """
    Find rotation angle between com image (/COM/*.png) and poi image (/COM/*.png)
    state == rotated 2, not rotated 0 or error -1
    @return: (rotation_angle, state)
    """
    scene_img = cv.imread(com)
    template_img = cv.imread(poi)

   
    # NOTE: Switched to ORB from this resource  (if using LMEDS, RANSAC):
    # https://stackoverflow.com/questions/48673104/how-to-detect-rotated-object-from-image-using-opencv
    # NOTE: Switched back to BRISK (for RHO method) see Jup notebook
    # NOTE: BRISK has poor results with a 90deg rotation switched back to ORB
    # NOTE: **USE SIFT with small images, ORB and other might not find features
    sift = cv.SIFT_create()

    # kp => keypoints 
    # des => descriptors
    kp1, des1 = sift.detectAndCompute(scene_img,None)
    kp2, des2 = sift.detectAndCompute(template_img, None)

    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    # Try force the generation of the transformation matrix.
    # if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
   
    try:
        # NOTE: search for these methods (cv.RHO)
        # https://docs.opencv.org/4.4.0/d9/d0c/group__calib3d.html#ga4abc2ece9fab9398f2e560d53c8c9780
        # M, mask = cv.findHomography(src_pts, dst_pts, cv.LMEDS,5.0, confidence=0.95)
        M, _ = cv.findHomography(src_pts, dst_pts, cv.RHO)#,confidence=0.95)
        # Calculate inverse matrix from M to Mi
        Mi = np.linalg.inv(M)

        try:
            # RGB Images (3 Channel)
            h,w,_ = template_img.shape
        except ValueError as e:
            print(f"{bcolors.WARNING}Warning: {e}, trying 2 values {bcolors.ENDC}")
            # Greyscale Images (1 Channel)
            h,w = template_img.shape
            print(f"{bcolors.OKGREEN}Success, Continuing... {bcolors.ENDC}")


        # NOTE: Rotation Here
        ss = Mi[1,0]
        sc = Mi[0,0]
        theta = np.arctan2(ss,sc)*(180/np.pi)
        
        theta = abs(theta)

        if (debug):
            out = cv.warpPerspective(scene_img, M, (w, h))
            # out = cv.warpAffine(scene_img,Ma,(w,h)) 
            out = cv.absdiff(template_img, out)
            cv.imwrite("Assets\\rotation.jpg", out)
            print("Homography Matrix:\n{}".format(M))
            print("Inverse Homography Matrix:\n{}".format(Mi))
            print("Rotation angle:\n{}".format(theta))
            print("WARNING: Check for min matches removed!")
        
        # Implement Classification stage:

        # https://stackoverflow.com/questions/9885217/in-python-if-i-return-inside-a-with-block-will-the-file-still-close
        # Only one of following are called (even if multiple are true)
        # Note `case` is an argument passed into the function 
        # that tells what type of component is being analysed (non-polarised, etc.)
        if theta > 178:
            return theta, 2
        # elif theta > 170 and int(case)==0:
        #     # case0: acceptable rotation
        #     return theta, 2
        elif theta < 2:
            # case1,2: accpetable rotation
            return theta, 0
        elif theta < 10 and int(case)==0:
            return theta, 0
        # below elif are classified defects.
        elif (10 < theta < 170):
            return theta, 1
        elif (2 < theta < 178):
            return theta, 1
        else:
            # Error
            return theta, -1 
    except Exception as e:
        pass
    #     print("{}.\nNot enough good matches".format(e))


if __name__ == "__main__":
    rotation_angle("IS4/4.png","IS4/4R.png", debug=True, case=0)