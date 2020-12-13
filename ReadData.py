import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import sys

sys.path.append(r"C:\Users\kawec\projects\NetVis\Multilayer-networks-library-master")
import pymnet

class ReadData(object):

    def __init__(self):
        with open(r"C:\Users\kawec\projects\NetVis\Padgett-Florence-Families_Multiplex_Social\Dataset\Padgett-Florentine-Families_multiplex.edges") as file:
            line = file.readline()
            print(line)