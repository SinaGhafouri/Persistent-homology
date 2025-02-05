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
margin = max_parameter / 15
dx = dy = 0.5  # The distance containing the dots to be removed on right click.

# Create figure and subplots
fig = plt.figure(figsize=(11, 7))
ax1 = fig.add_subplot(231)  # Point cloud
ax2 = fig.add_subplot(232)  # Persistence barcode
ax3 = fig.add_subplot(233)  # Persistence diagram
ax4 = fig.add_subplot(235)  # Betti curve

# Setup slider for parameter (radius)
parameter_slider_ax = fig.add_axes([0.05, 0.35, 0.02, 0.4])
parameter_slider = Slider(parameter_slider_ax, 'Parameter\n(radius)',
                          valmin=0, valmax=max_parameter, valinit=0,
                          orientation='vertical')
parameter_slider.label.set_size(10)
parameter_slider.label.set_color('black')


def configure_axes():
    """
    Initialize or reconfigure the four axes.
    """
    ax1.set_xlim(-margin, max_parameter * 2 + margin)
    ax1.set_ylim(-margin, max_parameter * 2 + margin)
    ax1.set_title('Point cloud')
    ax1.grid(True)

    ax2.set_xlim(-margin, max_parameter + margin)
    ax2.set_ylim(-margin, max_parameter + margin)
    ax2.set_title('Persistence barcode')
    ax2.set_yticks([])
    ax2.grid(True)

    ax3.set_xlim(-margin, max_parameter + margin)
    ax3.set_ylim(-margin, max_parameter + margin)
    ax3.set_title('Persistence diagram')
    ax3.set_xlabel('Birth')
    ax3.set_ylabel('Death')
    ax3.plot([0, max_parameter], [0, max_parameter], 'k--')
    ax3.grid(True)

    ax4.set_xlim(-margin, max_parameter + margin)
    ax4.set_title('Betti curve')
    ax4.set_xlabel('Parameter (radius)')
    ax4.set_ylabel('Abundancy')
    ax4.grid(True)


configure_axes()

# Global point arrays
X = np.empty(0)
Y = np.empty(0)


def simplex_finder(xs, ys, parameter):
    """
    Draw circles, edges and triangles (2-simplices) from the point cloud.
    Instead of check-each-pair with loops, we compute the full distance matrix.
    """
    if len(xs) == 0:
        return

    points = np.column_stack((xs, ys))
    # Compute the pairwise distance matrix at once
    dist_matrix = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=2)

    # Draw circles around each point
    for x, y in zip(xs, ys):
        ax1.add_patch(Circle((x, y), parameter, alpha=0.3, color='r'))

    # Draw edges for pairs with distance < parameter*2 using upper-triangle indices
    n = len(xs)
    i_upper, j_upper = np.triu_indices(n, k=1)
    valid_edges = dist_matrix[i_upper, j_upper] < parameter * 2
    for i, j in zip(i_upper[valid_edges], j_upper[valid_edges]):
        ax1.plot([xs[i], xs[j]], [ys[i], ys[j]], 'c-')

    # Draw filled triangles for triples with all pairwise distances < parameter*2.
    # (For a small number of points, looping over combinations is acceptable.)
    for i, j, k in itertools.combinations(range(n), 3):
        if (dist_matrix[i, j] < parameter * 2 and
            dist_matrix[i, k] < parameter * 2 and
            dist_matrix[j, k] < parameter * 2):
            ax1.fill([xs[i], xs[j], xs[k]],
                     [ys[i], ys[j], ys[k]], alpha=0.5, color='b')


def update_plot():
    """
    Clear and update all axes with the current state of the plotted points and filter parameter.
    Performs the persistent homology, draws the persistence diagram, barcode and Betti curves.
    """
    # Clear the axes and redraw their configuration
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()
    configure_axes()

    if len(X) == 0:
        fig.canvas.draw_idle()
        return

    # Assemble the (n,2) array of point coordinates
    xy = np.column_stack((X, Y))

    # Compute persistent homology using ripser. Note that we scale
    # the threshold (parameter_slider.val * 2) and then adjust the diagrams.
    try:
        dgms = ripser(xy, thresh=parameter_slider.val * 2)['dgms']
        dgms[0] /= 2
        dgms[1] /= 2
        dgms[0][:, 1][dgms[0][:, 1] >= parameter_slider.val] = parameter_slider.val
        dgms[1][:, 1][dgms[1][:, 1] >= parameter_slider.val] = parameter_slider.val
    except Exception as e:
        print("Ripser error:", e)
        dgms = None

    # Draw persistence diagram in ax3
    if dgms is not None:
        plot_diagrams(dgms, ax=ax3, xy_range=[-margin, max_parameter + margin,
                                               -margin, max_parameter + margin])

    # Draw persistence barcode in ax2
    if dgms is not None:
        if dgms[0].size > 0:
            y_ticks_H0 = np.linspace(margin, max_parameter / 2 - margin, len(dgms[0][:, 0]))
            ax2.hlines(y=y_ticks_H0, xmin=dgms[0][:, 0], xmax=dgms[0][:, 1],
                       linestyle='-', colors='g', label=r'$H_0$')
        if dgms[1].size > 0:
            y_ticks_H1 = np.linspace(max_parameter / 2, max_parameter - margin, len(dgms[1][:, 0]))
            ax2.hlines(y=y_ticks_H1, xmin=dgms[1][:, 0], xmax=dgms[1][:, 1],
                       linestyle='--', colors='r', label=r'$H_1$')
        ax2.legend()

    # Compute and draw Betti curves in ax4
    if dgms is not None:
        try:
            res = max(1, int(parameter_slider.val / max_parameter * 50))
            # Compute the Betti curves. (The BettiCurve returns one extra value, so we slice off the last one.)
            bc0 = BettiCurve(resolution=res + 1, sample_range=(0, parameter_slider.val))(dgms[0])[:-1]
            bc1 = BettiCurve(resolution=res + 1, sample_range=(0, parameter_slider.val))(dgms[1])[:-1]
            x_vals = np.linspace(0, parameter_slider.val, res)
            ax4.plot(x_vals, bc0, 'g-')
            ax4.plot(x_vals, bc1, 'r--')
            ax4.set_ylim(-margin, max(np.max(bc0), np.max(bc1)) + margin)
        except Exception as e:
            print("BettiCurve error:", e)

    # Draw the point cloud and the simplices on ax1
    ax1.plot(X, Y, 'co', markersize=4)
    simplex_finder(X, Y, parameter_slider.val)

    fig.canvas.draw_idle()


def onclick(event):
    """
    Mouse click event handler:
      - Left click (button==1): add a point.
      - Right click (button==3): remove points near the click.
      - Middle click (button==2): clear all points.
    """
    global X, Y

    # Process only clicks on our main axes (ignore slider clicks)
    if event.inaxes not in [ax1, ax2, ax3, ax4]:
        return

    if event.button == 1:  # Add a point on left click
        if event.xdata is not None and event.ydata is not None and event.x > 100:
            X = np.append(X, event.xdata)
            Y = np.append(Y, event.ydata)
    elif event.button == 3:  # Remove points near click on right click
        if len(X) > 0:
            mask = ~((X < event.xdata + dx) & (X > event.xdata - dx) &
                     (Y < event.ydata + dy) & (Y > event.ydata - dy))
            X = X[mask]
            Y = Y[mask]
    elif event.button == 2:  # Clear all points on middle click
        X = np.empty(0)
        Y = np.empty(0)

    update_plot()


# Connect the mouse click event to our onclick function
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Also update the plot whenever the slider value changes.
parameter_slider.on_changed(lambda val: update_plot())

plt.show()
