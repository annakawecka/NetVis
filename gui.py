import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Style, Combobox, Radiobutton, Checkbutton

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import mplcursors

from mpl_toolkits.mplot3d import Axes3D, proj3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import json

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from multiplex_graph import MultiplexGraph, intersection
from scrollable_frame import ScrollableFrame

from fancy_arrow import myArrow3D

class MainWindow(tk.Tk):

    fig = plt.figure(figsize=(6, 5))
    ax = None
    container = None
    chosen_dataset = 0      
    params = []             # list of dictionaries
    data = MultiplexGraph(title="Padgett Florence Families Social",  path="C:/Users/kawec/projects/NetVis/Data/Padgett-Florence-Families_Multiplex_Social/Dataset/Padgett-Florentine-Families_multiplex.edges",   n_layers=2,    directed=False,    weighted=False,     path_to_node_labels="C:/Users/kawec/projects/NetVis/Data/Padgett-Florence-Families_Multiplex_Social/Dataset/Padgett-Florentine-Families_nodes.txt", path_to_layer_labels="C:/Users/kawec/projects/NetVis/Data/Padgett-Florence-Families_Multiplex_Social/Dataset/Padgett-Florentine-Families_layers.txt")
    layer_to_inspect = 0
    layers_to_process = []
    layers_to_compute_pearson = []

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.title("NetVis")
        self.state('zoomed')

        self.container = self.MainFrame(outer_instance=self, fig=self.fig)#, data=self.data)

        self.ax = self.fig.add_subplot(111, projection='3d') # has to be done after canvas.draw(), otherwise it's not rotating
        self.ax.set_axis_off()
        self.ax.mouse_init()

        self.init_params(r'params.json')
        self.on_select_click()

    def get_ax(self):
        return self.ax

    def init_params(self, file):
        with open(file, 'r') as f:
            lines = json.loads(f.read())
        
        self.params = lines

    class MainFrame(Frame):

        def __init__(self, outer_instance, fig):
            super().__init__()
            self.outer_instance = outer_instance
            self.initUI(fig=fig)

        def initUI(self, fig):
            self.right_frame = self.RightFrame(outer_instance = self)
            self.right_frame.grid(row=0, column=1)

            self.left_frame = self.LeftFrame(outer_instance = self, fig = fig)
            self.left_frame.grid(row=0, column=0)

        def get_right_frame(self):
            return self.right_frame

        def get_left_frame(self):
            return self.left_frame

        def removethis(self):
            self.destroy()

        class RightFrame(Frame):

            def __init__(self, outer_instance):
                super().__init__()

                self.outer_instance = outer_instance
                self.radios = []
                self.checks = []
                self.pearsons = []
                self.radio_var = tk.IntVar()
                self.labelText = tk.StringVar()
                self.pearson_label = Label(self, textvariable = self.labelText)
                self.initUI()

            def initUI(self):
                self.columnconfigure(0, weight=1)
                self.rowconfigure(0, weight=3)
                self.rowconfigure(1, weight=2)

                self.cb_value = tk.StringVar()

                self.combobox = Combobox(self, textvariable = self.cb_value)
                self.combobox.grid(column=0, row=0)
                
                self.init_values_combobox(r'datasets.txt')

                self.combobox.bind("<<ComboboxSelected>>", self.combobox_callback)

                self.button_select = Button(self, text = "Wybierz", command = self.outer_instance.outer_instance.on_select_click)
                self.button_select.grid(column=1, row=0)

                self.button_aggregate = Button(self, text = "Projekcja", command = self.outer_instance.outer_instance.on_aggregate_click)
                self.button_aggregate.grid(column=1, row=4)
                
                self.button_projection = Button(self, text = "Przekrycia", command = self.outer_instance.outer_instance.on_overlap_click)
                self.button_projection.grid(column=1, row=3)

                self.button_inspect = Button(self, text = "Pokaż poziom", command = self.outer_instance.outer_instance.on_inspect_level_click)
                self.button_inspect.grid(column=0, row=3)

                self.radiobutton_frame = Frame(self)
                self.radiobutton_frame.grid(column=0, row=2)

                self.checkbutton_frame = Frame(self)
                self.checkbutton_frame.grid(column=1, row=2)

                self.pearson_label.grid(column=1, row=6)

                # self.perason_frame = Frame(self)
                # self.perason_frame.grid(column=0, row=6)
                self.undirected_frame = Frame(self)
                self.undirected_frame.grid(column = 0, row = 1)

                self.pearsons_button = Button(self, text = "Wspł. Pearsona", command = self.on_pearson_click)
                self.pearsons_button.grid(column=1, row=5)

                self.set_Radio(self.radiobutton_frame)
                self.set_Check(self.checkbutton_frame)
                # self.set_Pearson(self.perason_frame)
                
            def set_Radio(self, frame):
                for widget in self.radios:
                    widget.destroy()
                self.radios = []
                
                names = self.outer_instance.outer_instance.data.layer_labels
                for t in range(self.outer_instance.outer_instance.data.n_layers):
                    b = Radiobutton(frame, text=names[t], variable=self.radio_var, value=t, command=self.on_radiobutton_change)
                    self.radios.append(b)
                    b.pack(anchor = tk.W)

            def on_radiobutton_change(self, event = None):
                self.outer_instance.outer_instance.layer_to_inspect = int(self.radio_var.get())

            def set_Check(self, frame):
                for widget in self.checks:
                    widget.destroy()
                self.checks = []
                self.checks_val = []
                names = self.outer_instance.outer_instance.data.layer_labels
                for t in range(self.outer_instance.outer_instance.data.n_layers):
                    var = tk.IntVar()
                    self.checks_val.append(var)
                    b = Checkbutton(frame, text=names[t], variable=self.checks_val[t], onvalue=1, offvalue=0, command=self.on_checkbox_change)
                    self.checks.append(b)
                    b.pack(anchor = tk.W)

            def set_Pearson(self, frame):
                for widget in self.pearsons:
                    widget.destroy()
                self.pearsons = []
                self.pearsons_val = []
                names = self.outer_instance.outer_instance.data.layer_labels
                for t in range(self.outer_instance.outer_instance.data.n_layers):
                    var = tk.IntVar()
                    self.pearsons_val.append(var)
                    b = Checkbutton(frame, text=names[t], variable=self.pearsons_val[t], onvalue=1, offvalue=0, command=self.on_pearson_change)
                    self.pearsons.append(b)
                    b.pack(anchor = tk.W)

            def set_undirected_Button(self, frame):
                if self.outer_instance.outer_instance.data.directed:
                    self.undirected_button = Button(frame, text = "Do nieskierowanej", command = self.outer_instance.outer_instance.on_to_undirected_click)
                    self.undirected_button.pack()

            def on_checkbox_change(self, event = None):
                indices = [ii for ii, val in enumerate(self.checks_val) if val.get() == 1] 
                self.outer_instance.outer_instance.layers_to_process = indices

            def on_pearson_change(self, event = None):
                indices = [ii for ii, val in enumerate(self.checks_val) if val.get() == 1] 
                self.outer_instance.outer_instance.layers_to_compute_pearson = indices

            def combobox_callback(self, event = None):
                self.outer_instance.outer_instance.chosen_dataset = self.combobox.current()            

            def init_values_combobox(self, file):
                with open(file, 'r') as f:
                    lines = f.read().splitlines()

                self.combobox['values'] = lines
                self.combobox.current(0)

            def get_com_val(self):
                return self.combobox.get()

            def on_pearson_click(self, event = None):
                if len(self.outer_instance.outer_instance.layers_to_process) != 2:
                    self.labelText.set('Wybierz 2 poziomy')
                else:
                    r = self.outer_instance.outer_instance.compute_pearson_coefficient()
                    self.labelText.set(round(r,2))
                

        class LeftFrame(Frame):

            def __init__(self, outer_instance, fig):
                super().__init__()

                self.outer_instance = outer_instance
                self.initUI(fig)

            def initUI(self, fig):
                canvas = FigureCanvasTkAgg(fig, master=self)
                canvas.draw()
                canvas.get_tk_widget().grid(column=0, row=0)
                # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def on_select_click(self, event = None):
        self.fig.clear()

        self.container.right_frame.destroy()
        self.container = self.MainFrame(outer_instance=self, fig=self.fig)

        ax = self.fig.add_subplot(111, projection='3d')
        dataset = self.params[self.chosen_dataset]
        
        node_labels = [str(nn+1) for nn in range(300)]
        self.data = MultiplexGraph(ax = ax, title=dataset['title'], weighted=is_true(dataset['weighted']), path=path_not_none(dataset['path']), n_layers=int(dataset['n_layers']), directed= is_true(dataset['directed']), node_labels=node_labels, path_to_node_labels=path_not_none(dataset['path_to_node_labels']), path_to_layer_labels=path_not_none(dataset['path_to_layer_labels']))
        
        self.container.right_frame.set_Radio(self.container.right_frame.radiobutton_frame)
        self.container.right_frame.set_Check(self.container.right_frame.checkbutton_frame)   
        self.container.right_frame.set_undirected_Button(self.container.right_frame.undirected_frame)

    def on_aggregate_click(self, event = None):
        self.on_ag_ov_ins_click(mode = 'aggregate')
        
    def on_overlap_click(self, event = None):
        self.on_ag_ov_ins_click(mode = 'overlap')
        
    def on_inspect_level_click(self, event = None):
        self.on_ag_ov_ins_click(mode = 'inspect')
        
    def on_ag_ov_ins_click(self, event = None, mode = 'aggregate'):
        if mode == 'aggregate' or mode == 'overlap':
            if(len(self.layers_to_process)) == 0:
                return

        if mode == 'aggregate':
            g_list = self.layers_to_process
            edges, nodes, node_positions, graph = self.data.aggregate(g_list)
            window_name = 'Agregacja'
        elif mode == 'overlap':
            g_list = self.layers_to_process
            edges, nodes, node_positions, graph = self.data.overlap(g_list)
            window_name = 'Projekcja'
        elif mode == 'inspect':
            idx = self.layer_to_inspect
            edges, nodes, node_positions, node_degrees, graph = self.data.get_layer(idx)
            window_name = 'Poziom'

        fig = plt.figure(figsize=(3.5,3.5))
      
        newWindow = tk.Toplevel(self) 
        newWindow.title(window_name) 
        newWindow.geometry("1000x700") 
    
        canvas = FigureCanvasTkAgg(fig, master=newWindow)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)

        frame = Frame(master=newWindow)
        frame.grid(column=1, row=0)

        # scroll_frame = ScrollableFrame(parent=frame)
        # scroll_frame.pack(anchor = tk.W)

        text_field = tk.Text(master=frame, height=10, width=22)
        text_field.pack(anchor = tk.W)

        ax = fig.add_subplot(111, projection='3d')
        ax.set_axis_off()

        (xmin, xmax), (ymin, ymax) = self.data.get_extent(pad=0.1)
        u = np.linspace(xmin, xmax, 10)
        v = np.linspace(ymin, ymax, 10)
        U, V = np.meshgrid(u ,v)
        W = 0.0 * np.ones_like(U)
        ax.plot_surface(U, V, W, alpha=0.2, zorder=1) 

        if len(edges) == 0:
            return 

        xs, ys, zs = [], [], []

        has_node_labels = path_not_none(self.data.path_to_node_labels)

        mean_degree = 0
        node_names = []
        
        for node in nodes:
            x, y, z = node_positions[(node)]
            z *= 0.0
            if has_node_labels:
                node_names.append(self.data.node_labels_text[int(node)-1])
                # tk.Label(scroll_frame.interior, text=str(node) + ' - ' + self.data.node_labels_text[int(node)-1]).pack(anchor = tk.W)
            else:
                node_names.append(node)
            # ax.text(x, y, z, str(int(node)), size=4)
            xs.append(x)
            ys.append(y)
            zs.append(0.0)
            mean_degree += graph.degree[node]
                
        mean_degree /= len(nodes)
            
        xs = np.array(xs)
        ys = np.array(ys)
        zs = np.array(zs)
        X = np.column_stack((xs, ys, zs))

        x, y, z = zip(*[node_positions[node] for node in nodes])
        if mode == 'inspect':
            sizes = [node_degrees[node]*200/len(self.data.nodes) for node in nodes]
            sc = ax.scatter(x, y, 0.0, s=sizes, picker=True)
        else:
            sc = ax.scatter(x, y, 0.0, picker=True)

        annot = ax.annotate("", xy=(0,0), xytext=(10,10),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))

        annot.set_visible(False)

        cid = fig.canvas.mpl_connect('button_press_event', lambda event: hover(event, ax=ax, sc=sc, fig=fig, annot=annot, names=node_names, points=X))

        if mode == 'inspect':
            if self.data.directed:
                for source, target, weight in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    width = float(weight["weight"])
                    a = myArrow3D([x1, x2], [y1, y2], [0.0, 0.0], mutation_scale=4, linewidth=width, arrowstyle="-|>", color='k', alpha=0.4, linestyle='-', zorder=2)
                    ax.add_artist(a)
            else:
                segments = [] 
                for source, target, weight in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    segments.append(((x1, y1, 0.0), (x2, y2, 0.0)))
                widths = [float(weight["weight"]) for source, target, weight in edges]
                line_collection = Line3DCollection(segments, linewidths=widths, color='k', alpha=0.4, linestyle='-', zorder=2)
                ax.add_collection3d(line_collection)
        else:
            if self.data.directed:
                for source, target in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    width = 1.0
                    a = myArrow3D([x1, x2], [y1, y2], [0.0, 0.0], mutation_scale=4, linewidth=width, arrowstyle="-|>", color='k', alpha=0.4, linestyle='-', zorder=2)
                    ax.add_artist(a)
            else:
                segments = [] 
                for source, target in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    segments.append(((x1, y1, 0.0), (x2, y2, 0.0)))
                #widths = [float(weight["weight"]) for source, target, weight in edges]
                widths = [1.0 for source, target in edges]
                line_collection = Line3DCollection(segments, linewidths=widths, color='k', alpha=0.4, linestyle='-', zorder=2)
                ax.add_collection3d(line_collection)
        
        try:
            average_path = nx.average_shortest_path_length(graph)
        except:
            pass
        average_clustering_coefficient = nx.average_clustering(graph)
        density = nx.density(graph)
        no_of_nodes = nx.number_of_nodes(graph)
        no_of_edges = nx.number_of_edges(graph)

        text_field.insert(tk.END, 'Liczba węzów: ' + str(no_of_nodes) + '\n')
        text_field.insert(tk.END, 'Liczba krawędzi: ' + str(no_of_edges) + '\n')
        text_field.insert(tk.END, '<k>:' + str(round(mean_degree,2)) + '\n')
        text_field.insert(tk.END, 'Śr. współ. gronowania: ' + str(round(average_clustering_coefficient,2)) + '\n')
        try:
            text_field.insert(tk.END, 'Śr. droga: ' + str(round(average_path,2)) + '\n')
        except:
            pass
        text_field.insert(tk.END, 'Gęstość: ' + str(round(density,2)) + '\n')

        text_field.configure(state='disabled')

        return fig

    def on_to_undirected_click(self, event = None):
        self.fig.clear()

        self.container.right_frame.destroy()
        self.container = self.MainFrame(outer_instance=self, fig=self.fig)

        ax = self.fig.add_subplot(111, projection='3d')
        dataset = self.params[self.chosen_dataset]
        
        node_labels = [str(nn+1) for nn in range(300)]
        self.data = MultiplexGraph(ax = ax, title=dataset['title'], weighted=is_true(dataset['weighted']), path=path_not_none(dataset['path']), n_layers=int(dataset['n_layers']), directed=False, node_labels=node_labels, path_to_node_labels=path_not_none(dataset['path_to_node_labels']), path_to_layer_labels=path_not_none(dataset['path_to_layer_labels']))
        
        self.container.right_frame.set_Radio(self.container.right_frame.radiobutton_frame)
        self.container.right_frame.set_Check(self.container.right_frame.checkbutton_frame)   
        self.container.right_frame.set_undirected_Button(self.container.right_frame.undirected_frame)

    def compute_pearson_coefficient(self):
        g_list = self.layers_to_process
        g1 = self.data.graphs[g_list[0]]
        g2 = self.data.graphs[g_list[1]]

        nodes1 = g1.nodes
        nodes2 = g2.nodes
        common_nodes = intersection(nodes1, nodes2)
        N = len(common_nodes)

        r = 0.0
        mean_deg1 = 0
        mean_deg2 = 0
        mean_deg1_sq = 0
        mean_deg2_sq = 0
        sigma1 = 0
        sigma2 = 0
        for i in range(N):
            d1 = g1.degree[common_nodes[i]]
            d2 = g2.degree[common_nodes[i]]
            r += d1 * d2
            mean_deg1 += d1
            mean_deg2 += d2
            mean_deg1_sq += d1**2
            mean_deg2_sq += d2**2
        r /= N
        mean_deg1 /= N
        mean_deg2 /= N
        mean_deg1_sq /= N
        mean_deg2_sq /= N
        sigma1 = mean_deg1_sq - mean_deg1**2
        sigma2 = mean_deg2_sq - mean_deg2**2
        r -= mean_deg1 * mean_deg2
        r /= np.sqrt(sigma1 * sigma2)
        return r     

def distance(point, event, fig, ax):
        """Return distance between mouse position and given data point
        Args:
            point (np.array): np.array of shape (3,), with x,y,z in data coords
            event (MouseEvent): mouse event (which contains mouse position in .x and .xdata)
        Returns:
            distance (np.float64): distance (in screen coords) between mouse pos and data point
        """
        assert point.shape == (3,), "distance: point.shape is wrong: %s, must be (3,)" % point.shape

        # Project 3d data space to 2d data space
        x2, y2, _ = proj3d.proj_transform(point[0], point[1], point[2], ax.get_proj())
        # Convert 2d data space to 2d screen space
        x3, y3 = ax.transData.transform((x2, y2))

        return np.sqrt ((x3 - event.x)**2 + (y3 - event.y)**2)

def calcClosestDatapoint(X, event, fig, ax):
        """"Calculate which data point is closest to the mouse position.
        Args:
            X (np.array) - array of points, of shape (numPoints, 3)
            event (MouseEvent) - mouse event (containing mouse position)
        Returns:
            smallestIndex (int) - the index (into the array of points X) of the element closest to the mouse position
        """
        distances = [distance(X[i, 0:3], event, fig, ax) for i in range(X.shape[0])]
        return np.argmin(distances)

def update_annot(ind, fig, ax, sc, annot, names, points):
    x2, y2,_ = proj3d.proj_transform(points[ind, 0], points[ind, 1], points[ind, 2], ax.get_proj())
    annot.xy = (x2, y2)
    text = names[int(ind)]
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

def hover(event, ax, sc, fig, annot, names, points):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            closestIndex = calcClosestDatapoint(points, event, fig, ax)
            update_annot(closestIndex, fig, ax, sc, annot, names, points)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

def is_true(str: str):
    if str == 'True':
        return True
    else:
        return False

def path_not_none(path: str):
    if path == 'None':
        return None
    else:
        return path