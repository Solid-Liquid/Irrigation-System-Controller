#Irrigation Hardware 2019
#LCD for irrigation system

import I2C_LCD_driver
import time
import datetime
import RPi.GPIO as GPIO
import spidev
import time
import os
import dht11

#Import code from external files:
from valveControl import *

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

##D-PAD CODE DELETE LATER
GPIO.setup(26, GPIO.IN)
GPIO.setup(19, GPIO.IN)
GPIO.setup(13, GPIO.IN)
GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.IN)
##D-PAD CODE DELETE LATER

#lcd setup
mylcd = I2C_LCD_driver.lcd()

#scrolling setup 
str_pad = " " * 16

#analog stick variables
delay = 0.05
swt_channel = 0
vry_channel = 2
vrx_channel = 1

#Create SPI
##spi = spidev.SpiDev()
##spi.open(0, 0)
##spi.max_speed_hz = 3900000

#function for reading x and y values 
'''
def readadc(adcnum):
    # read SPI data from the MCP3008, 8 channels in total
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data
    '''

#get IPaddress of pi
def getIP():
    myCmd = os.popen("hostname -I").read()
    text = str(myCmd).split(' ')[0]
    return text


#setup menu
row = 0
col = 1
rowD = 0  #row for device menu
colD = 1  #col for device menu
menuTog = False
num = 0
ipAddress = getIP()
tempData = 0
humidData = 0
menuArray = [["Main Menu", datetime.datetime.now().strftime("%m/%d, %H:%M:%S")],
             ["Device Select"],
             ["Temperature", tempData, " F    "],
             ["Humidity", humidData, " %    "],
             ["IP Address", ipAddress],
             ["Reset",""]]
flowSensorData = 0
deviceArray = [["Device Menu", "device #: " , num],
               ["FlowSensor", "data: ", flowSensorData, " gpm"],
               ["Valves"],
               #["Status"],
               ["Reset",""],
               ["Back",""]]
    
for i in range(16):
    if i==0:
        menuArray[1].append("%s%s%s" %("    Device ", i+1, "   >"))
        deviceArray[2].append("%s%s%s" %("    Valve ", i+1, "    >"))
    elif i==15:
        menuArray[1].append("%s%s%s" %("<   Device ", i+1, "   "))
        deviceArray[2].append("%s%s%s" %("<   Valve ", i+1, "    "))
    elif i>8:
        menuArray[1].append("%s%s%s" %("<   Device ", i+1, "  >"))
        deviceArray[2].append("%s%s%s" %("<   Valve ", i+1, "   >"))
    else:
        menuArray[1].append("%s%s%s" %("<   Device ", i+1, "   >"))
        deviceArray[2].append("%s%s%s" %("<   Valve ", i+1, "    >"))
    
#menuArray[1].append("")

'''
for i in range(16):
    if i < 9 :
        deviceArray[2].append("%s %s %s" %("valve",i+1, "     OFF"))
        deviceArray[3].append("%s %s %s" %("valve", i+1, " WORKING"))
    else:    
        deviceArray[2].append("%s %s %s" %("valve",i+1, "    OFF"))
        deviceArray[3].append("%s %s %s" %("valve", i+1, "WORKING"))
'''

#deviceArray[2].append("")
#deviceArray[3].append("")

def clear():    
    mylcd.lcd_clear()
    

def update():
    global ipAdress
    menuArray[0][1] = datetime.datetime.now().strftime("%m/%d, %H:%M:%S")
    lcd_text1 = menuArray[row][0]
                
    if row == 2:
        instance = dht11.DHT11(pin = 4)
        result = instance.read()
        if result.is_valid():
           tempData = result.temperature
           menuArray[2][1] = tempData
        lcd_text2 = str(menuArray[row][col]) + menuArray[row][2]
    elif row ==3:
        instance = dht11.DHT11(pin = 4)
        result = instance.read()
        if result.is_valid():
            humidData = result.humidity
            menuArray[3][1] = humidData
        lcd_text2 = str(menuArray[row][col]) + menuArray[row][2]
    elif row == 4:
        ipAddress = getIP()
        lcd_text2 = menuArray[row][col]
    else:
        lcd_text2 = menuArray[row][col]
        
    mylcd.lcd_display_string(lcd_text1, 1)
    mylcd.lcd_display_string(lcd_text2, 2)
    

def MainMenu():

    global row, col
    
    ##D-PAD CODE DELETE LATER
    swt_value = 500
    vry_value = 500
    vrx_value = 500
    
    select = GPIO.input(5)
    if select == False:
        swt_value = 0
    else:
        swt_value = 100
        
    up = GPIO.input(26)
    if up == False:
        vrx_value = 0
        
    down = GPIO.input(19)
    if down == False:
        vrx_value = 1001
        
    left = GPIO.input(13)
    if left == False:
        vry_value = 0
        
    right = GPIO.input(6)
    if right == False:
        vry_value = 1001
    ##END D-PAD CODE
       
    #x and y values
    ##swt_value = readadc(swt_channel)
    ##vry_value = readadc(vry_channel)
    ##vrx_value = readadc(vrx_channel)
    
   
    

    if vrx_value < 20:
        #up
        if row-1 == -1:
            row = 5
        else:
            row -= 1
        col = 1
        clear()
        update()
        time.sleep(.1)
    elif vrx_value > 1000:
        #down
        if row + 1 > 5:
            row = 0
        else:
            row += 1
        col = 1
        clear()
        update()
        time.sleep(.1)
    elif vrx_value > 20 and vrx_value < 1000:
        #standby update
        update()
    if (vry_value < 20) and (len(menuArray[row]) > col+1) and (row != 2) and (row != 3):
        #right
        col += 1
        clear()
        update()
        time.sleep(.1)
    elif vry_value > 1000 and (col - 1 > 0):
        #left
        col -= 1
        clear()
        update()
        time.sleep(.1)
    if swt_value < 10:
        #select
        if row == 1:
            clear()
            global menuTog, rowD, colD
            menuTog = True
            rowD = 0
            deviceArray[0][2] = col
            colD = 1
            clear()
            update2()
            time.sleep(.1)


def update2():
    global rowD, colD

    lcd_text1 = deviceArray[rowD][0]
    #Flow sensor data string has a String, int, then a string
    if rowD == 0:
        #Device menu / device number
        lcd_text2 = str(deviceArray[rowD][colD]) + str(deviceArray[rowD][2])
    elif rowD == 1:
        #FlowSensor / gpm readout
        lcd_text2 = str(deviceArray[rowD][colD]) + str(deviceArray[rowD][2]) + deviceArray[rowD][3]
    elif rowD == 2:
        #Valve number / valve status
        lcd_text1 = str(deviceArray[rowD][colD])
        #TODO: get actual valve status here
        board = (deviceArray[0][2] - 1)
        valve = colD - 1
        on = valveIsOn(board,valve)
        lcd_text2 = "WORKING    "
        if on:
            lcd_text2 += " [ON]"
        else:
            lcd_text2 += "[OFF]"
    else:
        lcd_text2 = str(deviceArray[rowD][colD])

    mylcd.lcd_display_string(lcd_text1, 1)
    mylcd.lcd_display_string(lcd_text2, 2)
        

def DeviceMenu():
    global rowD, colD
    
    ##D-PAD CODE DELETE LATER
    swt_value = 500
    vry_value = 500
    vrx_value = 500
    
    select = GPIO.input(5)
    if select == False:
        swt_value = 0
    else:
        swt_value = 100
        
    up = GPIO.input(26)
    if up == False:
        vrx_value = 0
        
    down = GPIO.input(19)
    if down == False:
        vrx_value = 1001
        
    left = GPIO.input(13)
    if left == False:
        vry_value = 0
        
    right = GPIO.input(6)
    if right == False:
        vry_value = 1001
    ##END D-PAD CODE
    
    #x and y values
    ##swt_value = readadc(swt_channel)
    ##vry_value = readadc(vry_channel)
    ##vrx_value = readadc(vrx_channel)


    if vrx_value < 20:
        #up
        if rowD-1 == -1:
            rowD = 4
        else:
            rowD -= 1
        colD = 1
        clear()
        update2()
        time.sleep(.1)
    elif vrx_value > 1000:
        #down
        if rowD + 1 > 4:
            rowD = 0
        else:
            rowD += 1
        colD = 1
        clear()
        update2()
        time.sleep(.1)
    elif vry_value < 20 and (len(deviceArray[rowD]) > colD+1) and rowD > 1:
        #right
        colD += 1
        clear()
        update2()
        time.sleep(.1)
    elif vry_value > 1000 and (colD - 1 > 0):
        #left
        colD -= 1
        clear()
        update2()
        time.sleep(.1)
    elif swt_value < 10:
        #select
        if (rowD == 4) or (rowD == 0):
            global menuTog
            menuTog = False
            rowD = 0
            colD = 1
            clear()
            update()
        elif rowD == 2:
            board = (deviceArray[0][2] - 1)
            valve = colD - 1
            if valveIsOn(board,valve):
                valveOff(board,valve)
            else:
                valveOn(board,valve)
            #print("board",board,"valve",valve)
            #print(valveIsOn(board,valve))
            update2()
        time.sleep(.2)
    else:
        update2()

'''
def startMainLoop():
    update()
    try:
        while True:
            if menuTog is False:
                MainMenu()
            elif menuTog is True:
                DeviceMenu()
            
    finally:
        clear()

startMainLoop()
'''

#Initialize LCD code:
def setupLCD():
    update()

#Code to run each time for main loop:
def processLCD():
    #maybe put try except here
    if menuTog is False:
        MainMenu()
    elif menuTog is True:
        DeviceMenu()

#Main:
setupLCD()
