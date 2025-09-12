# splice recap (9/12/25)

#myName = "Jeremiah Jones"
#spaceLoc = myName.index(" ")
#print(f"Location of space : {spaceLoc} | Before: {myName[:spaceLoc]} | After: {myName[spaceLoc + 1:]}")

# TKINTER GUI - PYTHON BOOK 9/12

import tkinter as tk
from tkinter import ttk

root = tk.Tk()

window = ttk.Frame(root, padding=10)
window.grid()

text = ""

title = tk.Label(window, text = "Please input your name").grid(column=0, row=1)
text = tk.Entry(window, text="name goes here", textvariable=text).grid(column=0, row=2)
button = tk.Button(window, text="print", command=().grid(column=0, row=3)
root.mainloop() # initalize