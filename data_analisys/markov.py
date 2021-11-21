import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import random as rm
import pandas as pd
from pydtmc import MarkovChain, plot_graph, plot_eigenvalues

files = ["results/aversion_direction_one_stacking_trans.txt",
         "results/aversion_direction_trans.txt",
         "results/aversion_direction_strict_adaptive_period_trans.txt",
         "results/aversion_direction_strict_period_trans.txt",
         "results/one_stacking_trans.txt",
         "results/raw_data_trans.txt",
         "results/Strict_adaptive_period_trans.txt",
         "results/Strict_period_trans.txt"]

# files2 = ["results/aversion_direction_one_stacking_trans.txt"]
files2 = ["resources/aversion_direction_less_dirs_trans.txt"]

def transition_matrix(trans):
    df = pd.DataFrame(columns=['state', 'next_state'])
    for tr in trans:
        for i, val in enumerate(tr[:-1]):  # We don't care about last state
            df_stg = pd.DataFrame(index=[0])
            df_stg['state'], df_stg['next_state'] = tr[i], tr[i + 1]
            df = pd.concat([df, df_stg], axis=0)
    cross_tab = pd.crosstab(df['state'], df['next_state'])
    cross_tab = cross_tab.div(cross_tab.sum(axis=1), axis=0)
    return cross_tab




def main():
    for file in files:
        f = open(file, "r")
        lines = f.readlines()
        res = [line.split() for line in lines]
        cross_tab = transition_matrix(res)
        f.close()
        # print(file[:-4])
        # print(cross_tab)
        mc = MarkovChain(cross_tab.values, cross_tab.index._data)
        r = open(file.replace("_trans", "_matrix"),"w")
        r.write(str(mc.p))
        r.close()
        # matplotlib.interactive(True)
        figure , _ = plot_graph(mc, dpi=1000, path="/home/ja/Dokumenty/Pepper/data_analisys/" + file.replace("_trans.txt", "_graph.svg"))
        plt.close()
        # plt.waitforbuttonpress()

if __name__ == '__main__':
    main()



