#!/usr/bin/python
# -*- coding: utf-8 -*-

import cairo,Image
from math import log, sin, cos, pi, atan2, sqrt
from random import random
from operator import itemgetter
from time import time
import numpy as np

import matplotlib.pyplot as plt


PI     = pi
PII    = PI*2.

N      = 500       # size of png image
ONE    = 1./float(N)
NUM    = 50          # number of nodes
BACK   = 1.           # background color 
OUT    = 'orbitals.tmp.a'    # resulting image name
RAD    = 0.4      # radius of starting circle
GRAINS = 300
STP    = 0.001   # scale motion in each iteration by this
steps  = 3000     # iterations
MAXFS  = 5       # max friendships pr node
ALPHA  = 0.05

def pInit(X,Y):
  for i in xrange(NUM):
    the = random()*PII
    x = RAD * sin(the)
    y = RAD * cos(the)
    X[i] = 0.5+x
    Y[i] = 0.5+y
  return

def ctxInit():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx

def setDistances(X,Y,R,A):
  for i in xrange(NUM):
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
  for i in xrange(w):
    for j in xrange(h):
      r,g,b = rgbim.getpixel((i,j))
      key = '{:03d}{:03d}{:03d}'\
        .format(r,g,b)
      res[key] = (r/scale,g/scale,b/scale)
  res = [value for key,value in res.iteritems()]
  return res

def makeFriends(i,R,F):
  
  if F[i,:].sum() > MAXFS:
    return

  r = []
  for j in xrange(NUM):
    if i != j and F[j,:].sum() < MAXFS\
      and not F[j,i]:
        r.append((R[i,j],j))
  if not len(r):
    return
  r = sorted(r, key=itemgetter(0))

  index = len(r)-1
  for k in xrange(len(r)):
    if random() < 0.1:
      index = k
      break

  # this is bad for csc, csr matrix 
  F[i,r[index][1]] = True
  F[r[index][1],i] = True
  return

def renderConnectionPoints(X,Y,R,A,F,ctx,colors,alpha=ALPHA):
  def stroke(x,y):
      ctx.rectangle(x,y,1./N,1./N)
      ctx.fill()
      return
  vstroke = np.vectorize(stroke)


  lc = len(colors)
  t = time()
  indsx,indsy = F.nonzero()
  mask = indsx >= indsy 
  for i,j in zip(indsx[mask],indsy[mask]):
    a = A[i,j] ; d = R[i,j]

    scales = np.random.random(GRAINS)*d
    xp = X[i] - scales*np.cos(a)
    yp = Y[i] - scales*np.sin(a)
    
    c = colors[ (i*NUM+j) % lc ]
    ctx.set_source_rgba(c[0],c[1],c[2],alpha)

    vstroke(xp,yp)
  return

def run(X,Y,SX,SY,R,A,F,NEARL,FARL):

  setDistances(X,Y,R,A)
  
  SX[:] = 0.; SY[:] = 0.
  
  for i in xrange(NUM):
    xF        = np.logical_not(F[i,:])
    d         = R[i,:]
    a         = A[i,:]
    near      = d > NEARL
    near[xF]  = False
    far       = d < FARL
    far[near] = False
    near[i]   = False
    far[i]    = False
    speed     = FARL - d[far]

    SX[near] += np.cos(a[near])
    SY[near] += np.sin(a[near])
    SX[far]  -= speed*np.cos(a[far])
    SY[far]  -= speed*np.sin(a[far])

  X += SX*STP + (1-2*np.random.random(X.shape))*ONE
  Y += SY*STP + (1-2*np.random.random(Y.shape))*ONE
  makeFriends(int(random()*NUM),R,F)

  return

def main():

  sur,ctx = ctxInit()

  FARL  = 0.15
  NEARL = 0.1
  X  = np.zeros(NUM,        dtype=np.float)
  Y  = np.zeros(NUM,        dtype=np.float)
  SX = np.zeros(NUM,        dtype=np.float)
  SY = np.zeros(NUM,        dtype=np.float)
  R  = np.zeros((NUM,NUM),  dtype=np.float)
  A  = np.zeros((NUM,NUM),  dtype=np.float)
  F  = np.zeros((NUM,NUM),  dtype=np.byte)

  #colors = getColors('./resources/colors3.gif')
  colors = [(0.,0.,0.)]

  pInit(X,Y)
 
  plt.ion()
  plt.figure()

  t = 0
  for i in xrange(steps):
    run(X,Y,SX,SY,R,A,F,NEARL,FARL)
    #renderConnectionPoints(X,Y,R,A,F,ctx,colors)

    if not i%20:
      plt.clf()
      plt.plot(X,Y,'ro')
      plt.xlim([0,1])
      plt.ylim([0,1])
      plt.draw()
      print time()-t
      t = time()

    #if not (i+1)%200:
      #sur.write_to_png('{:s}.{:d}.png'.format(OUT,i+1))
  return

if __name__ == '__main__' : main()

