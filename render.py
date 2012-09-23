#!/usr/bin/python
# -*- coding: utf-8 -*-

import cairo,Image
from math import log, sin, cos, pi, atan2, sqrt
from random import random
from operator import itemgetter
from time import time
import numpy as np
import pickle as pkl
from scipy.sparse import lil_matrix

PI     = pi
PII    = PI*2.

N      = 10000        # size of png image
NUM    = 300          # number of nodes
BACK   = 1.           # background color 
OUT    = 'x05.img'    # resulting image name
IN     = './001run0.02x0.2/dots'
GRAINS = 1000

def print_timing(func):
  def wrapper(*arg):
    t1=time()
    res=func(*arg)
    t2=time()
    print '%s:\t%0.3f' % (func.func_name, (t2-t1)*1000.0)
    return res
  return wrapper

def ctxInit():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx

def setDistances(X,Y,R,A):
  for i in xrange(0,NUM):
    dx = X[i] - X
    dy = Y[i] - Y
    R[i,:] = np.sqrt(dx*dx+dy*dy)
    A[i,:] = np.arctan2(dy,dx)

  return

def getColors(f):
  scale = 255.
  im = Image.open(f)
  w,h = im.size
  rgbim = im.convert('RGB')
  res = {}
  for i in xrange(0,w):
    for j in xrange(0,h):
      r,g,b = rgbim.getpixel((i,j))
      key = '{:03d}{:03d}{:03d}'\
        .format(r,g,b)
      res[key] = [r/scale,g/scale,b/scale]
  res = [value for key,value in res.iteritems()]

  return res

#@print_timing
def renderConnectionPoints(X,Y,R,A,F,ctx):
  alpha = 15./256.
  colors = getColors('./resources/colors2.gif')
  lc = len(colors)
  for i in xrange(0,NUM):
    for j in xrange(i+1,NUM):
      if F[i,j]:
        a = A[i,j] ; d = R[i,j]

        scales = np.random.random(GRAINS)*d
        xp = X[i] - scales*np.cos(a)
        yp = Y[i] - scales*np.sin(a)
      
        c = colors[ (i*NUM+j) % lc ]
        ctx.set_source_rgba(c[0],c[1],c[2],alpha)
        for q in xrange(0,GRAINS):
          ctx.rectangle(xp[q],yp[q],1./N,1./N)
        ctx.fill()

  return

@print_timing
def renderSteps(STEP,GRID,batch,ctx,sur):

  stps = len(STEP)
  r = np.zeros((NUM,NUM))
  a = np.zeros((NUM,NUM))
   
  for i in xrange(0,stps):
    x,y,f = STEP[i]
    setDistances(x,y,r,a)
    renderConnectionPoints(x,y,r,a,f,ctx)
    if not (i+1) % 100:
      s = '{:s}.{:03d}.{:03d}.png'\
          .format(OUT,batch,i)
      sur.write_to_png(s)
      print i, s

  return

def main():
  
  sur,ctx = ctxInit()

  GRID = np.zeros((N,N))
  for i in xrange(0,5):
    nameroot = '{:s}{:04d}'.format(IN,i)
    name     = '{:s}.pkl'.format(nameroot)
    print 'reading {:s} ... '.format(name)
    f = open(name,'rb')
    STEP = pkl.load(f)
    print 'opened ... {:d} entries'.format(len(STEP))
    f.close()
    renderSteps(STEP,GRID,i,ctx,sur)

    #paintGrid(ctx,GRID)
    #sur.write_to_png('{:s}.{:03d}.png'.format(OUT,i))

  return


if __name__ == '__main__': main()

