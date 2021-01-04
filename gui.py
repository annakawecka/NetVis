import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Style, Combobox, Radiobutton, Checkbutton

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D, proj3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import json

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from multiplex_graph import MultiplexGraph

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
                self.radio_var = tk.IntVar()
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

                self.button_aggregate = Button(self, text = "Agregacja", command = self.outer_instance.outer_instance.on_aggregate_click)
                self.button_aggregate.grid(column=1, row=4)
                
                self.button_projection = Button(self, text = "Projekcja", command = self.outer_instance.outer_instance.on_overlap_click)
                self.button_projection.grid(column=1, row=3)

                self.button_inspect = Button(self, text = "Pokaż poziom", command = self.outer_instance.outer_instance.on_inspect_level_click)
                self.button_inspect.grid(column=0, row=3)

                self.radiobutton_frame = Frame(self)
                self.radiobutton_frame.grid(column=0, row=2)

                self.checkbutton_frame = Frame(self)
                self.checkbutton_frame.grid(column=1, row=2)

                self.set_Radio(self.radiobutton_frame)
                self.set_Check(self.checkbutton_frame)
                
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

            def on_checkbox_change(self, event = None):
                indices = [ii for ii, val in enumerate(self.checks_val) if val.get() == 1] 
                self.outer_instance.outer_instance.layers_to_process = indices

            def combobox_callback(self, event = None):
                self.outer_instance.outer_instance.chosen_dataset = self.combobox.current()            

            def init_values_combobox(self, file):
                with open(file, 'r') as f:
                    lines = f.read().splitlines()

                self.combobox['values'] = lines
                self.combobox.current(0)

            def get_com_val(self):
                return self.combobox.get()

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
       

    def on_aggregate_click(self, event = None):
        if(len(self.layers_to_process)) > 0:
            fig = plt.figure(figsize=(3.5,3.5))
        
            newWindow = tk.Toplevel(self) 
            newWindow.title("Aggregation") 
            newWindow.geometry("700x700") 
        
            canvas = FigureCanvasTkAgg(fig, master=newWindow)
            canvas.draw()
            canvas.get_tk_widget().grid(column=0, row=1)

            g_list = self.layers_to_process

            edges, nodes, node_positions = self.data.aggregate(g_list)

            ax = fig.add_subplot(111, projection='3d')
            ax.set_axis_off()

            (xmin, xmax), (ymin, ymax) = self.data.get_extent(pad=0.1)
            u = np.linspace(xmin, xmax, 10)
            v = np.linspace(ymin, ymax, 10)
            U, V = np.meshgrid(u ,v)
            W = 1.0 * np.ones_like(U)
            ax.plot_surface(U, V, W, alpha=0.2, zorder=1) 

            x, y, z = zip(*[node_positions[node] for node in nodes])
            ax.scatter(x, y, 1.0)

            if self.data.directed:
                for source, target, weight in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    # width = float(weight["weight"])
                    width = 1.0
                    a = myArrow3D([x1, x2], [y1, y2], [1.0, 1.0], mutation_scale=4, lw=width, arrowstyle="-|>", color='k', alpha=0.4, linestyle='-', zorder=2)
                    ax.add_artist(a)
            else:
                segments = [] 
                for source, target, weight in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    segments.append(((x1, y1, 1.0), (x2, y2, 1.0)))
                # widths = [float(weight["weight"]) for source, target, weight in edges]
                widths = [1.0 for source, target, weight in edges]
                line_collection = Line3DCollection(segments, linewidths=widths, color='k', alpha=0.4, linestyle='-', zorder=2) 
                ax.add_collection3d(line_collection)

    def on_overlap_click(self, event = None):
        if(len(self.layers_to_process)) > 0:
            fig = plt.figure(figsize=(3.5,3.5))
        
            newWindow = tk.Toplevel(self) 
            newWindow.title("Projection") 
            newWindow.geometry("700x700") 
        
            canvas = FigureCanvasTkAgg(fig, master=newWindow)
            canvas.draw()
            canvas.get_tk_widget().grid(column=0, row=1)

            g_list = self.layers_to_process

            edges, nodes, node_positions = self.data.overlap(g_list)

            ax = fig.add_subplot(111, projection='3d')
            ax.set_axis_off()

            (xmin, xmax), (ymin, ymax) = self.data.get_extent(pad=0.1)
            u = np.linspace(xmin, xmax, 10)
            v = np.linspace(ymin, ymax, 10)
            U, V = np.meshgrid(u ,v)
            W = 1.0 * np.ones_like(U)
            ax.plot_surface(U, V, W, alpha=0.2, zorder=1) 

            x, y, z = zip(*[node_positions[node] for node in nodes])
            ax.scatter(x, y, 1.0)

            if self.data.directed:
                for source, target in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    #width = float(weight["weight"])
                    width = 1.0
                    a = myArrow3D([x1, x2], [y1, y2], [1.0, 1.0], mutation_scale=4, linewidth=width, arrowstyle="-|>", color='k', alpha=0.4, linestyle='-', zorder=2)
                    ax.add_artist(a)
            else:
                segments = [] 
                for source, target in edges:
                    x1, y1, z1 = node_positions[source]
                    x2, y2, z2 = node_positions[target]
                    segments.append(((x1, y1, 1.0), (x2, y2, 1.0)))
                #widths = [float(weight["weight"]) for source, target, weight in edges]
                widths = [1.0 for source, target in edges]
                line_collection = Line3DCollection(segments, linewidths=widths, color='k', alpha=0.4, linestyle='-', zorder=2)
                ax.add_collection3d(line_collection)

    def on_inspect_level_click(self, event = None):
        fig = plt.figure(figsize=(3.5,3.5))
      
        newWindow = tk.Toplevel(self) 
        newWindow.title("Layer") 
        newWindow.geometry("1000x700") 
    
        canvas = FigureCanvasTkAgg(fig, master=newWindow)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)

        idx = self.layer_to_inspect
        graph = self.data.graphs[idx]

        edges, nodes, node_positions, node_degrees = self.data.get_layer(idx)

        ax = fig.add_subplot(111, projection='3d')
        ax.set_axis_off()

        (xmin, xmax), (ymin, ymax) = self.data.get_extent(pad=0.1)
        u = np.linspace(xmin, xmax, 10)
        v = np.linspace(ymin, ymax, 10)
        U, V = np.meshgrid(u ,v)
        W = 0.0 * np.ones_like(U)
        ax.plot_surface(U, V, W, alpha=0.2, zorder=1) 

        xs, ys = [], []

        for node in nodes:
            xx, yy, zz = node_positions[node]
            xs.append(xx)
            ys.append(yy)

        # x, y = zip(xs, ys)

        x, y, z = zip(*[node_positions[node] for node in nodes])
        sizes = [node_degrees[node]*500/len(self.data.nodes) for node in nodes]
        ax.scatter(x, y, 0.0, s=sizes)

        for node in nodes:
            x, y, z = node_positions[(node)]
            z *= 0.0
            ax.text(x, y, z, str(int(node)), size=8)

        if self.data.directed:
            for source, target in edges:
                x1, y1, z1 = node_positions[source]
                x2, y2, z2 = node_positions[target]
                #width = float(weight["weight"])
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