import numpy as np
def movingAverage(x,L,dx=1,wo=0):
    N=max(x.shape)		#Number of elements
    nw=int(np.ceil(L/float(dx)))#Window size number
    xs=x*0			#Inicialization moving Average
    t=0 			#Counter		
    lw=0			#left window
    
        
    if wo==0:			#0 means centered moving average	
        rw=int((nw-1)/2.)	#1 means forward moving average
    else:
        rw=nw-1
    if wo==-1:
        x=x[::-1]
    while (t<(N-rw+1) and t<N):
        xs[t]=np.mean(x[t-lw:t+rw])##
        #print xs
        if (lw<(nw-1)/2.):
            lw=lw+1-abs(wo)		#If wo==0 wl remains nule.
        if (t+rw==N):
            rw=rw-1
        t=t+1
    if wo==-1:
        xs=xs[::-1]
    return xs
