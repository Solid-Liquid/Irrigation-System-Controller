#Irrigation Hardware 2019
#GUI for irrigation system

import time
import tkinter as tk
from tkinter import ttk

#Import code from external files:
from menuLCD import *

#Setup the GUI window:
win = tk.Tk()
wintitle = win.title("MASTER CONTROLLER")
grid = ttk.LabelFrame()
grid.grid(column=0, row=0, padx=8, pady=4)
win.resizable(width=None,height=None)
run = True

#Define what happens when the GUI is closed:
def quit():
	global run
	run = False
	clear()
	win.destroy()
win.protocol("WM_DELETE_WINDOW", quit)

#Setup buttons for the GUI:
action1 = ttk.Button(grid, text="Bellagio", command= bellagio)
action1.grid(column=0, row=0)
action2 = ttk.Button(grid, text="Middle Out", command= bellagioCentered)
action2.grid(column=0, row=1)
action3 = ttk.Button(grid, text="All on", command= allOnDemo)
action3.grid(column=0, row=2)

#Main loop for system:
while run:
	checkSchedule() #check valve scheduling
	processLCD() #process LCD input/output
	win.update_idletasks()
	win.update()
