import numpy as np
import matplotlib.pyplot as plt
from ripser import ripser
from persim import plot_diagrams

max_lim = 10
border = .2
dx = dy = .5 # the distance containing the dots to be removed by right click.
fig = plt.figure(figsize=(11,5))
plt.suptitle(f'Left click to put a dot \n Right click to remove dots within certain range: {dx} units \n Middle click to clear', fontsize=10)
ax1 = fig.add_subplot(121, xlim=(-border,max_lim+border), ylim=(-border,max_lim+border))
ax2 = fig.add_subplot(122, xlim=(-border,max_lim+border), ylim=(-border,max_lim+border))
ax2.plot([0,max_lim],[0,max_lim],'k--')
ax2.set_xlabel('Birth')
ax2.set_ylabel('Death')
ax1.grid()
ax2.grid()

X = [] ; Y = [] # coordinate
plot_pd=1
def onclick(event):
    global X,Y,plot_pd,ax1,ax2
    xx = event.xdata
    yy = event.ydata
    if event.button==1: 
        X=np.append(X,xx)
        Y=np.append(Y,yy)
        xy = np.vstack((X,Y)).T
        dgms = ripser(xy)['dgms']
        plot_pd=1
    elif event.button==3:
        if plot_pd==1 and len(X)>1:
            XX=X.copy()
            YY=Y.copy()
            XX=np.delete(X,np.where((X<xx+dx)&(X>xx-dx)&(Y<yy+dy)&(Y>yy-dy))[0]) # to remove the dots by right click.
            YY=np.delete(Y,np.where((X<xx+dx)&(X>xx-dx)&(Y<yy+dy)&(Y>yy-dy))[0]) # to remove the dots by right click.
            X=XX
            Y=YY
            xy = np.vstack((X,Y)).T
            dgms = ripser(xy)['dgms']
        else: 
            X=[]
            Y=[]
            plot_pd = 0
            ax1.plot(X,Y,'go')
    elif event.button==2: 
        X=[]
        Y=[]
        plot_pd = 0 ; ax1.plot(X,Y,'go')
    if plot_pd==1:
        ax1.plot(X,Y,'go')
        plot_diagrams(dgms, ax=ax2, xy_range=[-border,max_lim+border,-border,max_lim+border])

    fig.canvas.draw()
    ax1.remove()
    ax2.remove()
    ax1 = fig.add_subplot(121, xlim=(-border,max_lim+border), ylim=(-border,max_lim+border))
    ax2 = fig.add_subplot(122, xlim=(-border,max_lim+border), ylim=(-border,max_lim+border))
    ax1.grid()
    ax2.grid()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
