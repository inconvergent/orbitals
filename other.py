
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

def gauss_kern(size):
    size = int(size)        
    x, y = np.mgrid[-size:size+1, -size:size+1]
    g = np.exp(-(x**2/float(size)+y**2/float(size)))

    return g / g.sum()

def showP(ctx,X,Y):
  ctx.set_source_rgba(1,0,0,0.5)
  for i in xrange(0,NUM):
    ctx.move_to(X[i],Y[i])
    ctx.arc(X[i],Y[i],2./N,0,PII)
  ctx.close_path()
  ctx.fill()

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
