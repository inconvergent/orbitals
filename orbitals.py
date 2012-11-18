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
NUM    = 800          # number of nodes
BACK   = 1.           # background color 
OUT    = 'x07.img'    # resulting image name
IN     = './dots'
RAD    = 0.4      # radius of starting circle
GRAINS = 1000
STP    = 0.0001   # scale motion in each iteration by this
steps  = 3000     # iterations
MAXFS  = 100       # max friendships pr node

def pInit(X,Y):
  for i in xrange(0,NUM):
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
  for i in xrange(0,NUM):
    dx = X[i] - X
    dy = Y[i] - Y
    R[i,:] = np.sqrt(dx*dx+dy*dy)
    A[i,:] = np.arctan2(dy,dx)

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

def makeFriends(i,R,F):
  if (F[i,:].sum()) > MAXFS:
    return

  r = []
  for j in xrange(0,NUM):
    if i != j and F[j,:].sum() < MAXFS\
      and not F[j,i]:
        r.append([R[i,j],j])
  if not len(r):
    return
  r = sorted(r, key=itemgetter(0))

  index = len(r)-1
  for k in xrange(0,len(r)):
    if random() < 0.1:
      index = k
      break
 
  F[i,r[index][1]] = True
  F[r[index][1],i] = True

  return

def run(X,Y,SX,SY,R,A,F,NEARL,FARL):
  setDistances(X,Y,R,A)
  
  SX[:] = 0.
  SY[:] = 0.
  
  for i in xrange(0,NUM):
    xF        = np.logical_not(F[i,:].toarray()).flatten()
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

  X += SX*STP
  Y += SY*STP
  makeFriends(int(random()*NUM),R,F)
  
  return

def renderConnectionPoints(X,Y,R,A,F,ctx):
  def stroke(x,y):
      ctx.rectangle(x,y,1./N,1./N)
      ctx.fill()
      return
  vstroke = np.vectorize(stroke)

  alpha = 15./256.
  colors = getColors('./resources/colors2.gif')

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

  print time()-t 

  return

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

  FARL  = 0.2
  NEARL = 0.02
  X  = np.zeros(NUM)
  Y  = np.zeros(NUM)
  SX = np.zeros(NUM)
  SY = np.zeros(NUM)

  R = np.zeros((NUM,NUM))
  A = np.zeros((NUM,NUM))

  F  = lil_matrix((NUM,NUM),dtype=np.byte).tocsr()

  pInit(X,Y)
  
  t0 = time()

  for i in xrange(0,steps):
    if not i%200:
      sur.write_to_png('test.png')
      print i,time()-t0
      t0 = time()
    run(X,Y,SX,SY,R,A,F,NEARL,FARL)
    renderConnectionPoints(X,Y,R,A,F,ctx)

  return

if __name__ == '__main__' : main()
