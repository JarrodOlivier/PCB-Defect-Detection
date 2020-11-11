import Cleanup

from multiprocessing import process
from Cleanup import partial_cleanup
from Image_Preparation import image_prepartion
from Thresholding import thresholding
from Components_and_Contours import components_and_contours
from BBox_overlap import bbox_overlap
from At_Angle import at_angle

from Rotation import rotation_angle
from Ssim_Compare import ssim_compare
from Component_Detection import component_detection
from Pin_Analysis import grab_pins, pin_analysis
from At_Angle import at_angle

import csv
import multiprocessing
import threading
import time
import cv2 as cv

def component_defect_classification(i, state, row, poi_rows):
    i = row["poi_id"]
    print("\nROI no.: {}".format(i))            
    com = "COM/"+str(i)+".png"
    poi = "POI/"+str(i)+".png"
    bor = "POI/BOARD/"+str(i)+".png"

    # type casted for surety
    case = int(row["type"])
    type = int(row["type"])

    # image coords
    poi_elem = poi_rows[int(i)]
    x0 = int(poi_elem["x0"])
    y0 = int(poi_elem["y0"])
    image =cv.imread("Assets/scnCOM.png")


    try:
        # CHECK ROTATION
        # print("1st Rotation Stage")
        angle, state = rotation_angle(com,poi,case=case)
        # print("Rotation: {}, State: {}".format(angle,state))
    except Exception as e:
        print(f"{e} \n\n\nChecking component rotation Failed (@Rotation.py)")
        state = -3

    if type != 0:
        try:
            # CHECK STRUCTURAL IMAGE SIMILARITY (This is robustness check to confirm the previous check)
            # print("1st SSIM Stage")
            state = ssim_compare(com, poi, bor, state)
            # print("SSIM State: {}".format(state))
        except Exception as e:
            print(f"{e} \n\n\nChecking component ssim Failed (@Ssim.py)")
            state = -3
    
    try:
        # CHECK TEXT (OCR) IDENTIFICATION
        print("1st OCR Stage")
        x,y,z = component_detection(com, poi)
        print("Text: {}, poi: {}, com: {}".format(x,y,z))
    except Exception as e:
        print(f"{e} \n\n\nChecking component label failed (@Component_Detection.py)")
        state = -3


    cv.namedWindow("Image",  cv.WINDOW_GUI_NORMAL)
    fontface = cv.FONT_HERSHEY_SIMPLEX
    fontscale = 3
    fontcolor = (255, 0, 255)
    # https://stackoverflow.com/questions/16615662/how-to-write-text-on-a-image-in-windows-using-python-opencv2



    if state == -3:
        print("Unknown Defect")
        cv.putText(image,"UK", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass
    elif state == 0 or state == 2:
        print("No Defect")
        cv.putText(image,"NO", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass
    elif state == 1:
        print("Twisted Component")
        cv.putText(image,"TC", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass
    elif state == 3:
        print("Opposite Polarity")
        cv.putText(image,"OP", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass
    elif state == 6 or state == 4:
        print("Component Rotated (uncertain)")
        cv.putText(image,"RC", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
    elif state == 71 or state == 7:
        print("Wrong Component")
        cv.putText(image,"WC", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass
    elif state == 81 or state == 8:
        print("Missing Component")
        cv.putText(image,"MC", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass

    cv.imwrite("Assets/scnCOM.png",image)
    


    #  *** ICs/uC/ Multipins
    # Only run grab_pins if IC in NOT rotated (remove At_Angle.py)
    if case == 2:
        # uses masked images in Assets/*.png (created in BBox.py)
        grab_pins(row)
        state = pin_analysis("Assets/scn_pins.png", "Assets/tmp_pins.png")
        # state = pin_analysis(com, poi)
        print("Bridged pins: {}".format(state))

    # at angle, the masked images are not used.
    # TODO:move this to under BBOX?
    if 3 <= case <= 4:
        if case == 3: 
            at_angle(com, poi, square=False)
        
        # For square components
        elif case == 4:
            at_angle(com, poi, square=True)
        state = pin_analysis(com, poi)
        print("Bridged pins: {}".format(state))
    
    if  state == 10:
        print("Bridge Pins")
        cv.putText(image,"BP", (x0,y0), fontface, fontscale, fontcolor, thickness=3)
        pass

    cv.imwrite("Assets/scnCOM.png",image)


if __name__ == "__main__":

    debug = False
    # TODO NOTE: Remove this check in final product, this is check is used to disable reanalysing
    # the images
    if not debug:
        partial_cleanup()
        
        # ***TEMPLATE IMAGES***
        template_file_name = "IS4/Template/template0.jpg"
        bare_board_file_name = "IS4/Template/template1.jpg"

        # template_file_name = "IS4/tmpR1.jpg"
        # bare_board_file_name = "IS4/Template/template1.jpg"

        #  ***SCENE IMAGES***
        # image_under_test_file_name = "IS4/tmpR2.jpg"
        image_under_test_file_name = "IS4/Under_Test/scene3.jpg"
        
        #  ***DATA PREPARATION***
        image_prepartion(image_under_test_file_name, template_file_name)
        thresholding("Assets/difference.png")
        components_and_contours("Assets/Threshold.png")
        try:
            bbox_overlap("Assets/scnCOM.png", template_file_name, bare_board_file_name)
        except Exception as _:
            print("No Component Defects")

    start = time.perf_counter()
    # POI are all components identified by the user through the GUI
    poi_rows = []
    # ROI are all the components which have a difference detected between template and image under test.
    roi_rows = []

    # ******************************************************************************************************************
    # *** CLASSIFYING COMPONENT DEFECTS ***
    # ******************************************************************************************************************
    
    print("*** CLASSIFYING ALL COMPONENT DEFECTS ***")
    with open("Files/poi.csv", newline='') as poi_csv:
        dict_reader = csv.DictReader(poi_csv, delimiter=',', quotechar='|')
        for row in dict_reader:
            poi_rows.append(row)
    
    proceed = True
    try:
        # If this does file not exist, it is assumed there are no defects.
        with open("Files/roi.csv", newline='') as roi_csv:
            dict_reader = csv.DictReader(roi_csv, delimiter=',', quotechar='|')
            for row in dict_reader:
                roi_rows.append(row)

    except Exception as _:
        proceed = False
    
    if proceed:
        # https://www.youtube.com/watch?v=fKl2JW_qrso
        # comp_count = len(poi_rows)
        comp_count = len(roi_rows)
        iter = 0 
        state = -3

        # select parallel type
        mp = 0
        
        # ***Multiprocessing***
        if mp == 1:
            cores = multiprocessing.cpu_count()
            while iter != comp_count:
                processes = []
                # start no. of cores processes
                for _ in range(cores):
                    #if the number of components is greather than the number of cores 
                    # then pass - the loop will exit on the next iteration
                    if iter == comp_count:
                        pass
                    else:
                        # start proccess
                        p = multiprocessing.Process(target=component_defect_classification, args=[iter, state, poi_rows[iter]])
                        p.start()
                        processes.append(p)
                        iter += 1
                
                for proc in processes:
                    proc.join()
                
        # ***Multithreading***
        elif mp == 0:
            while iter != comp_count:
                threads = []
                # start 8 threads
                for _ in range(8):
                    # if the number of components is greather than the number of threads
                    # then pass - the loop will exit on the next iteration
                    if iter == comp_count:
                        pass
                    else:
                        # start proccess
                        t = threading.Thread(target=component_defect_classification, args=[iter, state, roi_rows[iter], poi_rows])
                        t.start()
                        threads.append(t)
                        iter += 1
                
                    for thread in threads:
                        thread.join()

    finish = time.perf_counter()
                

    print("Time Taken: {}".format(finish - start))