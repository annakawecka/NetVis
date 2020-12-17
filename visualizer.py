import matplotlib.pyplot as plt
import matplotlib

from multiplex_graph import MultiplexGraph

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler

if __name__ == '__main__':
    window = tk.Tk()
    window.state('zoomed')

    fig = plt.figure(figsize=(11, 4))

    canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    ax = fig.add_subplot(111, projection='3d') # has to be done after canvas.draw(), otherwise it's not 3d
    ax.set_axis_off()

    node_labels = [str(nn+1) for nn in range(30)]
    data = MultiplexGraph(ax = ax, path=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_multiplex.edges", n_layers=2, directed=True, node_labels=node_labels, path_to_node_labels=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_nodes.txt")
    #data.draw_node_labels(data.node_labels, data.node_labels_text, horizontalalignment='center', verticalalignment='center', zorder=50) # draw node_labels_text <- and it actually works!!
    #mng = plt.get_current_fig_manager()
    #mng.window.showMaximized()
    #plt.show()

    window.mainloop()