import csv
import numpy as np
# NOTE: ImageDraw and ImageColor used for masking out components
from PIL import Image, ExifTags, ImageDraw, ImageColor  

def check_rotation(image):
    """
    Checks if `image` is rotated based on *exif tags* (Required for PIL)
    NOTE: (GUI name should change) check `alt_main_csv.py` orig. impl of this
    It appears openCV take exif data into account, and swithcing to this library may be better  
    """
    try:
        exif = dict((ExifTags.TAGS[k], v) for k, v in image._getexif().items() if k in ExifTags.TAGS)
        if exif['Orientation'] == 6:
            image = image.rotate(-90, expand=True)
        elif exif['Orientation'] == 5:
            image = image.rotate(90, expand=True)
    except Exception as e:
                print("{},\n\n\n EXIF data not available.".format(e))
    finally:
        print("Proceeding...")

def bbox_overlap(image_under_test, template_image, bare_board):
    """
    checks what contours from `rects.csv` (created in the previous stage) falls in the coordinates
    given in `poi.csv` (created in the GUI).

    The coordinates given in `poi.csv` are cropped out of both the 
    `template_image` and `image_under_test` and stored in \POI and \COM respectively 
    such that all the components are isolated.

    @returns: None
    @output: \COM\*.jpg, \POI\*.jpg
    """
    image = Image.open(template_image)
    scn_im = Image.open(image_under_test)
    bare_board = Image.open(bare_board)

    # reads Exif data to determine if the image was rotated before being processed
    check_rotation(image)
    check_rotation(scn_im)
    check_rotation(bare_board)
    
    x0 = "x0"
    x1 = "x1"
    y0 = "y0"
    y1 = "y1"

    pois = []
    rects =[]

    with open('Files/poi.csv', newline='') as poi_csv:
        dict_reader = csv.DictReader(poi_csv, delimiter=',', quotechar='|')
        i = 0
        for row in dict_reader:
            row["id"] = i
            i += 1
            pois.append(row)
            # print(row)

    with open('Files/rects.csv', newline='') as rects_csv:
        dict_reader = csv.DictReader(rects_csv, delimiter=',', quotechar='|')
        i = 0
        for row in dict_reader:
            row["id"] = i
            i += 1
            rects.append(row)
            # print(row)


    rois = []
    #NOTE: POI are the poi from the GUI
    #NOTE: rects are the poi (bboxes) from the threshold image (part 3)
    # Nested for loop: Checks every contour against every component (roi from GUI), if it is within the bbox of the 
    # component the contour is popped out from the list of contours.
    # 
    # Contour is within bbox 
    # if the TL cont. coord < BR poi coord
    # and
    # if the BR cont. coord > TL poi coord
    for poi in pois:
        # numpy libray is used to store the coord as it presevers element bools
        # has .any() or all() funtion to test against all elements states
        tl_poi =  np.array([int(poi[x0]),int(poi[y0])])
        br_poi =  np.array([int(poi[x1]),int(poi[y1])])

        # Save ROIs image 
        coords = (int(poi[x0]),int(poi[y0]),int(poi[x1]),int(poi[y1]))
        coords2 = [int(poi[x0]),int(poi[y0]),int(poi[x1]),int(poi[y1])]
        
        # Folders created in cleanup
        image_poi = image.crop(coords)
        image_poi.save("POI/"+str(poi["id"])+".png")
        
        # Save the bare board PCB image
        bare_poi = bare_board.crop(coords)
        bare_poi.save("POI/BOARD/"+str(poi["id"])+".png")

        # Template image mask
        tmp_masked = ImageDraw.Draw(image)
        tmp_masked.rectangle(xy=coords2, fill=(0,0,0))

        # poi_under test (crops the scene image, using same coords)
        poi_ut = scn_im.crop(coords)
        poi_ut.save("COM/"+str(poi["id"])+".png")
        
        # Scene image mask
        scn_masked = ImageDraw.Draw(scn_im)
        scn_masked.rectangle(xy=coords2, fill=(0,0,0))
        
        # checks if rect falls within POI bboxes
        for rect in rects:
            # bottom right _ respective
            br_rect = np.array([int(rect[x1]),int(rect[y1])])
            tl_rect = np.array([int(rect[x0]),int(rect[y0])])
            # results stored in `r1` and `r2`
            r1 = tl_rect < br_poi
            r2 = br_rect > tl_poi
            if r1.all() and r2.all():
                rect["type"] = poi["type"]
                # appends intersecting poi with rect to form roi. 
                rect["poi_id"] = poi["id"]
                # poi height, width
                rect["poi_h"] = int(poi["y1"])-int(poi["y0"])
                rect["poi_w"] = int(poi["x1"])-int(poi["x0"])
                rois.append(rect)
    # print(rois)    
    # [{'x0': '881', 'y0': '497', 'x1': '914', 'y1': '547', 'id': 17, 'type': '0', 'poi_id': 2, 'poi_h': 94, 'poi_w': 45}] 
    
    image.save("Assets/tmp_masked.png")
    scn_im.save("Assets/scn_masked.png")

    # NOTE: The following `for` loop calculates the area of the defects (`rect`) per ROI 
    # as well as the area of the ROI
    u_id = 0
    a = 0
    area = []
    prev_poi_id = rois[0]["poi_id"] 
    for roi in rois:
        poi_id = roi["poi_id"]
        h = (int(roi["y1"])-int(roi["y0"]))
        w = (int(roi["x1"])-int(roi["x0"]))

        # checks `if` roi part of the same POI or if it's the last element in the `rois` array.
        if (poi_id != prev_poi_id) or (roi == rois[-1]):
            # NOTE: (This has changed) this check above is *true* once the `poi_id` has changed however the area applies to the prev `poi_id`
            # this is rectified (decremented) in the `area` dictionary below. BUT the last element applies to 
            # the last `poi_id` and should NOT be decremented 
            if roi == rois[-1]:
                # The last region area would not be calculated otherwise
                h = (int(roi["y1"])-int(roi["y0"]))
                w = (int(roi["x1"])-int(roi["x0"]))
                a += h*w 

            poi_area = int(roi["poi_h"]) * int(roi["poi_w"])
            intersection = (a/poi_area)*100
            print("a: {}, poi_area: {}".format(a,poi_area))
            area.append({
                "roi_area":a,
                "poi_area":poi_area,
                "intersection":intersection,
                "poi_id":prev_poi_id,
                "type": roi["type"]
                })
            u_id += 1
            a = 0
        
        # cumulative area
        a += h*w
        
        prev_poi_id = roi["poi_id"]

        
    
    # Writes a `roi.csv` file which contains the 
    # ROI_id's which have differences from the tmp/scn
    # comaprison. Contains the intersection percentage as well.
    with open("Files/roi.csv","w",newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["intersection"]+["poi_id"]+["type"])
            for roi in area:
                writer.writerow([roi["intersection"]]+[roi["poi_id"]]+[roi["type"]])

if __name__ == "__main__":

    template_file_name = "IS4/Template/template0.jpg"
    bare_board_file_name = "IS4/Template/template1.jpg"
    image_under_test_file_name = "IS4/Under_Test/scene2.jpg"
    bbox_overlap(template_file_name, image_under_test_file_name, bare_board_file_name )