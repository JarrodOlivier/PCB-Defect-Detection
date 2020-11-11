import cv2 as cv
import matplotlib.pyplot as plt
# from skimage import data, img_as_float
from skimage.metrics import structural_similarity as ssim

def ssim_compare(iut, tmp, bor, state):
    """
    Compares the COM/*.png and POI/*.png for their similarity.

    @state (int), following from previous function


    """

    scn = cv.imread(iut)
    tmp = cv.imread(tmp)

    scn =  cv.GaussianBlur(scn,(9,9),0)
    tmp =  cv.GaussianBlur(	tmp,(9,9),0)


    ssim_value0 = ssim(tmp, scn, multichannel=True)

    # check if tmp is more structurally similar to the 180deg rotated poi 
    # for state where poi is *not* rotated from prev. test
    if state == 0:
        scn = cv.rotate(scn, cv.ROTATE_180)
        ssim_value1 = ssim(tmp, scn, multichannel=True)
        # print("SSIM values: {}, {}".format(ssim_value0, ssim_value1))
        if ssim_value0 > ssim_value1:
            return 5
        elif ssim_value0 <= ssim_value1:
            return 6

    # for state where poi *is* rotated from prev. test
    elif state == 2:
        scn = cv.rotate(scn, cv.ROTATE_180)
        ssim_value1 = ssim(tmp, scn, multichannel=True)
        # print("SSIM values: {}, {}".format(ssim_value0, ssim_value1))
        if ssim_value1 > ssim_value0:
            return 3
        elif ssim_value1 <= ssim_value0:
            return 4

    elif state == -3:
        scn = cv.imread(bor)
        scn =  cv.GaussianBlur(scn,(9,9),0)
        ssim_value1 = ssim(tmp, scn, multichannel=True)
        # print("SSIM values: {}, {}".format(ssim_value0, ssim_value1))
        if ssim_value1 > ssim_value0:
            return 81
        elif ssim_value0 > ssim_value1:
            return 71


if __name__ == "__main__":
    # ssim_mse("POI/4.png", "POI/4.png", False)
    print(ssim_compare("COM/0.png", "POI/0.png","POI/BOARD/0.png", 0))    