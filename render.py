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
OUT    = '1.large.img'  # resulting image name
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

#def getColors(f):
  #scale = 255.
  #im = Image.open(f)
  #w,h = im.size
  #rgbim = im.convert('RGB')
  #res = {}
  #for i in xrange(0,w):
    #for j in xrange(0,h):
      #r,g,b = rgbim.getpixel((i,j))
      #key = '{:03d}{:03d}{:03d}'\
        #.format(r,g,b)
      #res[key] = [r/scale,g/scale,b/scale]
  #res = [value for key,value in res.iteritems()]

  #return res

def getConnectionPoints(X,Y,R,A,F,GRID):

  for i in xrange(0,NUM):
    for j in xrange(i+1,NUM):
      if F[i,j]:
        a = A[i,j] ; d = R[i,j]

        scales = np.random.random(GRAINS)*d
        xp = np.int32((X[i] - scales*np.cos(a))*N)
        yp = np.int32((Y[i] - scales*np.sin(a))*N)
      
        for q in xrange(0,GRAINS):
          GRID[xp[q],yp[q]] += 1

  return

@print_timing
def paintGrid(ctx,G):
  alpha = 0.005
  beta = 1.-alpha
  cG = beta**G
  cG = cG**2. # gamma

  for i in xrange(0,N):
    ii = float(i)/N
    for j in xrange(0,N):
      if G[i,j]: 
        ig = cG[i,j]
        ctx.set_source_rgb(ig,ig,ig)
        ctx.rectangle(ii,float(j)/N,1./N,1./N)
        ctx.fill()

  return

@print_timing
def renderSteps(STEP,GRID):

  stps = len(STEP)
  r = np.zeros((NUM,NUM))
  a = np.zeros((NUM,NUM))
   
  for i in xrange(0,stps):
    x,y,f = STEP[i]
    setDistances(x,y,r,a)
    getConnectionPoints(x,y,r,a,f,GRID)
    if not i % 100:
      print i

  return

def main():
  
  sur,ctx = ctxInit()

  GRID = np.zeros((N,N))
  for i in xrange(0,5):
    nameroot = 'dots{:04d}'.format(i)
    name     = '{:s}.pkl'.format(nameroot)
    print 'reading {:s} ... '.format(name)
    f = open(name,'rb')
    STEP = pkl.load(f)
    print 'opened ... {:d} entries'.format(len(STEP))
    f.close()
    renderSteps(STEP,GRID)
    paintGrid(ctx,GRID)

    sur.write_to_png('{:s}.{:03d}.png'.format(OUT,i))

  return


if __name__ == '__main__': main()

#def gauss_kern(size):
    #size = int(size)        
    #x, y = np.mgrid[-size:size+1, -size:size+1]
    #g = np.exp(-(x**2/float(size)+y**2/float(size)))

    #return g / g.sum()

#def showP(ctx,X,Y):
  #ctx.set_source_rgba(1,0,0,0.5)
  #for i in xrange(0,NUM):
    #ctx.move_to(X[i],Y[i])
    #ctx.arc(X[i],Y[i],2./N,0,PII)
  #ctx.close_path()
  #ctx.fill()

  #return
