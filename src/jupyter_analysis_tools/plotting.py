# -*- coding: utf-8 -*-
# plotting.py

import matplotlib
import matplotlib.pyplot as plt

try:
    # increase the limit for the warning to pop up
    matplotlib.rcParams["figure.max_open_warning"] = 50
except TypeError:  # ignore the error with Sphinx
    pass


def initFigure(fig, width=80, aspectRatio=4.0 / 3.0, quiet=False):
    mmInch = 25.4
    fig.set_size_inches(width / mmInch, width / aspectRatio / mmInch)
    w, h = fig.get_size_inches()
    if not quiet:
        print("initFigure() with ({w:.1f}x{h:.1f}) mm".format(w=w * mmInch, h=h * mmInch))
    return fig


def createFigure(width=80, aspectRatio=4.0 / 3.0, quiet=False, **kwargs):
    """output figure width in mm"""
    fig = plt.figure(
        # tight_layout=dict(pad=0.05),
        **kwargs
    )
    initFigure(fig, width, aspectRatio, quiet)
    return fig


def plotVertBar(ax, xpos, ymax, **kwargs):
    ax.plot((xpos, xpos), (0, ymax), **kwargs)


def plotColor(idx):
    pltcol = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    # print(pltcol)
    pltcol = ["gray", "lightskyblue", "steelblue", "red", "salmon"]
    return pltcol[idx]


def lineWidth():
    return plt.rcParams["lines.linewidth"]
