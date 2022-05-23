import OpenGL

OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL.GL.shaders import *
import numpy as np
from PIL import Image

import sys

program = None

binary = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int16)
X = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[0]
Y = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[1]
Z = np.fromfile(r"C:\Users\aunik\Downloads\testdata.bin", dtype=np.int32)[2]
value_scale = 40

max = np.max(binary)
min = np.min(binary)

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


def InitGL(Width, Height, texture_image):
    glClearColor(0.0, 0.0, 0.0, 0.0)

    glBindTexture(GL_TEXTURE_2D, 0)

    glTexImage2D(GL_TEXTURE_2D,
                 0,
                 GL_RGB,
                 texture_image.size[0],
                 texture_image.size[1],
                 0,
                 GL_RGBA,
                 GL_UNSIGNED_BYTE,
                 np.array(list(texture_image.getdata()), np.uint8))

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(80.0, window_height / window_width, 0.01, 100.0)

    glMatrixMode(GL_MODELVIEW)

    global program

    program = compileProgram(
        compileShader('''
            varying vec2 pos;
            uniform float texture_width;
            uniform float texture_height;

            void main() {

                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                pos = gl_MultiTexCoord0.st;

            }
        ''', GL_VERTEX_SHADER),
        compileShader('''
            varying vec2 pos;
            uniform sampler2D s_texture;

            void main() {
                float tx = pos.x;
                float ty = pos.y;
                float R;
                float G;
                float B;
                float gamma = 0.25;

                R = pow(texture2D(s_texture,vec2(tx,ty)).r, gamma);
                G = pow(texture2D(s_texture,vec2(tx,ty)).g, gamma);
                B = pow(texture2D(s_texture,vec2(tx,ty)).b, gamma);

                gl_FragColor = vec4(R,G,B,1.0);
            }
    ''', GL_FRAGMENT_SHADER), )

def keyboard_function(button, x ,y):
    global value_scale
    if button == GLUT_KEY_RIGHT:
        value_scale += 1
        if value_scale > Z - 1:
            value_scale = Z - 1
        texture = createTexture(value_scale)
        glTexImage2D(GL_TEXTURE_2D,
                 0,
                 GL_RGB,
                 texture_image.size[0],
                 texture_image.size[1],
                 0,
                 GL_RGBA,
                 GL_UNSIGNED_BYTE,
                 np.array(list(texture.getdata()), np.uint8))
    if button == GLUT_KEY_LEFT:
        value_scale -= 1
        if value_scale < 0:
            value_scale = 0
        texture = createTexture(value_scale)
        glTexImage2D(GL_TEXTURE_2D,
                 0,
                 GL_RGB,
                 texture_image.size[0],
                 texture_image.size[1],
                 0,
                 GL_RGBA,
                 GL_UNSIGNED_BYTE,
                 np.array(list(texture.getdata()), np.uint8))

def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT)

    glLoadIdentity()

    glTranslatef(0, 0, -7)

    glUseProgram(program)

    glEnable(GL_TEXTURE_2D)
    #glEnable(GL_FRAMEBUFFER_SRGB)

    glBegin(GL_QUAD_STRIP)

    glVertex3f(-5, -5, 0)
    glTexCoord2f(0, 0)

    glVertex3f(-5, 5, 0)
    glTexCoord2f(1, 1)

    glVertex3f(5, -5, 0)
    glTexCoord2f(1, 0)

    glVertex3f(5, 5, 0)
    glTexCoord2f(0, 1)

    glEnd()

    glFlush()


global window
glutInit(sys.argv)

texture_image = createTexture(value_scale)
window_width, window_height = texture_image.size

glutInitWindowSize(window_width, window_height)
glutInitWindowPosition(100, 100)
window = glutCreateWindow("Tomogram_QuadStrip")

glutDisplayFunc(DrawGLScene)
glutIdleFunc(DrawGLScene)
glutSpecialFunc(keyboard_function)
InitGL(window_width, window_height, texture_image)

glutMainLoop()