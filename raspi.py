from operator import truediv
from pickle import TRUE
import serial
import time  # import the PySerial library
import pyaudio # import PyAudio
import wave # PyAudio req
import subprocess

#Sample wav files
# Z = start of alcohol detect
# Y = pass alcohol/start of driving session
# X = fail alcohol
# W = sleepy driver
# T = unauth/emergency


#custom libs
from detect import detect

#Serial Setup ###########################################################CHECK FIRST 
#ser = serial.Serial('/dev/ttyACM0', 19200, timeout=0.1) #RPI COMM
ser = serial.Serial('com3', 19200, timeout=.1) #PC COMM

#arduino outputs
temp = ""

#initialization of timer
start = time.time()
alcohol_tested = False
min_time = 20 #alcohol window

#eye tracker
eye_detect = detect()
state = 0

#initial questions
isAsked = False
isPassed = True
isClosed = True
isRunning = True 
lastValue = 0
isSendReceived = False
isYTriggered = False

def sendToArduino(ser:serial.Serial, buff:str):
	ser.flushOutput()
	ser.flushInput()
	time.sleep(3)
	for i in buff:
		ser.write(bytes(i,"ascii"))
		ser.flushInput()
	#ser.write(bytes("\n","ascii"))
	ser.flushInput()
	print("Send to Arduino: " + buff.replace('\n',''))

def playAudio(twave_file):
	subprocess.Popen(["cvlc", twave_file+".wav", "--quiet" , "vlc://quit"], shell=False)

def speaker(twav_file):
	p = pyaudio.PyAudio()
	#speaker setup
	wav_file = twav_file + ".wav"
	wf = wave.open(wav_file, 'rb')
	audio_data = wf.readframes(wf.getnframes())
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
	# Play the audio data
	stream.write(audio_data)
	stream.close()
	wf.close()
	p.terminate()

sendToArduino(ser, "B")
playAudio("Z")
while isRunning:
	state = eye_detect.getState()
	data = ser.read()  # read a single byte of data from the 
	try:
		ch = data.decode('utf-8')
	except:
		time.sleep(0)
	start_time = 0
	
	if not isAsked: #such that within time limit
		isAsked = True
		while time.time()-start < min_time:
			data = ser.read()  # read a single byte of data from the 
			try:
				ch = data.decode('utf-8')
			except:
				time.sleep(0)
			
			letters = (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z')
			nums = ch >= '0' and ch <= '9'
			reserve = ch == ':' or ch == ' ' or ch == '\r' or ch == '\n' or ch == '-'
			if nums or letters or reserve: #arduino input
				if ch == '\n':
					print("Arduino callback: " + temp.replace('\n',''))
					temp = ""
				elif ch == '\r':
					temp += ""
				else:
					temp += ch
			try:
				value = int("0"+temp)
				if value >= 450:
					isPassed = False
					min_time = -1
				else:
					isPassed = True
			except:
				#print(temp)
				if "sent" in temp:
					print("Emergency mode!!!")
					playAudio("T")
					isYTriggered = True
					min_time = -1
					if isClosed: #OPENS SERVO
						sendToArduino(ser, "A")
						isClosed = False
					'''if eye_detect.isRunning() and not isSendReceived: #if running and not yet sendrcv
						isSendReceived = True
						buff = str(-2)+"\n"
						ser.flush()
						print(buff.replace('\n',''))
						ser.write(buff.encode())
					
						print("Stopping alcohol detect...")
					'''
					if not eye_detect.isRunning() and state != -1:
						#print("Running camera...")
						eye_detect.run()
					state = eye_detect.getState()
					if state != lastValue:
						#print("Change value: ", lastValue, " > ", state)
						lastValue = state
						sendToArduino(ser, str(state))
					print("State: ", state)
					if state == -1:
						isRunning = False
	else: #natanong na kung lasing o hindi
		if isAsked and isPassed:
			if not isYTriggered: 
				playAudio("Y")
				print("YSound Triggered")
				isYTriggered = True
			if isClosed: #OPENS SERVO
				sendToArduino(ser, "A")
				isClosed = False
			'''if eye_detect.isRunning() and not isSendReceived: #if running and not yet sendrcv
				isSendReceived = True
				buff = str(-2)+"\n"
				ser.flush()
				print(buff.replace('\n',''))
				ser.write(buff.encode())
				print("Stopping alcohol detect...")
			'''
			if not eye_detect.isRunning() and state != -1:
				eye_detect.run()
			state = int(eye_detect.getState())
			if state != lastValue:
				print("Change value: ", lastValue, " > ", state)
				lastValue = state
				if lastValue == 5:
					playAudio("W")
				sendToArduino(ser, str(state))
			if state == -1:
				isRunning = False
			print("Blink_State: ", state)
			if state != -1: #Call 'detect.stop_eye()' for code equivalent
				sendToArduino(ser, str(state))
			else:
				temp_state = 6
				ser.write(temp_state.to_bytes(1,'big'))
		else:
			playAudio("X")
			sendToArduino(ser, "5")
			break
			
	
print("Servo reset")
sendToArduino(ser, "B")




    
