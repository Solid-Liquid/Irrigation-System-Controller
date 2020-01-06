#Irrigation Hardware 2019
#Code for using the PI to control valves on the STM

import RPi.GPIO as GPIO
import smbus
import time

#i2c communication bus:
bus = smbus.SMBus(1)
#Array of STM boards (True means board connected):
boards = [False] * 16

#Schedule 3D List: 16 boards x 16 valves x 4 statuses:
#Statuses: (0: Valve On/Off), (1: Problem), (2: Start Time), (3: End Time)
#(0) indicates if the valve has been set On/Off (True/False)
#(1) set True means there is a problem with the valve or i2c communcation
schedule = [[[False,False,0,0] for y in range(16)] for x in range(16)]
ON = 0
PROBLEM = 1
START = 2
STOP = 3

#Returns the address of a board based on board number:
def boardAddr(boardNum):
	return 40 + boardNum


#Ping all 16 board addresses to see which addresses are connected:
#If a board is connected, set True in the array of boards.
def boardSetup():
	print("Setup:")
	i = 0;
	while i < 16:
		try:
			bus.read_byte(boardAddr(i))
			print("  Board", i, "  CONNECTED")
			boards[i] = True
		except:
			print("  Board", i)
		i += 1
	return


#Turn on a valve (Board 0-15, Valve 0-15):
def valveOn(board, valve):
	if not sendCmd(board, valve):
		return False
	schedule[board][valve][ON] = True
	#time.sleep(.1)
	cmd = readCmd(board)
	#TODO handle more commands
	#set problem flag if problem schedule[board][valve][PROBLEM]
	if cmd == -1:
		return False
	return True


#Turn off a valve (Board 0-15, Valve 0-15):
def valveOff(board, valve):
	if not sendCmd(board, valve + 16):
		return False
	schedule[board][valve][ON] = False
	#time.sleep(.1)
	cmd = readCmd(board)
	#TODO handle more commands
	#set problem flag if problem schedule[board][valve][PROBLEM]
	if cmd == -1:
		return False
	return True
	

#Schedule when a valve should turn on (Board 0-15, Valve 0-15):
def setStartTime(board, valve, startTime):
	schedule[board][valve][START] = startTime


#Schedule when a valve should turn off (Board 0-15, Valve 0-15):
def setStopTime(board, valve, stopTime):
	schedule[board][valve][STOP] = stopTime


#Return true if a valve is on (Board 0-15, Valve 0-15):
def valveIsOn(board, valve):
	return schedule[board][valve][ON]


#Return true if a valve has a problem (Board 0-15, Valve 0-15):
def valveProblem(board, valve):
	return schedule[board][valve][PROBLEM]


#Helper function for sending command to STM:
def sendCmd(board, cmd):
	if boards[board] != True:
		return False
	try:
		bus.write_byte(boardAddr(board), cmd)
		return True
	except:
		print("Communication error with board", board)
		return False


#Helper function for reading command from STM:
def readCmd(board):
	if boards[board] != True:
		return -1
	try:
		msg = bus.read_byte(boardAddr(board))
		return msg
	except:
		print("Communication error with board", board)
		return -1


#Run a hardcoded 'Bellagio' sequence 
def bellagio():
	if boards[0]:
		ct = time.time()
		setStartTime(0,0,ct)
		setStartTime(0,1,ct+2)
		setStartTime(0,2,ct+4)
		setStartTime(0,3,ct+6)
		setStartTime(0,4,ct+8)
		setStartTime(0,5,ct+10)
		setStartTime(0,6,ct+12)
		setStopTime(0,0,ct+4)
		setStopTime(0,1,ct+6)
		setStopTime(0,2,ct+8)
		setStopTime(0,3,ct+10)
		setStopTime(0,4,ct+12)
		setStopTime(0,5,ct+14)
		setStopTime(0,6,ct+16)


#Bellagio sequence, sweep from middle to out, hard coded for 6 valves on board 0							
def bellagioCentered():
	if boards[0]:
		ct = time.time()
		setStartTime(0,0,ct+4)
		setStartTime(0,1,ct+2)
		setStartTime(0,2,ct)
		setStartTime(0,3,ct)
		setStartTime(0,4,ct+2)
		setStartTime(0,5,ct+4)
		setStopTime(0,0,ct+8)
		setStopTime(0,1,ct+6)
		setStopTime(0,2,ct+4)
		setStopTime(0,3,ct+4)
		setStopTime(0,4,ct+6)
		setStopTime(0,5,ct+8)
		

#Hard coded, turn all valves (0-6) on at once for a set time:
def allOnDemo():
	if boards[0]:
		ct = time.time()
		setStartTime(0,0,ct)
		setStartTime(0,1,ct)
		setStartTime(0,2,ct)
		setStartTime(0,3,ct)
		setStartTime(0,4,ct)
		setStartTime(0,5,ct)
		setStartTime(0,6,ct)
		ct += 5
		setStopTime(0,0,ct)
		setStopTime(0,1,ct)
		setStopTime(0,2,ct)
		setStopTime(0,3,ct)
		setStopTime(0,4,ct)
		setStopTime(0,5,ct)
		setStopTime(0,6,ct)
		

#Check the schedule to see if the state of any valve needs to change:
def checkSchedule():
	for b in range(0,16):
		if boards[b]:
			for v in range(0,16):
				vl = schedule[b][v] #statuses of one valve

				if vl[PROBLEM] or (vl[START] == 0) or (vl[STOP] == 0):  
					continue    #skip valve if not scheduled, or there is a problem

				if (not vl[ON]) and (time.time() >= vl[START]):
					#Valve off and time >= start time, so turn on valve
					valveOn(b,v)
					#return
				elif vl[ON] and (time.time() >= vl[STOP]):
					#Valve on and time >= stop time, so turn off valve
					setStartTime(b,v,0)
					setStopTime(b,v,0)
					valveOff(b,v)
					#return

		
#Main:
boardSetup()
