#!/usr/bin/python
# -*- coding: utf-8 -*-

import cairo, Image
import numpy as np
from numpy import sin, cos, pi, arctan2, square,sqrt, logical_not,\
                  linspace, array, zeros
from numpy.random import random, randint, shuffle
from time import time

#np.random.seed(1)

PI = pi
TWOPI = pi*2.

SIZE = 1000 # size of png image
NUM = 200 # number of nodes
BACK = 1. # background color 
GRAINS = 5
STP = 0.0001 # scale motion in each iteration by this
MAXFS = 5 # max friendships pr node
ALPHA = 0.05 # opacity of drawn points
ONE = 1./SIZE

FILENAME = 'res'

RAD = 0.20 # radius of starting circle
FARL  = 0.13 # ignore "enemies" beyond this radius
NEARL = 0.02 # do not attempt to approach friends close than this

UPDATE_NUM = 1000

FRIENDSHIP_RATIO = 0.1 # probability of friendship dens
FRIENDSHIP_INITIATE_PROB = 0.1 # probability of friendship initation attempt

COLOR_PATH = 'color/dark_cyan_white_black.gif'

class Render(object):

  def __init__(self):

    self.__init_cairo()
    #self.__get_colors(COLOR_PATH)
    self.colors = [(0,0,0)]
    self.n_colors = 1

  def __init_cairo(self):

    sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,SIZE,SIZE)
    ctx = cairo.Context(sur)
    ctx.scale(SIZE,SIZE)
    ctx.set_source_rgb(BACK,BACK,BACK)
    ctx.rectangle(0,0,1,1)
    ctx.fill()

    self.sur = sur
    self.ctx = ctx

  def __get_colors(self,f):
    scale = 1./255.
    im = Image.open(f)
    w,h = im.size
    rgbim = im.convert('RGB')
    res = []
    for i in xrange(0,w):
      for j in xrange(0,h):
        r,g,b = rgbim.getpixel((i,j))
        res.append((r*scale,g*scale,b*scale))

    shuffle(res)
    self.colors = res
    self.n_colors = len(res)

  def step_wrap(self,*args):

    res, added_new = self.step()

    if not self.itt%UPDATE_NUM:
      self.expose()

      ## write frames to file:
      #fn = 'image{:05d}.png'.format(self.num_img)
      #self.sur.write_to_png(fn)
      #self.num_img+=1
      #print fn

    return res


  def connections(self,X,Y,F,A,R):

    indsx,indsy = F.nonzero()
    mask = indsx >= indsy 
    for i,j in zip(indsx[mask],indsy[mask]):
      a = A[i,j]
      d = R[i,j]
      scales = random(GRAINS)*d
      xp = X[i] - scales*cos(a)
      yp = Y[i] - scales*sin(a)
     
      # colors. wooo!
      r,g,b = self.colors[ (i*NUM+j) % self.n_colors ]
      self.ctx.set_source_rgba(r,g,b,ALPHA)

      for x,y in zip(xp,yp):
        self.ctx.rectangle(x,y,ONE,ONE)
        self.ctx.fill()

def set_distances(X,Y,A,R):

  for i in xrange(NUM):

    dx = X[i] - X
    dy = Y[i] - Y
    R[i,:] = square(dx)+square(dy)
    A[i,:] = arctan2(dy,dx)

  sqrt(R,R)

def make_friends(i,F,R):

  cand_num = F.sum(axis=1)
  
  if cand_num[i]>=MAXFS:
    return

  cand_mask = cand_num<MAXFS
  cand_mask[i] = False
  cand_ind = cand_mask.nonzero()[0]

  cand_dist = R[i,cand_ind].flatten()
  cand_sorted_dist = cand_dist.argsort()
  cand_ind = cand_ind[cand_sorted_dist]

  cand_n = len(cand_ind)

  if cand_n<1:
    return

  for k in xrange(cand_n):

    if random()<FRIENDSHIP_RATIO:

      j = cand_ind[k]
      F[[i,j],[j,i]] = True
      return

def main():

  render = Render()

  X = zeros(NUM,'float')
  Y = zeros(NUM,'float')
  SX = zeros(NUM,'float')
  SY = zeros(NUM,'float')
  R = zeros((NUM,NUM),'float')
  A = zeros((NUM,NUM),'float')
  F = zeros((NUM,NUM),'byte')

  for i in xrange(NUM):
    the = random()*TWOPI
    x = RAD * sin(the)
    y = RAD * cos(the)
    X[i] = 0.5+x
    Y[i] = 0.5+y

  t_cum = 0.
  for itt in xrange(100000):

    set_distances(X,Y,A,R)
    
    SX[:] = 0.
    SY[:] = 0.

    t = time()
    
    for i in xrange(NUM):
      xF = logical_not(F[i,:])
      d = R[i,:]
      a = A[i,:]
      near = d > NEARL
      near[xF] = False
      far = d < FARL
      far[near] = False
      near[i] = False
      far[i] = False
      speed = FARL - d[far]

      SX[near] += cos(a[near])
      SY[near] += sin(a[near])
      SX[far] -= speed*cos(a[far])
      SY[far] -= speed*sin(a[far])

    X += SX*STP
    Y += SY*STP

    if random()<FRIENDSHIP_INITIATE_PROB:

      k = randint(NUM)
      make_friends(k,F,R)

    render.connections(X,Y,F,A,R)

    t_cum += time()-t

    if not (itt+1)%UPDATE_NUM:

      fn = '{:s}_{:05d}.png'.format(FILENAME,itt+1)
      print fn, t_cum
      render.sur.write_to_png(fn)

      t_cum = 0.


if __name__ == '__main__' :
  main()

