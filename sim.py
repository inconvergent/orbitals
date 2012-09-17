#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import os,sys,cairo,Image
from math import log, sin, cos, pi, atan2, sqrt
from random import random
from operator import itemgetter
from time import time
import numpy as np
from matplotlib import pylab as plt
import pickle as pkl
from scipy.sparse import lil_matrix

PI     = pi
PII    = PI*2.

NUM    = 300      # nodes
MAXFS  = 30       # max friendships pr node

RAD    = 0.25     # radius of starting circle

STP    = 0.0001   # scale motion in each iteration by this
steps  = 8000     # iterations
interval = 500

def print_timing(func):
  def wrapper(*arg):
    t1=time()
    res=func(*arg)
    t2=time()
    print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
    return res
  return wrapper

def pInit(X,Y):
  for i in xrange(0,NUM):
    the = random()*PII
    x = RAD * sin(the)
    y = RAD * cos(the)
    X[i] = 0.5+x
    Y[i] = 0.5+y

  return

#@print_timing
def setDistances(X,Y,R,A):
  for i in xrange(0,NUM):
    dx = X[i] - X
    dy = Y[i] - Y
    a  = np.arctan2(dy,dx)
    d  = np.sqrt(dx*dx+dy*dy)
    R[i] = d
    A[i] = a

  return

#@print_timing
def makeFriends(i,R,F):
  if (F[i,:].sum()) > MAXFS:
    return

  r = []
  for j in xrange(0,NUM):
    if i != j and F[j,:].sum() < MAXFS\
      and not F[j,i]:
        r.append([R[i][j],j])
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

#@print_timing
def run(X,Y,SX,SY,R,A,F,NEARL,FARL):
  setDistances(X,Y,R,A)
  
  SX[:] = 0.
  SY[:] = 0.
  
  for i in xrange(0,NUM):
    xF        = np.logical_not(F[i,:].toarray()).flatten()
    d         = R[i]
    a         = A[i]
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

def plotIt(X,Y,F):
  #plt.ion() ; plt.figure() # need to run this once on first run.
  plt.clf()
  plt.plot(X,Y,'ro')
  for k in xrange(0,NUM):
    for fi in xrange(0,NUM):
      if F[k,fi] and fi > k:
        plt.plot([X[k],X[fi]],[Y[k],Y[fi]],'k-')

  plt.axis([0,1,0,1])
  ax = plt.gca()
  ax.set_autoscale_on(False)
  plt.draw()

  return


def main():

  farmult =  0.05
  nearmult = 0.02
  g = 3
  h = 3
  FARL  = float(farmult) * float(g)
  NEARL = float(nearmult) * float(h)
  X  = np.zeros(NUM)
  Y  = np.zeros(NUM)
  SX = np.zeros(NUM)
  SY = np.zeros(NUM)
  R  = [np.zeros(NUM,dtype=np.bool) for i in xrange(0,NUM)]
  A  = [np.zeros(NUM,dtype=np.bool) for i in xrange(0,NUM)]
  F  = lil_matrix((NUM,NUM),dtype=np.byte).tocsr()

  pInit(X,Y)
  
  nc = 0

  STEP = [0]*interval
  ii = 0
  #plt.ion() ; plt.figure() # need to run this once on first run.
  t0 = time()

  for i in xrange(0,steps):
    if not i%10:
      print time()-t0
      t0 = time()
      #plotIt(X,Y,F)
      print i
    run(X,Y,SX,SY,R,A,F,NEARL,FARL)
    f = F.copy() 
    x = X.copy() 
    y = Y.copy() 
    STEP[ii] = [x,y,f]
    ii += 1

    if not (i+1) % interval:
      fname = 'dots{:04d}.pkl'\
        .format(nc)
      print 'writing to {:s} ... '\
        .format(fname)
      f = open(fname,'wb')
      pkl.dump(STEP,f)
      f.close()
      print 'done'
      nc += 1
      STEP = [0]*interval
      ii = 0

  return

if __name__ == '__main__' : main()

