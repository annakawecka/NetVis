import tkinter as tk
from tkinter.ttk import Frame, Button, Label, Style, Combobox

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from multiplex_graph import MultiplexGraph

class MainWindow(tk.Tk):

    fig = plt.figure(figsize=(5, 5))
    ax = None

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.title("NetVis")
        self.state('zoomed')

        self.container = self.MainFrame(outer_instance=self, fig=self.fig)

        self.ax = self.fig.add_subplot(111, projection='3d') # has to be done after canvas.draw(), otherwise it's not 3d
        self.ax.set_axis_off()

    def get_ax(self):
        return self.ax


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

                self.button_select = Button(self, text = "Select", command = self.outer_instance.outer_instance.on_select_click)
                self.button_select.grid(column=1, row=0)

            def init_values_combobox(self, file):
                with open(file, 'r') as f:
                    lines = f.read().splitlines()

                self.combobox['values'] = lines
                self.combobox.current(0)


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

        node_labels = [str(nn+1) for nn in range(30)]
        data = MultiplexGraph(ax = ax, path=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_multiplex.edges", n_layers=2, directed=True, node_labels=node_labels, path_to_node_labels=r"C:\Users\kawec\projects\NetVis\Data\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_nodes.txt")
