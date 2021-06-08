# -*- coding: utf-8 -*-
# plotting.py

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

# increase the limit for the warning to pop up
matplotlib.rcParams['figure.max_open_warning'] = 50

def initFigure(fig, width=80, aspectRatio=4./3., quiet=False):
    mmInch = 25.4
    fig.set_size_inches(width/mmInch, width/aspectRatio/mmInch)
    w, h = fig.get_size_inches()
    if not quiet:
        print("initFigure() with ({w:.1f}x{h:.1f}) mm"
              .format(w=w*mmInch, h=h*mmInch))
    return fig

def createFigure(width=80, aspectRatio=4./3., quiet=False, **kwargs):
    """output figure width in mm"""
    fig = plt.figure(
        #tight_layout=dict(pad=0.05),
        **kwargs
    )
    initFigure(fig, width, aspectRatio, quiet)
    return fig

def plotVertBar(ax, xpos, ymax, **kwargs):
    ax.plot((xpos, xpos), (0, ymax), **kwargs)

def plotColor(idx):
    pltcol = plt.rcParams['axes.prop_cycle'].by_key()['color']
    #print(pltcol)
    pltcol = ['gray', 'lightskyblue', 'steelblue', 'red', 'salmon']
    return pltcol[idx]

def lineWidth():
    return plt.rcParams["lines.linewidth"]

class GenericResult:
    color = None

    @staticmethod
    def getBarWidth(xvec):
        return np.concatenate((np.diff(xvec)[:1], np.diff(xvec)))

    @classmethod
    def plotPeakRange(cls, ax, peakRange, peakDistrib, fullDistrib, moments, distrPar):
        x, y, u = peakDistrib
        xvec, yvec, uvec = fullDistrib
        mom, momLo, momHi = moments
        dp, dpLo, dpHi = distrPar
        #ax.plot(x, y, 'o', color=cls.color)
        lbl, fmt = [], "{: <7s} {: 9.2g} ±{: 9.2g}"
        for k in "area", "median", "var", "skew", "kurt":
            if k == "median":
                lbl.append(fmt.format("median:", dp[-1], max(abs(dp[-1]-dpLo[-1]), abs(dpHi[-1]-dp[-1]))))
            else:
                lbl.append(fmt.format(k+':', mom[k], max(abs(mom[k]-momLo[k]), abs(momHi[k]-mom[k]))))
        ax.bar(x, y, width=cls.getBarWidth(x), color=cls.color, alpha=0.5, label="\n".join(lbl))
        ax.fill_between(x, np.maximum(0, y-u), y+u,
                        color='red', lw=0, alpha=0.1,
                        label=f"uncertainties (lvl: {1/np.median(y/u):.3g})")
        ax.legend(prop=font_manager.FontProperties(family='monospace')); ax.grid(True);