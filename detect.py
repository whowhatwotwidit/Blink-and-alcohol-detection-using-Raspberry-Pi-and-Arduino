#!/usr/bin/env python
# coding: utf-8

import cv2
import time
import threading

class detect:
	cap = None
	state = 0
	thread = None
	ret = None
	def __init__(self):
		self.thread = threading.Thread(target=self.eye)
		print("Eye detect init.")
	
	def stop_eye(self):
		self.ret = None
		if self.cap != None:
			self.cap.release()
			cv2.destroyAllWindows()
		self.state = -1
		try:
			self.thread.join()
		except:
			time.sleep(0)
	def run(self):
		print("Running camera thread")
		self.thread.start()
		print("Camera thread: ", self.isRunning())
	
	def resetState(self):
		self.state = 0
	
	def isRunning(self):
		return self.thread.is_alive()

	def getState(self):
		return self.state

	def eye(self):
		#Face and eye cascade classifiers from xml files
		face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
		eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_eye_tree_eyeglasses.xml')

		first_read = False
		blink_counter = 0
		start_time = time.time()
		# Video Capturing by using webcam
		self.cap = cv2.VideoCapture(0)
		self.ret, image = self.cap.read()

		start = time.time()
		end = time.time()
		time_diff = 0.0
		capture_time = 2
		#blink_limit = 3

		while self.ret:
				# this will keep the web-cam running and capturing the image for every loop
			self.ret, image = self.cap.read()
				# Convert the rgb image to gray
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				# Applying bilateral filters to remove impurities
			gray = cv2.bilateralFilter(gray, 5, 1, 1)
				# to detect face 
			faces = face_cascade.detectMultiScale(gray, 1.1, 6, minSize=(100,100))
			if len(faces) > 0:
				for (x, y, w, h) in faces:
					image = cv2.rectangle(image, (x, y), (x + w, y + h), (1, 190, 200), 2)
					roi_face = gray[y:y + h, x:x + w] #face detector
					roi_face_clr = image[y:y + h, x:x + w] #image
					eyes = eye_cascade.detectMultiScale(roi_face, 1.1, 6, minSize=(50,50)) #list of eyes
					cv2.putText(image, "Blinks: "+ str(blink_counter), (25,70), cv2.FONT_HERSHEY_SIMPLEX, .5, (1, 190, 200), 2)
					#cv2.putText(image, "Eye count:", str(len(eyes), "Eye coor:", *eyes, sep=" "), (10,395), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0), 2)
						#Check list of eyes if more than 2, thus it sees eyes. Needs to be outside for-loop for better performance
					if len(eyes) >= 2: #eyes open
						start = time.time()
						cv2.putText(image, "Eyes Open", (25,35), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)
						for (ex,ey,ew,eh) in eyes:
							cv2.rectangle(roi_face_clr,(ex,ey),(ex+ew,ey+eh),(255, 153, 255),2)
						#print(time.time(),str(eyes[0][0])+","+str(eyes[0][1])+"," +str(eyes[0][2])+","+str(eyes[0][3])+","+str(eyes[1][0])+","+str(eyes[1][1])+","+str(eyes[1][2])+","+str(eyes[1][3						
					else: #eyes closed
						end = time.time()
						time_diff = end - start
						if time_diff > capture_time: #Will trigger only if 5s has been reached
							cv2.putText(image, "Long Blink Detected! (Eyes closed at " + str(round(time_diff,2)) + "s)", (25,35), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
							blink_frame = image #Make a copy of the frame at blink capture so that it won't move with the continous camera feeds
							start = time.time() #Reset time to current time
							blink_counter = blink_counter + 1
							print("Blink detected!")
							self.state = blink_counter
							cv2.putText(image, "Long Blinks Detected: " + str(blink_counter), (440,70), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
							cv2.putText(image, time.ctime(end), (10,460), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)									#print("Image saved: ", cv2.imwrite(str(time.ctime(end).replace(":","").replace(" ",""))+".jpg",blink_frame))
							#cv2.imshow("Captured Blink", blink_frame) #Show captured frame
						cv2.putText(image, "Eye/s Closed @" + str(round(time_diff,2)) + "s", (460,35), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
						#print("0,0,0,0,0,0,0,0")
						#Plotting and GUI & output
			else:
				cv2.putText(image, "No Face Detected.", (20,35), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 255), 2)
			#cv2.putText(image, "Instructions: q/Q - Quit, s/S Start Blink Capture, r/R - Reset Blink Counter", (10,425), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
			cv2.imshow('Blink', image)
			a = cv2.waitKey(1)
			if a == 113:
				self.stop_eye()
			#print(self.getState())
    		# press q/Q to Quit and s/S to start
    		# ord(ch) returns the ascii of ch
	#Function for release and destroy all windows set as stop_eye()
#state = eye()
#print("State: ", state)
#detect().run()