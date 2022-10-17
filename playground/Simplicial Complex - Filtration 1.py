from matplotlib.patches import Circle
import numpy as np
from gudhi.representations import BettiCurve
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from ripser import ripser
from persim import plot_diagrams
import itertools
import warnings
warnings.filterwarnings("ignore")

max_parameter = 5
margin = max_parameter/15
dx = dy = .5 # the distance containing the dots to be removed by right click.
fig = plt.figure(figsize=(11,7)) #; plt.tight_layout(rect=(0,0,1,.5))
# plt.suptitle(f'Left click to put a dot \n Right click to remove dots within certain range: {dx} units \n Middle click to clear', fontsize=10)
ax1 = fig.add_subplot(231, xlim=(-margin,max_parameter*2+margin), ylim=(-margin,max_parameter*2+margin)) ; ax1.set_title('Point cloud') ; ax1.grid()
ax2 = fig.add_subplot(232, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax2.set_title('Persistence barcode') ; ax2.set_yticks([]) #ax2.set_xlabel('Parameter (radius)')  ; 
ax3 = fig.add_subplot(233, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax3.set_title('Persistence diagram') ; ax3.plot([0,max_parameter],[0,max_parameter],'k--') ; ax3.set_xlabel('Birth') ; ax3.set_ylabel('Death'); ax3.grid()
ax4 = fig.add_subplot(235, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax4.set_title('Betti curve') ; ax4.set_xlabel('Parameter (radius)') ; ax4.set_ylabel('Abundancy') ; ax4.grid()
parameter_slider_ax = fig.add_axes([0.05, 0.35, .02, .4]) ; parameter_slider = Slider(parameter_slider_ax, 'Parameter\n(radius)', valmin=0, valmax=max_parameter, valinit=0, orientation='vertical') ; parameter_slider.label.set_size(10) ; parameter_slider.label.set_color('black')


def distance(x0, x1, y0, y1):
    return np.sqrt((x0-x1)**2+(y0-y1)**2)
    
def simplex_finder(xs, ys, parameter):
    points = range(len(xs))
    distances = []
    triangles_x = [] ; triangles_y = []
    for i in range(len(xs)):
        distances.append([])
        for j in range(len(ys)):
            distances[-1].append(distance(xs[i],xs[j],ys[i],ys[j]))

    all_two_fold_combinations = tuple(itertools.combinations(points, 2))
    all_three_fold_combinations = tuple(itertools.combinations(points, 3))
    triangles_x = []
    triangles_y = []
    for i in range(len(all_three_fold_combinations)):
        three_points = tuple(itertools.combinations(all_three_fold_combinations[i], 2))
        condition = distances[three_points[0][0]][three_points[0][1]]<parameter*2 and distances[three_points[1][0]][three_points[1][1]]<parameter*2 and distances[three_points[2][0]][three_points[2][1]]<parameter*2
        if condition:
            triangles_x.append([]) ; triangles_y.append([])
            triangles_x[-1].extend([xs[all_three_fold_combinations[i][j]] for j in range(3)])
            triangles_y[-1].extend([ys[all_three_fold_combinations[i][j]] for j in range(3)])
    triangles_x = np.array(triangles_x) ; triangles_y = np.array(triangles_y)
    xf = triangles_x.flatten() ; yf = triangles_y.flatten()
    x_in_triangle = np.unique(triangles_x.flatten()) ; y_in_triangle = []
    for i in range(len(x_in_triangle)): y_in_triangle.append(yf[list(xf).index(x_in_triangle[i])])

    """ax1:"""
    for x,y in zip(xs, ys): ax1.add_patch(plt.Circle((x, y), parameter, alpha=.3, color='r'))
    for i,j in all_two_fold_combinations: #"""drawing 2-simplices"""
        if distance(xs[i],xs[j],ys[i],ys[j]) < parameter*2:
            ax1.plot([xs[i],xs[j]],[ys[i],ys[j]], 'c-')
    for i in range(len(triangles_x)): #"""drawing 3-simplices"""
        ax1.fill(triangles_x[i], triangles_y[i], alpha=.5, color='b')

X = [] ; Y = [] # coordinate
plot_pd=0
def onclick(event, blit=True):
        global X,Y,plot_pd,ax1,ax2,ax3,ax4,dgms
    # try:
        for i in range(20):
            xx = event.xdata ; yy = event.ydata ; boundary = event.x
            if event.button==1: 
                if i==0 and type(xx)!=type(None) and type(yy)!=type(None) and boundary>100: X=np.append(X,xx) ; Y=np.append(Y,yy)           
                xy = np.vstack((X,Y)).T ; plot_pd=1
            elif event.button==3:
                if plot_pd==1 and len(X)>=1:
                    XX=X.copy() ; YY=Y.copy()
                    try:
                        XX=np.delete(X,np.where((X<xx+dx)&(X>xx-dx)&(Y<yy+dy)&(Y>yy-dy))[0]) # to remove the dots by right click.
                        YY=np.delete(Y,np.where((X<xx+dx)&(X>xx-dx)&(Y<yy+dy)&(Y>yy-dy))[0]) # to remove the dots by right click.
                    except: pass
                    finally: X=XX ; Y=YY ; xy = np.vstack((X,Y)).T
                else: X=[] ; Y=[] ; plot_pd = 0
                continue
            elif event.button==2: X=[] ; Y=[] ; plot_pd = 0; continue

            try: dgms = ripser(xy, thresh=parameter_slider.val*2)['dgms'] ; dgms[0]/=2 ; dgms[1]/=2 ; dgms[0][:,1][dgms[0][:,1]>=parameter_slider.val]=parameter_slider.val ; dgms[1][:,1][dgms[1][:,1]>=parameter_slider.val]=parameter_slider.val 
            except: pass
            if plot_pd==1: plot_diagrams(dgms, ax=ax3, xy_range=[-margin,max_parameter+margin,-margin,max_parameter+margin])
            ax1.plot(X,Y,'co')
            simplex_finder(X, Y, parameter_slider.val) # drawing the simplices
            y_ticks_H0 = np.linspace(margin, max_parameter/2-margin, len(dgms[0][:,0]))
            y_ticks_H1 = np.linspace(max_parameter/2, max_parameter-margin, len(dgms[1][:,0]))
            ax2.hlines(y=y_ticks_H0, xmin=dgms[0][:,0], xmax=dgms[0][:,1], linestyle='-', colors='g', label=r'$H_0$')
            ax2.hlines(y=y_ticks_H1, xmin=dgms[1][:,0], xmax=dgms[1][:,1], linestyle='--', colors='r', label=r'$H_1$') ; ax2.set_yticks([]); ax2.set_title('Persistence barcode') ; ax2.legend()# ; ax2.set_xlabel('Parameter (radius)')
            res = int(parameter_slider.val / max_parameter * 50)
            
            try: bc0 = BettiCurve(resolution=res+1, sample_range=(0,parameter_slider.val))(dgms[0])[:-1] ; ax4.plot(np.linspace(0, parameter_slider.val, res), bc0, 'g-')
            except: pass
            try: bc1 = BettiCurve(resolution=res+1, sample_range=(0,parameter_slider.val))(dgms[1])[:-1] ; ax4.plot(np.linspace(0, parameter_slider.val, res), bc1, 'r--')
            except: pass
            fig.canvas.draw() ; fig.canvas.flush_events()
            ax1.remove() ; ax3.remove() ; ax2.remove() ; ax4.remove()
            ax1 = fig.add_subplot(231, xlim=(-margin,max_parameter*2+margin), ylim=(-margin,max_parameter*2+margin)) ; ax1.grid() ; ax1.set_title('Point cloud')
            ax2 = fig.add_subplot(232, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax2.set_title('Persistence barcode') ; ax2.set_yticks([]) #; ax2.set_xlabel('Parameter (radius)') 
            ax3 = fig.add_subplot(233, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax3.grid() ; ax3.set_title('Persistence diagram')#; ax3.plot([0,max_parameter],[0,max_parameter],'k--') ; ax3.set_xlabel('Birth') ; ax3.set_ylabel('Death')
            try: ax4 = fig.add_subplot(235, xlim=(-margin,max_parameter+margin), ylim=(-margin,np.max((bc0, bc1))+margin)) ; ax4.set_title('Betti curve') ; ax4.set_xlabel('Parameter (radius)') ; ax4.set_ylabel('Abundancy')
            except: ax4 = fig.add_subplot(235, xlim=(-margin,max_parameter+margin), ylim=(-margin,max_parameter+margin)) ; ax4.set_title('Betti curve') ; ax4.set_xlabel('Parameter (radius)') ; ax4.set_ylabel('Abundancy')
            ax4.grid()  
    # except: pass

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()