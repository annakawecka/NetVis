import tkinter as tk
from tkinter import ttk


# class ScrollableFrame(ttk.Frame):
#     def __init__(self, container, *args, **kwargs):
#         super().__init__(container, *args, **kwargs)
#         canvas = tk.Canvas(self)
#         scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
#         self.scrollable_frame = ttk.Frame(canvas)

#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(
#                 scrollregion=canvas.bbox("all")
#             )
#         )

#         canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

#         canvas.configure(yscrollcommand=scrollbar.set)

#         canvas.pack(side="left", fill="both", expand=True)
#         scrollbar.pack(side="right", fill="y")

class ScrollableFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
