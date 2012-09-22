#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import path
path.append('./') # kinda bad

from scipy import signal
from sim import *

N      = 10000   # size of png image
BACK   = 1.     # background color 
OUT    = 'large.img'  # resulting image name
GRAINS = 1000

def ctxInit():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx

def showP(ctx,X,Y):
  ctx.set_source_rgba(1,0,0,0.5)
  for i in xrange(0,NUM):
    ctx.move_to(X[i],Y[i])
    ctx.arc(X[i],Y[i],2./N,0,PII)
  ctx.close_path()
  ctx.fill()

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

def getConnectionPoints(X,Y,R,A,F,GRID):

  for i in xrange(0,NUM):
    for j in xrange(i+1,NUM):
      if not F[i,j]:
        continue

      a = A[i][j]
      sx = cos(a)
      sy = sin(a)
      
      d = R[i][j]
      scale = random()*d/GRAINS
      if random()<0.5:
        q = i
      else:
        q = j
        scale *= -1

      xp = X[q]
      yp = Y[q]
      
      ij = NUM*i + j
      for q in xrange(0,GRAINS):
        xp -= sx*scale
        yp -= sy*scale
        GRID[int(xp*N),int(yp*N)] += 1

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
  r = [np.zeros(NUM,dtype=np.bool) for i in xrange(0,NUM)]
  a = [np.zeros(NUM,dtype=np.bool) for i in xrange(0,NUM)]
  
  for i in xrange(0,stps):
    x,y,f = STEP[i]
    setDistances(x,y,r,a)
    getConnectionPoints(x,y,r,a,f,GRID)

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

#def countGrid(G,P):
  #n = len(P)/3
  #for k in xrange(0,n):
    #k3 = k*3
    #x = int(N*P[k3+1])
    #y = int(N*P[k3+2])
    #if x < N and y < N:
      #G[x,y] += 1
  #return

#def gauss_kern(size):
    #size = int(size)        
    #x, y = np.mgrid[-size:size+1, -size:size+1]
    #g = np.exp(-(x**2/float(size)+y**2/float(size)))

    #return g / g.sum()

#def paintIt(ctx,POINTS,colors,opa=0.2):
  #n = len(POINTS)/3
  #print 'elements:\t{:d}'.format(n)
  #ncolors = len(colors)
  #for k in xrange(0,n):
    #k3 = k*3
    #ij = POINTS[k3]
    #rgb = colors[ij % ncolors]
    #ctx.set_source_rgba(rgb[0],rgb[1],rgb[2],opa)
    #ctx.rectangle(POINTS[k3+1],POINTS[k3+2],1./N,1./N)
    #ctx.fill()

  #return


