#!/usr/bin/python
# -*- coding: utf-8 -*-

def main():
  import cairo,Image
  from operator import itemgetter
  from time import time
  import numpy as np
  from scipy.sparse import csr_matrix,lil_matrix,csc_matrix

  sin         = np.sin
  cos         = np.cos
  pi          = np.pi
  sqrt        = np.sqrt
  arctan2     = np.arctan2
  logical_not = np.logical_not
  float       = np.float
  int         = np.int
  random      = np.random.random
  zeros       = np.zeros
  byte        = np.byte
  
  PI     = pi
  PII    = PI*2.

  N      = 4000               # size of png image
  NUM    = 400                # number of nodes
  BACK   = 1.                 # background color 
  OUT    = 'orbitals.color.4' # resulting image name
  RAD    = 0.265              # radius of starting circle
  GRAINS = 100
  STP    = 0.0001             # scale motion in each iteration by this
  steps  = 500000             # iterations
  MAXFS  = 150                # max friendships pr node
  ALPHA  = 0.05


  def pInit(X,Y):
    for i in xrange(NUM):
      the = random()*PII
      x = RAD * sin(the)
      y = RAD * cos(the)
      X[i] = 0.5+x
      Y[i] = 0.5+y
    return


  def ctx_init():
    sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
    ctx = cairo.Context(sur)
    ctx.scale(N,N)
    ctx.set_source_rgb(BACK,BACK,BACK)
    ctx.rectangle(0,0,1,1)
    ctx.fill()
    return sur,ctx


  def set_distances(X,Y,R,A):
    for i in xrange(NUM):
      dx = X[i] - X
      dy = Y[i] - Y
      R[i,:] = dx*dx+dy*dy
      A[i,:] = arctan2(dy,dx)
    sqrt(R,R)
    return


  def get_colors(f):
    scale = 1./255.
    im = Image.open(f)
    w,h = im.size
    rgbim = im.convert('RGB')
    res = []
    for i in xrange(0,w):
      for j in xrange(0,h):
        r,g,b = rgbim.getpixel((i,j))
        res.append((r*scale,g*scale,b*scale))

    return res


  def makeFriends(i,R,F):
    
    if F[i,:].nnz > MAXFS:
      return

    r = []
    for j in xrange(NUM):
      if i != j and F[j,:].nnz < MAXFS\
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

  def render_connection_points(X,Y,R,A,F,ctx,colors,alpha=ALPHA):
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

      scales = random(GRAINS)*d
      xp = X[i] - scales*cos(a)
      yp = Y[i] - scales*sin(a)
      
      c = colors[ (i*NUM+j) % lc ]
      ctx.set_source_rgba(c[0],c[1],c[2],alpha)

      vstroke(xp,yp)
    return

  def run(X,Y,SX,SY,R,A,F,NEARL,FARL):

    t = time()
    set_distances(X,Y,R,A)
    t = time()
    
    SX[:] = 0.; SY[:] = 0.
    
    for i in xrange(NUM):
      xF        = logical_not(F[i,:].toarray()).flatten()
      d         = R[i,:]
      a         = A[i,:]
      near      = d > NEARL
      near[xF]  = False
      far       = d < FARL
      far[near] = False
      near[i]   = False
      far[i]    = False
      speed     = FARL - d[far]
      
      SX[near] += cos(a[near])
      SY[near] += sin(a[near])
      SX[far]  -= speed*cos(a[far])
      SY[far]  -= speed*sin(a[far])
    t = time()

    X += SX*STP
    Y += SY*STP
    if random()<0.3:
      makeFriends(int(random()*NUM),R,F)
    t = time()

    return

  sur,ctx = ctx_init()

  FARL  = 0.17
  NEARL = 0.02
  X  = zeros(NUM,            dtype=float)
  Y  = zeros(NUM,            dtype=float)
  SX = zeros(NUM,            dtype=float)
  SY = zeros(NUM,            dtype=float)
  R  = zeros((NUM,NUM),      dtype=float)
  A  = zeros((NUM,NUM),      dtype=float)
  F  = csr_matrix((NUM,NUM), dtype=byte)

  #colors = [(0.,0.,0.)]
  colors = get_colors('../city/color/color_purple.gif')

  pInit(X,Y)
  
  for i in xrange(steps):
    t = time()
    run(X,Y,SX,SY,R,A,F,NEARL,FARL)
    render_connection_points(X,Y,R,A,F,ctx,colors)
    if not (i+1)%1000:
      sur.write_to_png('{:s}.{:d}.png'.format(OUT,i+1))
    print i,time()-t

  return

if __name__ == '__main__' : main()

