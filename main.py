#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# orbitals. andershoff.net
# inspired by complexification.net
#

import os,sys,cairo
from math import log, sin, cos, pi, atan2, sqrt
from random import random
from operator import itemgetter
from time import time
import numpy as np
from matplotlib import pylab as plt


PI     = pi
PII    = PI*2.

NUM    = 100
MAXFS  = int(NUM/6.)
NEARL  = 0.05
FARL   = 0.2

N      = 800
N2     = N/2
GRAINS = 5
BACK   = 1.
OUT    = 'img'

RAD    = 0.1 # radius of starting circle

STP    = 0.001
steps  = 100

R      = [0.]*NUM
A      = [0.]*NUM
F      = [[] for i in xrange(0,NUM)]

def ctxInit():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx

def pInit(X,Y):
  for i in xrange(0,NUM):
    the = random()*PII
    x = RAD * sin(the)
    y = RAD * cos(the)
    X[i] = 0.5+x
    Y[i] = 0.5+y
  return

def showP(ctx,X,Y):
  ctx.set_source_rgb(1,0,0)
  for i in xrange(0,NUM):
    ctx.move_to(X[i],Y[i])
    ctx.arc(X[i],Y[i],2./N,0,PII)
  ctx.close_path()
  ctx.fill()
  return

def setDistances(X,Y):
  for i in xrange(0,NUM):
    dx = X[i] - X
    dy = Y[i] - Y
    a  = np.arctan2(dy,dx)
    d  = np.sqrt(dx*dx+dy*dy)
    R[i] = d
    A[i] = a
    A[i][i+1:] += PI
  return

def makeFriends(i):
  if len(F[i]) > MAXFS:
    return

  r = []
  for j in xrange(0,NUM):
    if i != j:
      r.append((R[i][j],j))
  sorted(r, key=itemgetter(0))

  index = NUM-2
  for k in xrange(0,NUM-1):
    if random() < 0.1:
      index = k
      break
  
  for k in xrange(0,len(F[i])):
    if F[i][k] == index:
      return

  F[i].append(r[index][1])
  F[r[index][1]].append(i)
  return

def drawConnections(ctx,X,Y):
  for i in xrange(0,NUM):
    for f in xrange(0,len(F[i])):
      if i == F[i][f] or F[i][f] < i:
        continue
      dist = R[i][F[i][f]] * random()
      a = A[i][F[i][f]]

      sx = cos(a)
      sy = sin(a)
      scale = dist/GRAINS
      
      xp,yp = 0.,0.
      if random() < 0.5:
        xp = X[i]
        yp = Y[i]
      else:
        xp = X[F[i][f]]
        yp = Y[F[i][f]]
        scale = -scale

      for q in xrange(0,GRAINS):
        xp -= sx*scale
        yp -= sy*scale
        ctx.rectangle(xp,yp,1./N,1./N)
        ctx.fill()
  return

def run(ctx,X,Y,SX,SY):
  t = []
  t.append(time())
  setDistances(X,Y)
  t.append(time())
  
  SX[:] = 0.
  SY[:] = 0.
  
  t.append(time())
  for i in xrange(0,NUM):
    for j in xrange(i+1,NUM):
      if len(F[i]) < 1 or F[j] < 1:
        continue
      dist = R[i][j]
      a    = A[j][i]

      f = False
      for q in xrange(0,len(F[i])):
        if j == F[i][q]:
          f = True
          break

      if dist > NEARL and f:
        SX[i] += cos(a)
        SY[i] += sin(a)
        SX[j] -= cos(a)
        SY[j] -= sin(a)
      elif dist < FARL:
        pass
        force = FARL - dist
        aPI = a+PI
        SX[i] += force*cos(aPI)
        SY[i] += force*sin(aPI)
        SX[j] -= force*cos(aPI)
        SY[j] -= force*sin(aPI)

  t.append(time())

  X  += SX*STP
  Y  += SY*STP

  t.append(time())
  makeFriends(int(random()*NUM))
  t.append(time())
  #drawConnections(ctx,X,Y)
  #showP(ctx,X,Y)
  t.append(time())
  
  #for ti in xrange(0,len(t)-1):
    #print str(t[ti+1] - t[ti]),
  #print 

def main():
  X       = np.zeros((NUM,1))
  Y       = np.zeros((NUM,1))
  SX      = np.zeros((NUM,1))
  SY      = np.zeros((NUM,1))
  sur,ctx = ctxInit()
  pInit(X,Y)

  ctx.set_source_rgba(0,0,0,0.8)
 
  plt.ion()
  plt.figure()
  for i in xrange(0,steps):
    run(ctx,X,Y,SX,SY)

    plt.clf()
    plt.plot(X,Y,'ro')
    for k,ff in enumerate(F):
      for f in ff:
        plt.plot([X[k],X[f]],[Y[k],Y[f]],'k-')

    plt.axis([0,1,0,1])
    ax = plt.gca()
    ax.set_autoscale_on(False)
    plt.draw()

  #sur.write_to_png('./'+OUT+'.png')
  return

if __name__ == '__main__' : main()

