import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Style, Combobox

import matplotlib.pyplot as plt

import json

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from multiplex_graph import MultiplexGraph

class MainWindow(tk.Tk):

    fig = plt.figure(figsize=(5, 5))
    ax = None
    container = None
    chosen_dataset = 0      
    params = []             # list of dictionaries

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.title("NetVis")
        self.state('zoomed')

        self.container = self.MainFrame(outer_instance=self, fig=self.fig)

        self.ax = self.fig.add_subplot(111, projection='3d') # has to be done after canvas.draw(), otherwise it's not 3d
        self.ax.set_axis_off()
        self.init_params(r'params.json')

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
            self.initUI(fig)

        def initUI(self, fig):
            #self.pack(fill=tk.BOTH, expand=True)

            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(0, weight=1)

            right_frame = self.RightFrame(outer_instance = self)
            right_frame.grid(row=0, column=1)

            left_frame = self.LeftFrame(outer_instance = self, fig = fig)
            left_frame.grid(row=0, column=0)

        def get_right_frame(self):
            return self.right_frame

        def get_left_frame(self):
            return self.left_frame

        class RightFrame(Frame):

            def __init__(self, outer_instance):
                super().__init__()

                self.outer_instance = outer_instance
                self.initUI()

            def initUI(self):
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


    def on_select_click(self, event = None):
        fig = self.fig

        self.container = self.MainFrame(outer_instance=self, fig=self.fig)

        ax = fig.add_subplot(111, projection='3d')

        dataset = self.params[self.chosen_dataset]

        node_labels = [str(nn+1) for nn in range(300)]
        data = MultiplexGraph(ax = ax, path=path_not_none(dataset['path']), n_layers=int(dataset['n_layers']), directed= is_true(dataset['directed']), node_labels=node_labels, path_to_node_labels=path_not_none(dataset['path_to_node_labels']), path_to_layer_labels=path_not_none(dataset['path_to_layer_labels']))

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