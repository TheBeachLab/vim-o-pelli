#!/usr/bin/env python
#
# frep.py
#    functional representation solver
#
# usage:
#    pcb.py | frep.py [dpi [filename]]
#
# Neil Gershenfeld 9/30/19
# (c) Massachusetts Institute of Technology 2019
#
# Modified by Francisco Sanchez Arroyo 2020
#
# This work may be reproduced, modified, distributed,
# performed, and displayed for any purpose, but must
# acknowledge this project. Copyright is retained and
# must be preserved. The work is provided as is; no
# warranty is provided, and users accept all liability.
#

#
# import
#

import json,sys
from numpy import *
from PIL import Image

#
# read input
#

frep = json.load(sys.stdin)

#
# check arguments
#
if (frep['type'] != 'RGB'):
   print('types other than RGB not (yet) supported')
   sys.exit()
if (len(sys.argv) == 1):
   print('output to out.png at 100 DPI')
   filename = 'out.png'
   dpi = 100
elif (len(sys.argv) == 2):
   dpi = sys.argv[1]
   filename = 'out.png'
   print(('output to out.png at '+dpi+'DPI'))
   dpi = int(dpi)
elif (len(sys.argv) == 3):
   dpi = sys.argv[1]
   filename = sys.argv[2]
   print(('output to '+filename+' at '+dpi+' DPI'))
   dpi = int(dpi)

#
# evaluate
#

print('evaluating')
xmin = frep['xmin']
xmax = frep['xmax']
ymin = frep['ymin']
ymax = frep['ymax']
units = float(frep['mm_per_unit'])
delta = (25.4/dpi)/units
x = arange(xmin,xmax,delta) # arange creates a int32 array by default
y = flip(arange(ymin,ymax,delta),0)
X = outer(ones(y.size),x)
Y = outer(y,ones(x.size))
if (len(frep['layers']) == 1):
   Z = frep['layers'][0]
   print("   z =",Z)
   f = eval(frep['function']).astype(uint32) # evals and stores as 32 bit integer
else:
   f = zeros((y.size,x.size),dtype=uint32)
   zmin = min(frep['layers'])
   zmax = max(frep['layers'])
   for Z in frep['layers']:
      print("   z =",Z)
      i = int(255*(Z-zmin)/(zmax-zmin)) | (255 << 8) | (255 << 16)
      flayer = i & (eval(frep['function'])).astype(uint32)
      f = f + flayer

#
# construct image
#

# create an array of 3 matrix made of 8 bits unsigned integers, each one y rows and x columns, populate with zeroes (black)
# each matrix holds values or R,G,B. Using channels-last convention

m = zeros((y.size,x.size,3),dtype=uint8)

# put back the 24 bit decimal value to R, G and B channels
# is f made out of zeros and ones?
m[:,:,0] = (f & 255) # Red channel.  255 = 1111 1111 operator & is a mask to get the 8 first bits
m[:,:,1] = ((f >> 8) & 255) # Green
m[:,:,2] = ((f >> 16) & 255) # Blue

# generates a RGB image from the matrix
im = Image.fromarray(m,'RGB')
# save the image, and append the xy dpi values
im.save(filename,dpi=[dpi,dpi])
