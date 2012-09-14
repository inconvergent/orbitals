#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import path
path.append('./') # kinda bad

from sim import *

N      = 2000   # size of png image
BACK   = 1.     # background color 
OUT    = 'img'  # resulting image name

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

def paintIt(ctx,POINTS,colors,opa=0.2):
  n = len(POINTS)/3
  print 'elements:\t{:d}'.format(n)
  ncolors = len(colors)
  for k in xrange(0,n):
    k3 = k*3
    ij = POINTS[k3]
    rgb = colors[ij % ncolors]
    ctx.set_source_rgba(rgb[0],rgb[1],rgb[2],opa)
    ctx.rectangle(POINTS[k3+1],POINTS[k3+2],1./N,1./N)
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

def countGrid(G,P):
  n = len(P)/3
  for k in xrange(0,n):
    k3 = k*3
    x = int(N*P[k3+1])
    y = int(N*P[k3+2])
    G[x,y] += 1
  return

def paintGrid(ctx,G):
  scale = max(G.flatten())
  print scale
  G = G/float(scale)
  for i in xrange(0,N):
    ii = float(i)/N
    for j in xrange(0,N):
      ig = G[i,j]
      if ig: 
        rgb = 1.-ig
        ctx.set_source_rgb(rgb,rgb,rgb)
        ctx.rectangle(ii,float(j)/N,1./N,1./N)
        ctx.fill()

  return

def main():
  
  GRID = np.zeros((N,N))
  POINTS = []
  for i in xrange(0,5):
    nameroot = 'dots{:04d}'.format(i)
    name     = '{:s}.pkl'.format(nameroot)
    print 'reading {:s} ... '.format(name)
    f = open(name,'rb')
    POINTS = pkl.load(f)
    f.close()
    print '\tdone'
    print 'counting ... '
    countGrid(GRID,POINTS)
    POINTS = []
    print '\tdone'
  
  print 'drawing ... '
  sur,ctx = ctxInit()
  paintGrid(ctx,GRID)
  sur.write_to_png('./img.01.{:s}.png'.format(nameroot))

if __name__ == '__main__': main()

  #for i in xrange(0,5):
    #POINTS = []
    #nameroot = 'dots{:04d}'.format(i)
    #name = '{:s}.pkl'.format(nameroot)
    #print 'reading {:s} ... '.format(name)
    #f = open(name,'rb')
    #POINTS = pkl.load(f)
    #f.close()
    #print '\tdone'
    #print 'painting ... '
    #paintIt(ctx,POINTS,colors,0.01)
    #print '\tdone'
    #sur.write_to_png('./img.2.{:s}.png'.format(nameroot))

