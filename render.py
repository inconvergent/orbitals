#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import path
path.append('./') # kinda bad

from sim import *

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
  ncolors = len(colors)
  for k in xrange(0,n):
    k3 = k*3
    ij = POINTS[k3]
    rgb = colors[ij % ncolors]
    ctx.set_source_rgba(rgb[0],rgb[1],rgb[2],opa)
    ctx.rectangle(POINTS[k3+1],POINTS[k3+2],1./N,1./N)
    ctx.fill()

  return

def main():
  #colors = getColors('colors.gif')

  f = open('dots.pkl','rb')
  POINTS = pkl.load(f)
  f.close()

  colors = [[0,0,0]]
  sur,ctx = ctxInit()

  paintIt(ctx,POINTS,colors,opa=0.2)
  sur.write_to_png('./'+OUT+'.png')

if __name__ == '__main__': main()

