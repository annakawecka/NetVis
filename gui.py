import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Style, Combobox

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D, proj3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import json

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from multiplex_graph import MultiplexGraph

class MainWindow(tk.Tk):

    fig = plt.figure(figsize=(6, 5))
    fig2 = plt.figure(figsize=(3,2))
    ax = None
    ax2 = None
    container = None
    chosen_dataset = 0      
    params = []             # list of dictionaries
    data = MultiplexGraph(path="C:/Users/kawec/projects/NetVis/Data/Padgett-Florence-Families_Multiplex_Social/Dataset/Padgett-Florentine-Families_multiplex.edges", n_layers=2, node_labels=[str(nn+1) for nn in range(30)])

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.title("NetVis")
        self.state('zoomed')

        self.container = self.MainFrame(outer_instance=self, fig=self.fig, fig2=self.fig2)

        self.ax = self.fig.add_subplot(111, projection='3d') # has to be done after canvas.draw(), otherwise it's not 3d
        self.ax.set_axis_off()

        self.ax2 = self.fig2.add_subplot(111, projection='3d')
        self.ax2.set_axis_off()

        self.init_params(r'params.json')
        self.on_select_click()

    def get_ax(self):
        return self.ax

    def init_params(self, file):
        with open(file, 'r') as f:
            lines = json.loads(f.read())
        
        self.params = lines

    class MainFrame(Frame):

        def __init__(self, outer_instance, fig, fig2):
            super().__init__()

            self.outer_instance = outer_instance
            self.initUI(fig=fig, fig2=fig2)

        def initUI(self, fig, fig2):
            #self.pack(fill=tk.BOTH, expand=True)

            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(0, weight=1)

            right_frame = self.RightFrame(outer_instance = self, fig2=fig2)
            right_frame.grid(row=0, column=1)

            left_frame = self.LeftFrame(outer_instance = self, fig = fig)
            left_frame.grid(row=0, column=0)

        def get_right_frame(self):
            return self.right_frame

        def get_left_frame(self):
            return self.left_frame

        class RightFrame(Frame):

            def __init__(self, outer_instance, fig2):
                super().__init__()

                self.outer_instance = outer_instance
                self.initUI(fig2=fig2)

            def initUI(self, fig2):
                self.columnconfigure(0, weight=1)
                self.rowconfigure(0, weight=3)
                self.rowconfigure(1, weight=2)

                self.cb_value = tk.StringVar()

                self.combobox = Combobox(self, textvariable = self.cb_value)
                self.combobox.grid(column=0, row=0)
                
                self.init_values_combobox(r'datasets.txt')

                # self.combobox.bind("<<ComboboxSelected>>", lambda _ : print(self.combobox.current()))
                self.combobox.bind("<<ComboboxSelected>>", self.combobox_callback)

                self.button_select = Button(self, text = "Select", command = self.outer_instance.outer_instance.on_select_click)
                self.button_select.grid(column=1, row=0)

                self.button_aggregate = Button(self, text = "Aggregate", command = self.outer_instance.outer_instance.on_aggregate_click)
                self.button_aggregate.grid(column=1, row=1)
                
                self.button_projection = Button(self, text = "Project", command = self.outer_instance.outer_instance.on_overlap_click)
                self.button_projection.grid(column=0, row=1)

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
                canvas.get_tk_widget().grid(column=0, row=1)


    def on_select_click(self, event = None):
        self.fig.clear()

        self.container = self.MainFrame(outer_instance=self, fig=self.fig, fig2=self.fig2)

        ax = self.fig.add_subplot(111, projection='3d')
        dataset = self.params[self.chosen_dataset]
        
        node_labels = [str(nn+1) for nn in range(300)]
        self.data = MultiplexGraph(ax = ax, title=dataset['title'], weighted=is_true(dataset['weighted']), path=path_not_none(dataset['path']), n_layers=int(dataset['n_layers']), directed= is_true(dataset['directed']), node_labels=node_labels, path_to_node_labels=path_not_none(dataset['path_to_node_labels']), path_to_layer_labels=path_not_none(dataset['path_to_layer_labels']))

    def on_aggregate_click(self, event = None):
        fig = plt.figure(figsize=(3.5,3.5))
      
        newWindow = tk.Toplevel(self) 
        newWindow.title("Aggregation") 
        newWindow.geometry("700x700") 
    
        canvas = FigureCanvasTkAgg(fig, master=newWindow)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=1)

        g_list = [0, 1]
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
                width = float(weight["weight"])
                a = myArrow3D([x1, x2], [y1, y2], [1.0, 1.0], mutation_scale=8, lw=width, arrowstyle="simple", **kwargs)
                ax.add_artist(a)
        else:
            segments = [] 
            for source, target, weight in edges:
                x1, y1, z1 = node_positions[source]
                x2, y2, z2 = node_positions[target]
                segments.append(((x1, y1, 1.0), (x2, y2, 1.0)))
            widths = [float(weight["weight"]) for source, target, weight in edges]
            line_collection = Line3DCollection(segments, linewidths=widths)
            ax.add_collection3d(line_collection)

    def on_overlap_click(self, event = None):
        fig = plt.figure(figsize=(3.5,3.5))
      
        newWindow = tk.Toplevel(self) 
        newWindow.title("Projection") 
        newWindow.geometry("700x700") 
    
        canvas = FigureCanvasTkAgg(fig, master=newWindow)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=1)

        g_list = [0, 1] # test list
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
                a = myArrow3D([x1, x2], [y1, y2], [1.0, 1.0], mutation_scale=8, lw=width, arrowstyle="simple", **kwargs)
                ax.add_artist(a)
        else:
            segments = [] 
            for source, target in edges:
                x1, y1, z1 = node_positions[source]
                x2, y2, z2 = node_positions[target]
                segments.append(((x1, y1, 1.0), (x2, y2, 1.0)))
            #widths = [float(weight["weight"]) for source, target, weight in edges]
            widths = [1.0 for source, target in edges]
            line_collection = Line3DCollection(segments, linewidths=widths)
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