import cv2
import math
import common
import numpy as np
from scipy.spatial import KDTree
from model.DBFace import DBFace
from dbface_main import detect
import common


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def remap(value_to_map, new_range_min, new_range_max, old_range_min, old_range_max):

    remapped_val = (value_to_map - old_range_min) * (new_range_max - new_range_min) / (old_range_max - old_range_min) + new_range_min
    if(remapped_val>new_range_max):
        remapped_val = new_range_max
    elif (remapped_val < new_range_min):
        remapped_val = new_range_min

    return remapped_val

def plot_ellipse_from_bbox(frame, bbox, col=(255, 0, 0)):
    # plot an ellipse/cicle from the bbox coords
    # Args: 
    # frame, (center-xy) , (maj,min)-ax-len, rotAngle in anticlockwise dir, startAngleArc, endAngleArc, .. 
    # cv.ellipse(img,(256,256),(100,50),0,0,180,255,-1)
    # There's an alternate function which can draw from bboxes. 
    # Docs: https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga28b2267d35786f5f890ca167236cbc69
    rect = ((cx, cy), (w, h), 0)
    col = (255, 0, 0) # Blue color because BGR
    cv2.ellipse(frame, rect, col, 2 )
    # Now draw the 4 end points... 
    rect_points = cv2.boxPoints(rect)
    rect_points = np.int0(rect_points)  # Convert to integer coordinates
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
        cv2.circle(frame, mid_pt, radius=5, color=col, thickness=-1)  # Green midpoint

    return np.array(mid_pts)

def find_face(image_to_check, max_target_distance, model, yolo_models):
    # gray = cv2.cvtColor(image_to_check, cv2.COLOR_BGR2GRAY) #convert image to black and white
    # faces = face_cascade.detectMultiScale(gray, 1.2, 5)     #look for faces
    yolo_res_list = []
    for mod in yolo_models:
        yolo_res_list.append(mod(image_to_check, verbose=False))

    objs = detect(model, image_to_check)

    # Objects is a list of tuples (bbox, landmarks)
    # I don't know but assuming that the they are already sorted in descending order of scores. 
    faces = []
    for bbox in objs:
        x1, y1 = bbox.x, bbox.y
        w, h = bbox.width, bbox.height
        faces.append( [x1, y1, w, h])
    # Constructing an object like before 
    print("In opr printing faces:=-----")
    print(faces)

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


        cv2.rectangle(image_to_check,(center_face_X-10, center_face_Y), (center_face_X+10, center_face_Y),    #draw first line of the cross
                      color, 2)
        cv2.rectangle(image_to_check,(center_face_X, center_face_Y-10), (center_face_X, center_face_Y+10),    #draw second line of the cross
                      color,2)

        cv2.circle(image_to_check, (int(width/2), int(height/2)), int(max_target_distance) , color, 2)    #draw circle

        for obj in objs:
            common.drawbbox(image_to_check, obj)
        
        all_midpoints = []
        for results_yolo in yolo_res_list:
            for i, res in enumerate(results_yolo):
                # print("------------yolo res--------")
                image_to_check = res.plot(img=image_to_check)
                # Now use the custom plotting function to plot the ellipess instead of retangbles, and fix io later
                mid_pts = plot_ellipse_from_bbox()
                all_midpoints.append(mid_pts)
            # print("FOUND FACE \n ... ")
        # all_midpoints_array = np.vstack(all_midpoints)

        # # Use KDTree for fast nearest neighbor search
        # kdtree = KDTree(all_midpoints_array)

        # # Find the closest point for each point in the array
        # closest_points = []
        # for i, point in enumerate(all_midpoints_array):
        #     dist, idx = kdtree.query(point, k=2)  # k=2 because the closest point to itself is included
        #     closest_points.append(all_midpoints_array[idx[1]])  # idx[1] is the closest "other" point
        # Convert the list to a stacked array (K*4 x 2)
        all_midpoints_array = np.vstack(all_midpoints)

        # Initialize an empty list to store the closest points for each box
        closest_points_per_box = []

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
            for point in current_midpoints:
                dist, idx = kdtree.query(point, k=1)  # Find the closest point
                closest_points_for_current.append(other_midpoints[idx])  # Append the closest point
            
            # Store the closest points for the current box
            closest_points_per_box.append(np.array(closest_points_for_current))
            for j in range(4):
                pt1 = tuple(current_midpoints[j])
                pt2 = tuple(closest_points_for_current[j])
                cv2.line(img, pt1, pt2, (0, 255, 0), thickness=1)  # Green line
            # Now `closest_points_per_box` contains the closest points for each box, 
            # excluding its own midpoints

        return [True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]

    else:
        # print("COUDN't find  FACE \n ... ")

        return [False]
