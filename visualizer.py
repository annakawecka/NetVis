from multiplex_graph import MultiplexGraph

from gui import MainWindow

if __name__ == '__main__':
    window = MainWindow()

    # node_labels = [str(nn+1) for nn in range(30)]
    # data = MultiplexGraph(ax = window.ax, path=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_multiplex.edges", n_layers=2, directed=True, node_labels=node_labels, path_to_node_labels=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_nodes.txt")
    # #data.draw_node_labels(data.node_labels, data.node_labels_text, horizontalalignment='center', verticalalignment='center', zorder=50) # draw node_labels_text <- and it actually works!!

    window.mainloop()
    