import cv2
#import torch
from opr import find_face, find_face_basic
#from model.DBFace import DBFace
import comm_ard
import time 
import random
#HAS_CUDA = torch.cuda.is_available()
#print(f"HAS_CUDA = {HAS_CUDA}")
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class Controller():
	def __init__(self):
		self.ard = comm_ard.ard_connect(self)     #create object allowing communication with arduino
		self.is_connected = False 
		
		self.cam = cv2.VideoCapture(0)
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
		#self.dbface = DBFace()
		#self.dbface.eval()
		#if HAS_CUDA:
		#	self.dbface = self.dbface.cuda()
		#self.dbface.load("model/dbface.pth")
		#self.dbface.load("model/dbfaceSmallH.pth")

		self.servo_x_center = 90
		self.servo_y_center = 90

		self.servo_x_target = 90
		self.servo_y_target = 90

		self.servo_x_range = [40, 140]
		self.servo_y_range = [30, 120]
		
		self.screen_width = 500
		self.screen_height = 500


	def connect(self, port_number):    #set COM port from text box if arduino not already connected
		# This functions hangs somehow.... Different from camera change freeze. 
		if(not self.is_connected):
			port = port_number
			if (self.ard.connect(port)):    #set port label message
				msg = "..................... Connected to port : " + port + " ......................"
			else:
				msg = ".................... Cant connect to port : " + port + " ....................."
			print(msg)
	
	def move_servos(self):
		if (self.is_connected):
			
			# NEED TO CHANGE LED LOGIC LATER 
			led_mode = 1
			#if self.LED_ON and not self.manual_mode:
			#if not self.face_detected: #set led mode (0:red, 1:yellow 2:green)
			# 		led_mode = 0
			#	else:
			#		if self.target_locked:
			 #			led_mode = 1
			#		else :
			 #			led_mode = 2

			# elif self.LED_ON and self.manual_mode:
			# 	led_mode = 3 #turn all led's on
			#else:
			# 	led_mode = 4 #turn led's off

			# data_to_send = "<" + str(int(self.target_pan)) + "," + str(int(self.target_tilt)) + "," + str(led_mode) + ">"

			# data_to_send = "<" + str(int(self.servo1_target)) + "," + str(int(self.servo2_target)) + "," + str(int(self.servo3_target)) + "," + str(int(self.servo4_target)) + "," + str(int(self.servo5_target)) + ","  + str(led_mode) + ">"
			data_to_send = "<" + str(int(self.servo_x_target)) + "," + str(int(self.servo_y_target)) +  ","  + str(led_mode) + ">"
			
			self.ard.runTest(data_to_send)
	
	def get_ratio(self, delta, delta_max,  angle_center, angle_range):
		if abs(delta) <= 1: 
			return angle_center
		ratio = (delta*1.0)/delta_max
		ratio = abs(ratio)
		sign = delta / abs(delta)
		# trimmed_range = angle_range
		if sign>=0:
			trimmed_range = [angle_center, angle_range[1]]
		else : 
			trimmed_range = [angle_range[0], angle_center]
		FACTOR = 1.3
		target_angle = angle_center + (FACTOR) * sign * (trimmed_range[1] - trimmed_range[0]) * ratio 
		#target_angle *= 1.3
		return int(target_angle)
		

	def process_image(self, image_to_proc): 
		#RESULT = find_face(image_to_proc, 50, self.dbface)
		RESULT = find_face_basic(image_to_proc, 50)
		
		# If face found, 
		if RESULT[0]:
			image_to_proc = RESULT[1]
			dx = -RESULT[5]
			dy = -RESULT[6]
			h,w,c = image_to_proc.shape 
			print("_"*50)
			print(w, h , dx, dy ) 
			self.servo_x_target = self.get_ratio(dx, w/2.0, self.servo_x_center, self.servo_x_range)
			self.servo_y_target = self.get_ratio(dy, h/2.0, self.servo_y_center, self.servo_y_range)
			print(self.servo_x_target, self.servo_y_target)
			led_mode = 2
			# print(dx, dy)
			
			self.move_servos()
		else :
			xr = self.servo_x_range
			yr = self.servo_y_range
			self.servo_x_target = random.randint(50, 100)
			self.servo_y_target = random.randint(60, 100)
			print("Sending random values: ")
			print(self.servo_x_target, self.servo_y_target)
			time.sleep(0.8)
			# print(dx, dy)
			self.move_servos() 
			
		return image_to_proc
	

	def show(self):			
		while True:
			ret, image = self.cam.read()

			cv2.imshow('Fisheye',self.process_image(image))
			k = cv2.waitKey(1)
			if k != -1:
				break
		#cv2.imwrite('D:\Github\face_tracking_camera\outputs', image)
		cv2.imwrite('/home/pi', image)
		self.cam.release()
		cv2.destroyAllWindows()


ctrl = Controller()
ctrl.connect("/dev/ttyUSB0")
ctrl.show()
