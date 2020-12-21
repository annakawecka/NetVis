import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D, proj3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from fancy_arrow import myArrow3D

class MultiplexGraph():

    def __init__(self, path: str, n_layers: int, layout = nx.spring_layout, directed = False, ax = None, node_labels = None, path_to_node_labels = None, path_to_layer_labels = None, title = None, weighted = False):
        self.n_layers = n_layers
        self.layout = layout
        self.directed = directed
        self.weighted = weighted
        self.title = title
        self.node_labels = node_labels
        self.path_to_node_labels = path_to_node_labels
        self.path_to_layer_labels = path_to_layer_labels

        if directed:
            self.graphs = [nx.DiGraph() for ii in range(n_layers)]
        else:
            self.graphs = [nx.Graph() for ii in range(n_layers)]

        if ax:
            self.ax = ax
        else:
            fig = plt.figure()
            self.ax = fig.add_subplot(111, projection='3d')
        
        self.ax.set_axis_off()

        self.read_data(path)
        self.get_nodes()
        self.get_node_positions()
        self.get_edges_between_layers()
        self.get_edges_within_layers()
        self.get_node_label_text(path_to_node_labels)
        self.get_layer_labels(path_to_layer_labels)
        self.draw()
    
    def read_data(self, path):
        with open(path) as file:
            lines = file.read().splitlines()

        for line in lines:
            layerID, node1ID, node2ID, weight = line.split(sep=' ')
            self.graphs[int(layerID)-1].add_edge(node1ID, node2ID, weight=weight)

    def get_nodes(self):
        """Construct an internal representation of nodes with the format (node ID, layer)."""
        self.nodes = []
        for z, g in enumerate(self.graphs):
            self.nodes.extend([(node, z) for node in g.nodes()])

    def get_node_positions(self, *args, **kwargs):
        """Get the node positions in the layered layout."""

        composition = self.graphs[0]
        for h in self.graphs[1:]:
            composition = nx.compose(composition, h)

        pos = self.layout(composition, *args, **kwargs)

        self.node_positions = dict()
        for z, g in enumerate(self.graphs): # z - level, g - graph
            self.node_positions.update({(node, z) : (*pos[node], z) for node in g.nodes()})

    def draw_nodes(self, nodes, *args, **kwargs):
        x, y, z = zip(*[self.node_positions[node] for node in nodes])
        self.ax.scatter(x, y, z, *args, **kwargs)

    def get_extent(self, pad=0.1):
        xyz = np.array(list(self.node_positions.values()))
        xmin, ymin, _ = np.min(xyz, axis=0)
        xmax, ymax, _ = np.max(xyz, axis=0)
        dx = xmax - xmin
        dy = ymax - ymin
        return (xmin - pad * dx, xmax + pad * dx), \
            (ymin - pad * dy, ymax + pad * dy)

    def get_edges_within_layers(self):
        """Remap edges in the individual layers to the internal representations of the node IDs."""
        self.edges_within_layers = []
        for z, g in enumerate(self.graphs):
            graph = self.graphs[z]
            self.edges_within_layers.extend([((source, z), (target, z), (graph[source][target])) for source, target in g.edges()])

    def get_edges_between_layers(self):
        """Determine edges between layers. Nodes in subsequent layers are
        thought to be connected if they have the same ID."""
        self.edges_between_layers = []
        for z1, g in enumerate(self.graphs[:]):
            for z2, h in enumerate(self.graphs[:]):
                if z1 == z2:
                    pass
                else:
                    shared_nodes = set(g.nodes()) & set(h.nodes())
                    self.edges_between_layers.extend([((node, z1), (node, z2)) for node in shared_nodes])

    def get_layer_labels(self, path):
        if path is not None:
            self.layer_labels = []
            with open(path) as file:
                lines = file.read().splitlines()
            
            for line in lines[1:]:
                values = line.split(sep=' ')
                self.layer_labels.append(values[1])       

    def draw_plane(self, z, *args, **kwargs):
        (xmin, xmax), (ymin, ymax) = self.get_extent(pad=0.1)
        u = np.linspace(xmin, xmax, 10)
        v = np.linspace(ymin, ymax, 10)
        U, V = np.meshgrid(u ,v)
        W = z * np.ones_like(U)
        self.ax.plot_surface(U, V, W, *args, **kwargs)

    def draw_edges_between_layers(self, edges, *args, **kwargs):
        segments = [(self.node_positions[source], self.node_positions[target]) for source, target in edges]
        line_collection = Line3DCollection(segments, *args, **kwargs)
        self.ax.add_collection3d(line_collection)

    def draw_edges_within_layers(self, edges, *args, **kwargs):
        if self.directed:
            for source, target, weight in edges:
                x1, y1, z1 = self.node_positions[source]
                x2, y2, z2 = self.node_positions[target]
                width = float(weight["weight"])
                a = myArrow3D([x1, x2], [y1, y2], [z1, z2], mutation_scale=8, lw=width, arrowstyle="simple", **kwargs)
                self.ax.add_artist(a)
        else:
            segments = [(self.node_positions[source], self.node_positions[target]) for source, target, weight in edges]
            widths = [float(weight["weight"]) for source, target, weight in edges]
            line_collection = Line3DCollection(segments, linewidths=widths, *args, **kwargs)
            self.ax.add_collection3d(line_collection)

    def get_node_label_text(self, path):
        if path is not None:
            self.node_labels_text = []

            with open(path) as file:
                lines = file.read().splitlines()

            for line in lines[1:]:
                params = line.split(sep=' ')
                nodeID = params[0]
                nodeLabel = params[1] 
                self.node_labels_text.append(nodeLabel)

    def draw_node_labels(self, node_labels, text, *args, **kwargs):
        for node, z in self.nodes:
            if node in node_labels:
                self.ax.text(*self.node_positions[(node, z)], text[int(node)-1], *args, **kwargs)

    def draw_layer_labels(self, layer_labels, *args, **kwargs):
        plt.rcParams.update({'font.size': 8})
        if self.path_to_layer_labels is not None:
            for ii in range(self.n_layers):
                self.ax.text(1, 1, float(ii), self.layer_labels[ii], None)
        plt.rcParams.update({'font.size': 12})

    def draw(self):
        self.draw_edges_between_layers(self.edges_between_layers, color='k', alpha=0.3, linestyle='-', linewidth = 0.3, zorder=2)
        self.draw_edges_within_layers(self.edges_within_layers,  color='k', alpha=0.4, linestyle='-', zorder=2)

        for z in range(self.n_layers):
            self.draw_plane(z, alpha=0.2, zorder=1)
            self.draw_nodes([node for node in self.nodes if node[1]==z], s=10, zorder=3)

        self.draw_layer_labels(self.path_to_layer_labels)

        # if self.node_labels:
        #     self.draw_node_labels(self.node_labels, self.node_labels_text, horizontalalignment='center', verticalalignment='center', zorder=100)

        if self.title is not None:
            # Placement 0, 0 would be the bottom left, 1, 1 would be the top right.
            self.ax.text2D(0.05, 0.95, self.title, transform=self.ax.transAxes)

    def aggregate(self, idx):
        """idx - list of incides to be aggregated.
        Returns edges of aggregated network and dict of positions of nodes ('node': (x, y, z))"""
        g = [self.graphs[i] for i in idx]
        aggregated = nx.compose_all(g)
        edges = []
        edges.extend([((source), (target), (aggregated[source][target])) for source, target in aggregated.edges()])
        
        nodes = aggregated.nodes()
        agg_node_positions = dict()

        for node in self.node_positions:
            if node[0] in nodes:
                if node[0] not in agg_node_positions:
                    key = (node[0], node[1])
                    position = self.node_positions[key]
                    agg_node_positions.update({(node[0]): (position)})

        return edges, nodes, agg_node_positions

    def overlap(self, idx):
        """idx - list of incides to be aggregated.
        Returns edges of overlapping network and dict of positions of nodes ('node': (x, y, z))"""
        g = [self.graphs[i] for i in idx]

        graphs = iter(g)
        R = next(graphs)

        for H in graphs:
            edges_R = R.edges()
            edges_H = H.edges()
            
            if self.directed:
                common_edges = set.intersection(set(edges_R), set(edges_H))
                common_edges = list(common_edges)
            else:
                edges_R = [list(ele) for ele in edges_R]
                edges_H = [list(ele) for ele in edges_H]
                common_edges = []
                for edge in edges_R:
                    if edge in edges_H:
                        common_edges.append(tuple(edge))
                    else:
                        edge_rev = [edge[1], edge[0]]
                        if edge_rev in edges_H:
                            common_edges.append(tuple(edge_rev))
            
            R.clear()
            for edge in common_edges:
                R.add_edge(*edge)

        proj_node_positions = dict()

        for node in self.node_positions:
            if node[0] in R.nodes:
                if node[0] not in proj_node_positions:
                    key = (node[0], node[1])
                    position = self.node_positions[key]
                    proj_node_positions.update({(node[0]): (position)})

        return R.edges, R.nodes, proj_node_positions

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 