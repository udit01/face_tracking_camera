import cv2
import math
import common
import numpy as np
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
        
        for results_yolo in yolo_res_list:
            for i, res in enumerate(results_yolo):
                # print("------------yolo res--------")
                image_to_check = res.plot(img=image_to_check)
            # print("FOUND FACE \n ... ")
        return [True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]

    else:
        # print("COUDN't find  FACE \n ... ")

        return [False]
