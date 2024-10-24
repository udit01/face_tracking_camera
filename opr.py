import cv2
import math
import common
import numpy as np
from scipy.spatial import KDTree
from model.DBFace import DBFace
from dbface_main import detect
import common
from collections import defaultdict

SHOW_FACES = True
SHOW_OBJECTS = True
SHOW_CENTER_CONFIDENCE = True 
# The higest confidence object will be plotted with the first color and so on...
# Can pick new colors here. Can also rank the ellipses with area and then plot them in descending order of area
# OR CAN ALSO track the object by IDS and then use that 
# https://www.w3schools.com/colors/colors_picker.asp
# I PICKED RGB and these are expected to be BGR.... so sad 
COLOR_ARRAY = [ (51, 204, 204), (255, 102, 255), (255, 102, 0), (42, 128, 0) ]
COLOR_COUNTER = 0 

MANUAL_COLOR = False 
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# INTENDED TO BE CALLED ONCE INSIDE the init function
def make_random_colors_array(num_colors=20):
    # REMOTE PREV array
    global COLOR_ARRAY
    COLOR_ARRAY = []
    for _ in range(num_colors):
        c1 = (np.random.random(size=1)[0]) * 256
        c1 = int(c1)
        color = (c1, c1, c1)
        COLOR_ARRAY.append(color)
    
    # Return nothing
def get_color(idx):
    return COLOR_ARRAY[idx%(len(COLOR_ARRAY))]

def remap(value_to_map, new_range_min, new_range_max, old_range_min, old_range_max):

    remapped_val = (value_to_map - old_range_min) * (new_range_max - new_range_min) / (old_range_max - old_range_min) + new_range_min
    if(remapped_val>new_range_max):
        remapped_val = new_range_max
    elif (remapped_val < new_range_min):
        remapped_val = new_range_min

    return remapped_val

def plot_ellipse_from_bbox(frame, xywh, col=(150, 150, 150), thickness=4 , 
                           corner_pts_radius=10, center_circle_radius = 40, 
                           center_circle_thickness=4, 
                           center_circle_text_font_size = 1,
                           center_circle_text_font_thickness =1,
                           center_circle_text_color = (255, 255, 255),
                           center_circle_fill_color = (0, 200, 0),
                           confidence_value=0.5 ):
    # plot an ellipse/cicle from the bbox coords
    # Args: 
    # frame, (center-xy) , (maj,min)-ax-len, rotAngle in anticlockwise dir, startAngleArc, endAngleArc, .. 
    # cv.ellipse(img,(256,256),(100,50),0,0,180,255,-1)
    # There's an alternate function which can draw from bboxes. 
    # Docs: https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga28b2267d35786f5f890ca167236cbc69
    cx, cy, w, h = xywh.cpu().detach().numpy()
    rect = ((cx, cy), (w, h), 0)
    # col = (255, 0, 0) # Blue color because BGR
    ellipse_color = col

    if SHOW_CENTER_CONFIDENCE:
        px, py = np.int0((cx, cy))
        # cv2.circle(frame, (px, py), radius=center_circle_radius, color=col, thickness = center_circle_thickness)

        circle_color = center_circle_fill_color if MANUAL_COLOR else col
        cv2.circle(frame, (px, py), radius=center_circle_radius, color=circle_color, thickness = center_circle_thickness)

        conf_value_ = int(100*confidence_value)
        text = f'{conf_value_}'
        
        # font = cv2.FONT_HERSHEY_SIMPLEX
        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        
        # THIS IS THE FONT SIZE< THAT IS THE THICKNESSSSS
        font_scale = center_circle_text_font_size
        # text_color_ = center_circle_text_color if MANUAL_COLOR else col  # White text_color_ in BGR
        text_color_ = center_circle_text_color 
        text_thickness = center_circle_text_font_thickness

        # Get the text size (width, height) and baseline
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, text_thickness)

        text_x = px - (text_width // 2)
        text_y = py + (text_height // 2)

        cv2.putText(frame, text, (text_x, text_y), font, font_scale, text_color_, text_thickness, cv2.LINE_AA)

        # cv2.putText(frame, text=txt_, org=(px, py), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=col, thickness=1) 
    
    
    # Making the ellipse & 4 end points color same as the circle color
    cv2.ellipse(frame, rect, ellipse_color, thickness=thickness )
    # Now draw the 4 end points... 
    rect_points = cv2.boxPoints(rect)
    rect_points = np.int0(rect_points)  # Convert to integer coordinates
    # Don't show rectangles anymore
    # cv2.polylines(frame, [rect_points], isClosed=True, color=(255, 0, 0), thickness=2)

    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
    mid_pts = []
    for i in range(4):
        pt1 = rect_points[i]
        pt2 = rect_points[(i + 1) % 4]  # The next point (wrapping around)
        
        mid_pt = midpoint(pt1, pt2)
        mid_pts.append(mid_pt)
        # Draw the midpoint as a small circle
        # Color same as that orignal ellipse color?
        # What will be the color of the points?
        cv2.circle(frame, mid_pt, radius=corner_pts_radius, color=ellipse_color, thickness=-1)  # Green midpoint

    return np.array(mid_pts)


def get_line_color(distance, threshold_dict, img_dim):
    lower = threshold_dict['line-color-mid-low'] * img_dim
    upper = threshold_dict['line-color-mid-high'] * img_dim
    col = threshold_dict['mid-rgb'] 
    if distance < lower:
        col = threshold_dict['short-rgb']
    elif distance > upper:
        col = threshold_dict['long-rgb']
    return col

def visualize_objects(original_image, processed_image, yolo_models, threshold_dict):

    
    im_height, im_width, im_channels = processed_image.shape
    image_dimension = im_width
    # Reference
    # threshold_dict = {}
    
    # # Number of objects to display
    # threshold_dict['max-objects'] = 5
    # threshold_dict['confidence-threshold'] = 0.3 
    # # Line colors
    # threshold_dict['short-rgb'] = (1, 128, 1) # Green
    # threshold_dict['mid-rgb'] = (160, 32, 240) # Purple
    # threshold_dict['long-rgb'] = (255, 219, 88) # Mustard
    
    # # Best to set these as ranges not exact values:
    ## Better to set them as percentage of image size (Width)
    # threshold_dict['line-color-mid-low'] = 0.25
    # threshold_dict['line-color-mid-high'] = 0.45 

    # The Code just modifies the image_to_check and no other change in results. 
    # yolo_res_list = []
    # for mod in yolo_models:
    #     yolo_res_list.append(mod(original_image, verbose=False))
        
    # for results_yolo in yolo_res_list:
    #     # As we're giving in 1 frame, there should be only 1 results object
    #     for i, res in enumerate(results_yolo):
    #         # print("------------yolo res--------")
    #         processed_image = res.plot(img=processed_image)

    if SHOW_OBJECTS:
        # Detect objects, segmentation and pose from Yolo
        
        yolo_res_list = []
        # for mod in yolo_models:
        #     yolo_res_list.append(mod(original_image, verbose=False))
        track_history = defaultdict(lambda: [])
        # CHECKING TRACKING STRICTLY
        yolo_res_list.append(yolo_models[0].track(original_image, verbose=False, show=False))

        # Stop plotting mass results
        # # When it's 1 Yolo model, the obj detector, loop will run once. 

                # Now use the custom plotting function to plot the ellipses instead of rectangles, and fix io later
        # # all_midpoints_array = np.vstack(all_midpoints)
        
        
        # DRAWING YOLO STUFF
        # Simplyfing logic for 1 obj detector model : 

        # If no results then just return 
        if len(yolo_res_list) == 0:
            return processed_image
            
        results_yolo = yolo_res_list[0]

        # If no results in the first model, then just return
        if len(results_yolo) == 0:
            return processed_image
        
        
        all_midpoints = []
        # By default the boxes are sorted in order of confidence scores
        # print("------printing len of results yolo, (it's 1 as expected) to see how the results are ")
        # print(len(results_yolo))
        # print(results_yolo[0].boxes)
        # What should be the color of the ellipses?
        for res in results_yolo:
            # Only enumerate on TOP MAX OBJECTS Then further constrain by confidence threshold
            boxes_obj = res.boxes
            # Because if it's  None, it breaks the next logic. 
            if(boxes_obj is None):
                return processed_image
            # maybe the tracking ids are nulls, and it can't success fully track
            if res.boxes.id is not None: 
                track_ids = res.boxes.id.int().cpu().tolist()
            else:
                # Just color them according to their iter numbers
                track_ids = range(111, 111+threshold_dict['max-objects'])
            # print("----------------printing tracking ids: ")
            # print(track_ids)
            for i, xywh in enumerate(boxes_obj.xywh[:threshold_dict['max-objects']]):
                # TODO: WRITE the area based sorting color coding algorithm. 
                if(boxes_obj.conf[i]>=threshold_dict['confidence-threshold']):
                    
                    # THis trail logic doesn't work right now anyway...
                    # track = track_history[track_ids[i]]

                    # track.append((float(xywh[0]), float(xywh[1])))  # x, y center point
                    # if len(track) > 300:  # retain 90 tracks for 90 frames
                    #     track.pop(0)

                    # # Draw the tracking lines
                    # points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    # cv2.polylines(processed_image, [points], isClosed=False, color=(230, 230, 230), thickness=10)


                    mid_pts = plot_ellipse_from_bbox(processed_image, xywh, col = get_color(track_ids[i]),
                                                     thickness = threshold_dict['ellipse-line-thickness'], 
                                                     corner_pts_radius = threshold_dict['ellipse-corner-points-radius'],
                                                     center_circle_radius =   threshold_dict['center-circle-radius'],
                                                     center_circle_thickness =   threshold_dict['center-circle-thickness'],
                                                     center_circle_text_font_size = 0.5,
                                                     center_circle_text_font_thickness =  threshold_dict['center-circle-text-font-thickness'] ,
                                                     center_circle_text_color =  threshold_dict['center-circle-text-color'] ,
                                                     center_circle_fill_color =  threshold_dict['center-circle-fill-color'] ,
                                                     confidence_value=boxes_obj.conf[i])
                    all_midpoints.append(mid_pts)

        # # Use KDTree for fast nearest neighbor search
        # kdtree = KDTree(all_midpoints_array)

        # # Find the closest point for each point in the array
        # closest_points = []
        # for i, point in enumerate(all_midpoints_array):
        #     dist, idx = kdtree.query(point, k=2)  # k=2 because the closest point to itself is included
        #     closest_points.append(all_midpoints_array[idx[1]])  # idx[1] is the closest "other" point
        # Convert the list to a stacked array (K*4 x 2)
        # all_midpoints_array = np.vstack(all_midpoints)

        # Initialize an empty list to store the closest points for each box
        closest_points_per_box = []
        K = len(all_midpoints)
        if( K < 2 ):
            # If 0 or 1 ellipse then cannot plot lines.
            return processed_image
        # Loop through each box's midpoints and exclude its points for the nearest neighbor search
        for i in range(K):
            # Midpoints of the current box
            current_midpoints = all_midpoints[i]
            
            # Combine all other midpoints except the current box's
            other_midpoints = np.vstack([all_midpoints[j] for j in range(K) if j != i])
            
            # Create a KDTree for the other midpoints
            kdtree = KDTree(other_midpoints)
            
            # Find the closest point in the "other midpoints" for each point in the current box
            closest_points_for_current = []
            closest_distance_list = []
            for point in current_midpoints:
                dist, idx = kdtree.query(point, k=1)  # Find the closest point
                closest_points_for_current.append(other_midpoints[idx])  # Append the closest point
                closest_distance_list.append(dist)
                # TO check how much are the distance values
            

            # Store the closest points for the current box
            closest_points_per_box.append(np.array(closest_points_for_current))
            for j in range(4):
                pt1 = tuple(current_midpoints[j])
                pt2 = tuple(closest_points_for_current[j])
                col_to_plot = get_line_color(closest_distance_list[j], threshold_dict, image_dimension)
                cv2.line(processed_image, pt1, pt2, col_to_plot, thickness=threshold_dict['connecting-line-thickness'])  # Selected Color
            # Now `closest_points_per_box` contains the closest points for each box, 
            # excluding its own midpoints
    
    return processed_image


def find_face(image_to_check, max_target_distance, model):

    # At the end all of this code will be wrapped in an exception handler. 
    RESULT_TO_RETURN = [False]
    # gray = cv2.cvtColor(image_to_check, cv2.COLOR_BGR2GRAY) #convert image to black and white
    # faces = face_cascade.detectMultiScale(gray, 1.2, 5)     #look for faces

    # Detect faces from DBFace
    objs = detect(model, image_to_check)

    # Objects is a list of tuples (bbox, landmarks)
    # I don't know but assuming that the they are already sorted in descending order of scores. 
    faces = []
    for bbox in objs:
        x1, y1 = bbox.x, bbox.y
        w, h = bbox.width, bbox.height
        faces.append( [x1, y1, w, h])
    # Constructing an object like before 
    # print("In opr printing faces:=-----")
    # print(faces)

    # TODO : RIGHT NOW, IF NO FACES DETECTED, EVEN THE YOLO OBJECTS WON"T BE DRAWN, 
    # NEED to decouple those modules and have independence
    # DONE
    if len(faces) >= 1: #if face(s) detected
        faces = list(faces)[0] #if several faces found use the first one

        x = faces[0]
        y = faces[1]
        w = faces[2]
        h = faces[3]

        center_face_X = int(x + w / 2)
        center_face_Y = int(y + h / 2)
        height, width, channels = image_to_check.shape

        distance_from_center_X = (center_face_X - width/2)/220 # why? can't remember why I did this
        distance_from_center_Y = (center_face_Y - height/2)/195 # why?

        target_distance = math.sqrt((distance_from_center_X*220)**2 + (distance_from_center_Y*195)**2) # calculate distance between image center and face center

        if target_distance < max_target_distance :#set added geometry colour
            locked = True
            color = (0, 255, 0)
        else:
            locked = False
            color = (0, 0, 255)


        # cv2.rectangle(image_to_check,(center_face_X-10, center_face_Y), (center_face_X+10, center_face_Y),    #draw first line of the cross
        #               color, 2)
        # cv2.rectangle(image_to_check,(center_face_X, center_face_Y-10), (center_face_X, center_face_Y+10),    #draw second line of the cross
        #               color,2)

        # cv2.circle(image_to_check, (int(width/2), int(height/2)), int(max_target_distance) , color, 2)    #draw circle

        # This is to draw the Face landmarks from DBface
        for obj in objs:
            common.drawbbox(image_to_check, obj, landmarkcolor=(255,255,255))
        # IF FACE is found, modify the result: 
        RESULT_TO_RETURN =  [True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]

    return RESULT_TO_RETURN

