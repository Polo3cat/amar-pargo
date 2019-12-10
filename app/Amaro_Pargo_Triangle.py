#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from math import *
import tkMessageBox
import os

window=Tk()
window.lift()
window.attributes("-topmost", True)
windowWidth = window.winfo_reqwidth()
windowHeight = window.winfo_reqheight()*2
positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)
window.geometry("+{}+{}".format(positionRight, positionDown))
window.resizable(0, 0)
window.title("Amaro Pargo")
window.geometry("295x320")
color_boton=("gray77")

def runClic():
	message = "Searching the video in " + url.get()
	
	if triangleSize.get() == 3:
		triangle = "big"
	elif triangleSize.get() == 1:
		triangle = "small"
	else:
		triangle = "medium"

	runable = "./main.py url " + url.get() + " --triangle_size " + triangle

	window.attributes("-topmost", False)
	tkMessageBox.showinfo("Amaro Pargo: Running...", message)
	window.attributes("-topmost", True)
	os.system (runable)
	clear()

def exitClic():
    window.destroy()

def clear():
    url_text.set("")

def sel():
    print ("Changed Triangle Size to:")
    print triangleSize.get()

title=Label(window,text="Amaro Pargo", font=("Courier", 44)).place(x=0,y=0)    

urlLabel = Label(window, text="URL:").place(x=10,y=105)
url_text = StringVar()
url = Entry(window, textvariable=url_text, bd =5)
url.place(x=75,y=100)

label = Label(window, text="Triangle Size:")
label.place(x=10,y=175)

triangleSize = IntVar()

small = Radiobutton(window, text="Small", variable=triangleSize, value=1, command=sel)
small.place(x=125,y=175)

medium = Radiobutton(window, text="Medium", variable=triangleSize, value=2, command=sel)
medium.place(x=125,y=200)

large = Radiobutton(window, text="Big", variable=triangleSize, value=3, command=sel)
large.place(x=125,y=225)

BotonEnter=Button(window,text="Run",bg=color_boton,width=11,height=3,command=runClic).place(x=10,y=250)
BotonExit=Button(window,text="Exit",bg=color_boton,width=11,height=3,command=exitClic).place(x=150,y=250)

window.mainloop()