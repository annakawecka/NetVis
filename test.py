import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

G = nx.Graph()
G.add_node(1)
G.add_nodes_from([2, 3])
plt.subplot(121)
nx.draw(G)
plt.subplot(122)
nx.draw(G, pos=nx.circular_layout(G), node_color='r', edge_color='b')

plt.show()