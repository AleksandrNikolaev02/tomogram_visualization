import tkinter
from tkinter import *
from PIL import Image, ImageTk
import numpy as np

binary = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int16)
X = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[0]
Y = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[1]
Z = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[2]
value_scale = 0

def clamp(value, min, max):
    res = 0
    if min<=value<=max:
        res = value
    if value<min:
        res = min
    if max<value:
        res = max
    return res

def TransferFunction(value):
    min = 0
    max = 2000
    pixel = ()
    newVal = clamp((value - min) * 255 // (max - min), 0, 255)
    if newVal > 0 and newVal<=85:
        pixel = (newVal, newVal, newVal, 255)
    elif newVal >= 86 and newVal<=170:
        pixel = (0, 0, 255, 255)
    elif newVal >= 171 and newVal<=255:
        pixel = (255, 0, 0, 255)
    else:
        pixel = (newVal, newVal, newVal, 255)
    return pixel

def createTexture(layerNumber):
    textureImage = Image.new('RGBA', (X, Y))
    for i in range(X):
        for j in range(Y):
            pixelNumber = i + j * X + layerNumber * X * Y
            textureImage.putpixel((i, j), TransferFunction(binary[pixelNumber]))
    return textureImage

class App:
    def __init__(self):
        self.root = tkinter.Tk()

        self.frame = tkinter.Frame(self.root)
        self.frame.grid()

        global value_scale
        if value_scale > 77:
            value_scale = 77
        if value_scale < 0:
            value_scale = 0
        self.image = createTexture(value_scale)
        self.photo = ImageTk.PhotoImage(self.image)

        #v = tkinter.DoubleVar()
        #self.scale = tkinter.Scale(self.root, variable=v, from_=0, to= Z - 1, orient=tkinter.HORIZONTAL, length=400).grid(row=1, column=0)
        #self.scale = tkinter.Scale(self.root, variable=v, from_=0, to= Z - 1, orient=tkinter.HORIZONTAL, length=400).set(10)

        self.root.bind_all("<KeyPress-Right>", self.scroll)
        self.root.bind_all("<KeyPress-Left>", self.scroll)

        self.canvas = tkinter.Canvas(self.root, height=X, width=Y)
        self.c_image = self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.canvas.grid(row=0, column=0)
        self.root.mainloop()

    def scroll(self, event):
        global value_scale
        if event.keysym == 'Right':
            value_scale += 1
            if value_scale > 77:
                value_scale = 77
            self.image = createTexture(value_scale)
            self.photo = ImageTk.PhotoImage(self.image)
            self.c_image = self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
            self.canvas.grid(row=0, column=0)
        if event.keysym == 'Left':
            value_scale -= 1
            if value_scale < 0:
                value_scale = 0
            self.image = createTexture(value_scale)
            self.photo = ImageTk.PhotoImage(self.image)
            self.c_image = self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
            self.canvas.grid(row=0, column=0)

app= App()