import sys
from PyQt5.QtWidgets import QApplication, QWidget, QColorDialog
from PyQt5.QtGui import QIcon, QPixmap, QImage, QColor
from PyQt5.uic import loadUi
import opr
import comm_ard
import random
import pickle
import copy
import cv2
import torch
from model.DBFace import DBFace
from ultralytics import YOLO

HAS_CUDA = torch.cuda.is_available()
print(f"HAS_CUDA = {HAS_CUDA}")

class App(QWidget):

    def __init__(self):
        super().__init__()

        self.ui = loadUi('tracking.ui', self)    #Load .ui file that define the window layout(buttons, tick boxoex...)

        self.setMouseTracking(True)    #allow mouse tracking(use during manual mode)
        self.manual_mode = False       #set manual mode to false to start in tracking face mode
        self.LED_ON = True             #set LED on mode
        self.CameraID = 0              #define camera ID, first camera = ID 0, second ID 1 and so on

        self.rec = True                #allows to start camera recording
        self.cap = cv2.VideoCapture(self.CameraID)  #define open CV camera recording
        self.cap.set(3, 960)                        #set capture width
        self.cap.set(4, 540)                        #set capture height
        #The bigger the image is, the longer the processing is goint to take to process it
        ## My computer is a bit shit so I kept it quite small .

        self.min_tilt = 22          #minimum tilt angle in degree (up/down angle)
        self.max_tilt = 80          #maximum tilt angle in degree
        self.current_tilt = 0       #current tilt (info received from arduino and displayed in LCD numbers)
        self.target_tilt = 90      #the tilt angle you need to reach

        self.min_pan = 80            #minimum pan angle in degree(left/ right angle)
        self.max_pan = 100         #maximum pan angle in degree
        self.current_pan = 80        #current pan (info received from arduino and displayed in LCD numbers)
        self.target_pan = 90       #the pan angle you need to reach

        self.roam_target_pan = 90
        self.roam_target_tilt = 90
        self.roam_pause = 40      #amount of frame the camera is going to pause for when roam tilt or pan target reached
        self.roam_pause_count = self.roam_pause   #current pause frame count


        self.is_connected = False    #boolean defining if arduino is connected

        self.InvertPan = False       #allows pan to be inverted
        self.InvertTilt = False      #allows tilt to be inverted

        self.face_detected = False     #define if a face is detected
        self.target_locked = False     #define if detected face is close enough to the center of the captured image
        self.max_target_distance = 50  #minimum distance between face/center of image for setting target locked
        self.max_empty_frame = 50      #number of empty frame (no face detected) detected before starting roaming
        self.empty_frame_number = self.max_empty_frame   #current empty frame count

        # Later this will be modified in the GUI just the init values
        # Relaxed constraints in the beginning
        threshold_dict = {}    
        # Number of objects to display
        threshold_dict['max-objects'] = 10
        threshold_dict['confidence-threshold'] = 0.1
        # Line colors
        threshold_dict['short-rgb'] = (1, 128, 1) # Green
        threshold_dict['mid-rgb'] = (160, 32, 240) # Purple
        threshold_dict['long-rgb'] = (255, 219, 88) # Mustard
        
        # Best to set these as ranges not exact values:
        threshold_dict['line-color-mid-low'] = 0.25
        threshold_dict['line-color-mid-high'] = 0.45

        threshold_dict['ellipse-line-thickness']   = 4
        threshold_dict['connecting-line-thickness'] = 3

        self.threshold_dict = threshold_dict

        self.dbface = DBFace()
        self.dbface.eval()
        if HAS_CUDA:
            self.dbface.cuda()
        self.dbface.load("model/dbface.pth")

        # Instead of using 3 models for showcasing, using 1 model for req
        # self.yolo_models = [YOLO("yolov8n.pt"), YOLO("yolov8n-seg"), YOLO("yolov8n-pose")]
        self.yolo_models = [YOLO("yolov8n.pt")]

        self.selected_color = QColor(0,0,255)

        # Initialize the random colors otherwise 
        opr.make_random_colors_array(num_colors=20)

        self.ard = comm_ard.ard_connect(self)     #create object allowing communicationn with arduino
        self.initUI()    #set up UI( see below )

    def initUI(self):     #UI related stuff
        self.setWindowTitle('Unbinding Bodies')              #set window title
        self.label = self.ui.label                      #set label (it will be used to display the captured images)
        self.QuitButton = self.ui.QuitButton            #set quit button
        self.PauseButton = self.ui.PauseButton          #set pause button
        self.Pan_LCD = self.ui.Pan_LCD                  #and so on...
        self.Tilt_LCD = self.ui.Tilt_LCD                #...
        self.Manual_checkbox = self.ui.Manual_checkbox  #...
        self.ConnectButton = self.ui.ConnectButton
        self.COMlineEdit = self.ui.COMlineEdit
        self.COMConnectLabel = self.ui.COMConnectLabel
        self.UpdateButton = self.ui.UpdateButton
        self.MinTiltlineEdit = self.ui.MinTiltlineEdit
        self.MaxTiltlineEdit = self.ui.MaxTiltlineEdit
        self.InvertTilt_checkbox = self.ui.InvertTilt_checkbox
        self.InvertTilt = self.InvertTilt_checkbox.isChecked()
        self.MinPanlineEdit = self.ui.MinPanlineEdit
        self.MaxPanlineEdit = self.ui.MaxPanlineEdit
        self.InvertPan_checkbox = self.ui.InvertPan_checkbox
        self.InvertPan = self.InvertPan_checkbox.isChecked()
        self.TiltSensivityEdit = self.ui.TiltSensivityEdit
        self.TiltSensivity = 1
        self.PanSensivityEdit = self.ui.PanSensivityEdit
        self.PanSensivity = 1
        self.LED_checkbox = self.ui.LED_checkbox
        self.CameraIDEdit = self.ui.CameraIDEdit

        self.QuitButton.clicked.connect(self.quit)               #bind quit button to quit method
        self.PauseButton.clicked.connect(self.toggle_recording)  #bind pause button to pause method
        self.Manual_checkbox.stateChanged.connect(self.set_manual_mode)  #bla bla bla
        self.ConnectButton.clicked.connect(self.connect)
        # Here the variables are updated!! All the new varaibles updates will go in there
        self.UpdateButton.clicked.connect(self.update_angles)

        # Full screen button
        self.FullScreenButton = self.ui.FullScreenButton
        self.FullScreenButton.clicked.connect(self.fullScreen)

        # These buttons are just taken in here, no functionality is added
        self.ShortMinTextField = self.ui.ShortMinTextField
        self.MidMinTextField = self.ui.MidMinTextField
        self.MidMaxTextField = self.ui.MidMaxTextField
        self.LongMaxTextField = self.ui.LongMaxTextField

        self.short_rgb_color = QColor(200,0,0)
        self.mid_rgb_color = QColor(0,200,0)
        self.long_rgb_color = QColor(0,0,200)

        self.shortRGBbutton = self.ui.ShortRGBButton
        self.midRGBbutton = self.ui.MidRGBButton
        self.longRGBbutton = self.ui.LongRGBButton
        
        self.shortRGBbutton.clicked.connect( lambda: self.showColorDialog(len_code=0) )
        self.midRGBbutton.clicked.connect( lambda: self.showColorDialog(len_code=1) )
        self.longRGBbutton.clicked.connect( lambda: self.showColorDialog(len_code=2) )
        
        # SAVE AND LOAD THESE SERVO VALUES TO AND FROM PICKLE LATER
        self.Servo1Min = self.ui.Servo1Min
        self.Servo1Max = self.ui.Servo1Max

        self.Servo2Min = self.ui.Servo2Min
        self.Servo2Max = self.ui.Servo2Max
        
        self.Servo3Min = self.ui.Servo3Min
        self.Servo3Max = self.ui.Servo3Max

        self.Servo4Min = self.ui.Servo4Min
        self.Servo4Max = self.ui.Servo4Max
        
        self.Servo5Min = self.ui.Servo5Min
        self.Servo5Max = self.ui.Servo5Max

        self.MaxObjectsTextField = self.ui.MaxObjectsTextField
        self.ConfidenceThresholdTextField = self.ui.ConfidenceThresholdTextField
        self.EllipseThicknessTextField = self.ui.EllipseThicknessTextField
        self.LineThicknessTextField = self.ui.LineThicknessTextField

        # What are the values in here need to be checked and confirmed according to our setup
        self.load_init_file()
        self.update_angles() #update angle method

        self.record()  #start recording
    
    def fullScreen(self, targetWidget):
        # def switch_fullscreen(targetWidget):
        if targetWidget.isFullScreen():
            targetWidget.showNormal()
            print("Showing normal.")
        else:
            targetWidget.showFullScreen()
            print("Showing full-screen.")


    # TO get the color input from the USER
    def showColorDialog(self, len_code=0):
        # TODO: Encapsulate in a try except for final version.
        # get color from user
        selected_color = QColorDialog.getColor(self.selected_color, self)
        # did user cancel operation ?
        if not selected_color.isValid():
            # print("----- invalid color selected----")
            return
        # update stylesheet
        # self.frame.setStyleSheet(
        #     "QWidget { background-color: %s}" % selected_color.name())
        # # grab RBG values and print them to terminal
        # rgb = (selected_color.red(),
        #     selected_color.green(),
        #     selected_color.blue())
        bgr = (selected_color.blue(),
            selected_color.green(),
            selected_color.red())
        print("COLOR BGR---------")
        print(bgr)
        # set `selected_color`as an instance variable so you can retrieve it later
        # self.selected_color = selected_color
        if len_code == 0 :
            self.short_rgb_color = selected_color
            self.threshold_dict['short-rgb'] = bgr
        elif len_code == 1 :
            self.mid_rgb_color = selected_color
            self.threshold_dict['mid-rgb'] = bgr
        elif len_code == 2 :
            self.long_rgb_color = selected_color
            self.threshold_dict['long-rgb'] = bgr
        return 

    def load_init_file(self):
        #this method will allow to reload the latest values entered in text boxes even after closing the software
        try:         #try to open init file if existing
            with open('init.pkl', 'rb') as init_file:
                var = pickle.load(init_file)  #load all variable and update text boxes
                self.COMlineEdit.setText(var[0])
                if(var[4]):
                    self.MinTiltlineEdit.setText(str(var[2]))
                    self.MaxTiltlineEdit.setText(str(var[1]))
                else:
                    self.MinTiltlineEdit.setText(str(var[1]))
                    self.MaxTiltlineEdit.setText(str(var[2]))
                self.TiltSensivityEdit.setText(str(var[3]))
                self.InvertTilt_checkbox.setChecked(var[4])
                if (var[8]):
                    self.MinPanlineEdit.setText(str(var[6]))
                    self.MaxPanlineEdit.setText(str(var[5]))
                else:
                    self.MinPanlineEdit.setText(str(var[5]))
                    self.MaxPanlineEdit.setText(str(var[6]))
                self.PanSensivityEdit.setText(str(var[7]))
                self.InvertPan_checkbox.setChecked(var[8])
                #self.CameraIDEdit.setText(str(var[9]))
                self.LED_checkbox.setChecked(var[10])
            print(var)
            #set variables
        except:
            pass

    def save_init_file(self):
        init_settings = [self.COMlineEdit.text(),
        self.min_tilt, self.max_tilt, self.TiltSensivity, self.InvertTilt,
        self.min_pan, self.max_pan, self.PanSensivity, self.InvertPan,
        self.CameraID, self.LED_ON]
        with open('init.pkl', 'wb') as init_file:
            pickle.dump(init_settings, init_file)

    def connect(self):    #set COM port from text box if arduino not already connected
        if(not self.is_connected):
            port = self.COMlineEdit.text()
            if (self.ard.connect(port)):    #set port label message
                self.COMConnectLabel.setText("..................... Connected to port : " + port + " ......................")
            else:
                self.COMConnectLabel.setText(".................... Cant connect to port : " + port + " .....................")

    def update_angles(self):  #update variables from text boxes
        
        def get_norm(x):
            # Then it's a percentage and needs to be divided by 100
            if(x > 1):
                return get_norm(x/100.0) # keep dividing by 100 till you reach 0 to 1
            return x

        try:
            self.InvertTilt = self.InvertTilt_checkbox.isChecked()
            self.InvertPan = self.InvertPan_checkbox.isChecked()
            self.TiltSensivity = float(self.TiltSensivityEdit.text())
            self.PanSensivity = float(self.PanSensivityEdit.text())
            self.LED_ON = self.LED_checkbox.isChecked()

            self.cap.release()    #camera need to be released in order to update the camera ID (if changed)
            self.CameraID = int(self.CameraIDEdit.text())
            self.cap = cv2.VideoCapture(self.CameraID)

            if(self.InvertPan):
                self.max_pan = int(self.MinPanlineEdit.text())
                self.min_pan = int(self.MaxPanlineEdit.text())
            else:
                self.min_pan = int(self.MinPanlineEdit.text())
                self.max_pan = int(self.MaxPanlineEdit.text())

            if(self.InvertTilt):
                self.max_tilt = int(self.MinTiltlineEdit.text())
                self.min_tilt = int(self.MaxTiltlineEdit.text())
            else:
                self.min_tilt = int(self.MinTiltlineEdit.text())
                self.max_tilt = int(self.MaxTiltlineEdit.text())

            # Connecting 
            self.threshold_dict['line-color-short-low']      = get_norm( float( self.ShortMinTextField.text() ) )
            self.threshold_dict['line-color-mid-low']        = get_norm( float( self.MidMinTextField.text() ) )
            self.threshold_dict['line-color-mid-high']       = get_norm( float( self.MidMaxTextField.text() ) )
            self.threshold_dict['line-color-long-high']      = get_norm( float( self.LongMaxTextField.text() ) )
            self.threshold_dict['max-objects']               =         (   int( self.MaxObjectsTextField.text() ) )
            self.threshold_dict['confidence-threshold']      = get_norm( float( self.ConfidenceThresholdTextField.text() ) )
            self.threshold_dict['ellipse-line-thickness']    =         (   int( self.EllipseThicknessTextField.text() ) )
            self.threshold_dict['connecting-line-thickness'] =         (   int( self.LineThicknessTextField.text() ) )

            # Set these servo values later and save and load them from pickle
            # value to set  = self.Servo1Min
            # value to set  = self.Servo1Max
            # value to set  = self.Servo2Min
            # value to set  = self.Servo2Max
            # value to set  = self.Servo3Min
            # value to set  = self.Servo3Max
            # value to set  = self.Servo4Min
            # value to set  = self.Servo4Max
            # value to set  = self.Servo5Min
            # value to set  = self.Servo5Max


            self.save_init_file()
            print("values updated")
        except Exception as e:
            print(e)
            print("can't update values")

    def mouseMoveEvent(self, event):

        #the position of the mouse is tracked avec the window and converted to a pan and tilt amount
        #for example if mouse completely to the left-> pan_target = 0(or whatever minimum pan_target value is)
        # if completely to the right-> pan_target = 180(or whatever maximum pan_target value is)
        #same principal for tilt

        if(self.manual_mode): #if manual mode selected
            if(35<event.y()<470 and 70<event.x()<910):
                if(self.InvertTilt):  #if invert tilt selected values will be mapped in the opposite direction
                    self.target_tilt = opr.remap(event.y(), self.max_tilt, self.min_tilt, 470, 35)
                    #(470,35 allows the mouse to be tracked only over the image. yes...it is very lazy)
                else:
                    self.target_tilt =  opr.remap(event.y(), self.min_tilt, self.max_tilt, 35, 470)

                if (self.InvertPan):
                    self.target_pan = opr.remap(event.x(), self.max_pan, self.min_pan, 910, 70)  # event.x()
                else:
                    self.target_pan = opr.remap(event.x(), self.min_pan, self.max_pan, 70, 910)  # event.x()

    def update_LCD_display(self):

        #update servo angle values sent by the arduino
        ##actually pretty useless since the arduino return its target value and not its actual real world position
        self.Pan_LCD.display(self.current_pan)
        self.Tilt_LCD.display(self.current_tilt)

    def quit(self):
        print('Quit')
        self.rec = False
        sys.exit()

    def closeEvent(self, event):
        self.quit()# call quit method when cross pressed

    def set_manual_mode(self):
        self.manual_mode = self.Manual_checkbox.isChecked()
        if(not self.manual_mode):          #if not in manual mode
            self.random_servos_position()  #select a random pan and tilt target
        print(self.manual_mode)

    def random_servos_position(self):
        self.target_tilt = random.uniform(self.min_tilt, self.max_tilt)
        self.target_pan = random.uniform(self.min_pan, self.max_pan)

    def toggle_recording(self):
        if(self.rec):
            self.rec = False                   #stop recording
            self.PauseButton.setText("Resume") #change pause button text
        else:
            self.rec = True
            self.PauseButton.setText("Pause")
            self.record()


    def record(self):  #video recording

        while(self.rec):
            ret, img = self.cap.read() #CAPTURE IMAGE

            if(self.is_connected):            #if arduino connected
                if(self.manual_mode):         #and manual mode on
                    processed_img = img       #don't process image
                else:
                    processed_img = self.image_process(img) #process image (check for faces and draw circle and cross)
            else:                             #if arduino  not connected
                # processed_img = img           #don't process image
                # process image even if not connected to aurdino
                processed_img = self.image_process(img) #process image (check for faces and draw circle and cross)


            self.update_GUI(processed_img)    #update image in window
            cv2.waitKey(0)                    #no delay between frames
            # I don't want to move servos right now
            # self.move_servos() #move servos

            if (not self.rec):     #allows while loop to stop if pause button pressed
                break

    def update_GUI(self, openCV_img): # Convert openCV image and update pyQt label

        try: #if this doesn't work check camera ID
            openCV_img = cv2.resize(openCV_img, (960, 540))  #this is stretching the image a bit but if not done it won't fit the UI
            height, width, channel = openCV_img.shape
            bytesPerLine = 3 * width
            qImg = QImage(openCV_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

            pixmap = QPixmap(qImg)
            self.label.setPixmap(pixmap)

        except:
            self.label.setText("check camera ID")

        self.show()

    def move_servos(self):
        if (self.is_connected):

            if self.LED_ON and not self.manual_mode:
                if not self.face_detected: #set led mode (0:red, 1:yellow 2:green)
                    led_mode = 0
                else:
                    if self.target_locked:
                        led_mode = 1
                    else :
                        led_mode = 2

            elif self.LED_ON and self.manual_mode:
                led_mode = 3 #turn all led's on
            else:
                led_mode = 4 #turn led's off

            data_to_send = "<" + str(int(self.target_pan)) + "," + str(int(self.target_tilt)) + "," + str(led_mode) + ">"
            self.ard.runTest(data_to_send)
            #the data sent to the arduino will look something like the this (<154, 23, 0>)
            #the arduino will look for the start character "<"
            #then save everything following until it finds the end character ">"
            #at that point the arduino will have saved a message looking like this "154, 23, 0"
            #it will then split the message at every coma and use the pieces of data to move the servos acordingly

            #And yes I should have used bytes or something a bit better
            #I wrote this a while back and at that time I had even more to learn than I do now!
            #I still lazy and can't be asked to change it now as it works .


    def roam(self):
        # This makes the robot go jittery in that case, these pan and tilt need to be adjusted 
        if(self.roam_pause_count < 0 ):      #if roam count inferior to 0

            self.roam_pause_count = self.roam_pause                                        #reset roam count
            self.roam_target_pan = int(random.uniform(self.min_pan, self.max_pan))
            self.roam_target_tilt = int(random.uniform(self.min_tilt, self.max_tilt))

        else:        #if roam count > 1
                     #increment pan target toward roam target
            if (int(self.target_pan) > self.roam_target_pan):
                self.target_pan -= 1
            elif (int(self.target_pan) < self.roam_target_pan):
                self.target_pan += 1
            else:    #if roam target reached decrease roam pause count
                self.roam_pause_count -= 1

            if (int(self.target_tilt) > self.roam_target_tilt):
                self.target_tilt -= 1
            elif (int(self.target_tilt) < self.roam_target_tilt):
                self.target_tilt += 1
            else:
                self.roam_pause_count -= 1


    def image_process(self, img):  #handle the image processing
        #to add later : introduce frame scipping (check only 1 every nframe)
        original_image = copy.deepcopy(img)
        processed_img = opr.find_face(img, self.max_target_distance, self.dbface)  # try to find face and return processed image
        # if face found during processing , the data return will be as following :
        #[True, image_to_check, distance_from_center_X, distance_from_center_Y, locked]
        #if not it will just return False
        # 

        if(processed_img[0]):             #if face found
            self.face_detected = True
            self.empty_frame_number = self.max_empty_frame  #reset empty frame count
            self.target_locked = processed_img[4]
            self.calculate_camera_move(processed_img[2], processed_img[3])  # calculate new targets depending on distance between face and image center
            # Add yolo objects 
            processed_img[1] = opr.visualize_objects(original_image, processed_img[1], self.yolo_models, self.threshold_dict)
            # Return the shiny new image here. 
            return processed_img[1]
        else:
            self.face_detected = False
            self.target_locked = False
            # Need to check if else and roam, and if that impedes the return. 
            if(self.empty_frame_number> 0):
                self.empty_frame_number -= 1  #decrease frame count until it equal 0
            else:
                self.roam()              #then roam
            img = opr.visualize_objects(original_image, img, self.yolo_models, self.threshold_dict)
            return img


    def calculate_camera_move(self, distance_X, distance_Y):

        #self.target_pan += distance_X * self.PanSensivity

        if(self.InvertPan): #handle inverted pan
            self.target_pan -= distance_X * self.PanSensivity
            if(self.target_pan>self.min_pan):
                self.target_pan = self.min_pan
            elif (self.target_pan < self.max_pan):
                self.target_pan = self.max_pan

        else:
            self.target_pan += distance_X * self.PanSensivity
            if(self.target_pan>self.max_pan):
                self.target_pan = self.max_pan
            elif (self.target_pan < self.min_pan):
                self.target_pan = self.min_pan


        #self.target_tilt += distance_Y * self.TiltSensivity

        if(self.InvertTilt): #handle inverted tilt
            self.target_tilt -= distance_Y * self.TiltSensivity
            if(self.target_tilt>self.min_tilt):
                self.target_tilt = self.min_tilt
            elif (self.target_tilt < self.max_tilt):
                self.target_tilt = self.max_tilt
        else:
            self.target_tilt += distance_Y * self.TiltSensivity
            if(self.target_tilt>self.max_tilt):
                self.target_tilt = self.max_tilt
            elif (self.target_tilt < self.min_tilt):
                self.target_tilt = self.min_tilt

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()
    #sys.exit(app.exec_())
