# -*- coding: utf-8 -*-
# distrib.py

import pandas as pd
import numpy as np
import scipy.integrate
import scipy.interpolate
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

from .utils import grouper
from .plotting import plotVertBar

def integrate(xvec, yvec):
    return abs(scipy.integrate.simps(yvec, x=xvec))

def normalizeDistrib(x, y, u=None):
    x = x.values if isinstance(x, pd.Series) else x
    y = y.values if isinstance(y, pd.Series) else y
    # normalize the distribution to area of 1
    norm = integrate(x, y)
    #print("CONTINs norm", norm)
    y /= norm
    if u is not None:
        u /= norm
    return x, y, u

def area(xvec, yvec, showArea = True):
    """Returns a string with the area value of the given discrete curve points."""
    return " $\int${:.3g}".format(integrate(xvec, yvec)) if showArea else ""

def findPeakRanges(x, y, tol=1e-16):
    """Returns the location of data/peak above a base line.
    Assumes it touches the baseline before and after. For distributions.
    *tol*: Multiplied by Y to produce a threshold to distinguish noise/artifacts from peaks."""
    x = x.values if isinstance(x, pd.Series) else x
    y = y.values if isinstance(y, pd.Series) else y
    # look at all data above zero, get their array indices
    indices = np.where(y > tol*y.max())[0]
    # segmentation: look where continous groups of indices start and end
    indexGroups = np.where(np.diff(indices) > 1)[0]
    ranges = []
    istart = indices[0]
    def appendPeakRange(start, end):
        #print("appending", start, end, end-start)
        start, end = max(start-1, 0), min(end+1, len(x)-1)
        monotony = np.sign(np.diff(y[start:end+1]))
        if not all(monotony == monotony[0]):
            # avoid monotonously increasing/decreasing peaks -> unwanted artefacts
            ranges.append((start, end))
    for idx in indexGroups:
        appendPeakRange(istart, indices[idx]) # add the new range to the list
        istart = indices[idx+1]               # start new range
    appendPeakRange(istart, indices[-1])
    #print("findPeakRanges", ranges)
    return ranges

def findLocalMinima(peakRanges, xarr, yarr, doPlot=False, verbose=False):
    """Identify local (non-zero) minima within given peak ranges and separate those
    bimodal ranges into monomodal ranges, thus splitting up the peak range if it contains
    maxima connected by non-zero minima. Returns a list of index tuples indicating the
    start and end of each peak. Uses 4th order spline fitting and its derivative
    for finding positions of local minima."""
    #print("findLocalMinima", peakRanges)
    newRanges = []
    if doPlot:
        plt.figure(figsize=(15,5))
    for ip, (istart, iend) in enumerate(peakRanges):
        if verbose: print((istart, iend), xarr[istart], xarr[iend])
        if iend-istart < 5: # skip this, can't be fitted and no sub-peaks are likely
            newRanges.append((istart, iend))
            continue
        while yarr[istart] <= 0. and istart < iend:
            istart += 1 # exclude leading zero
        while yarr[iend] <= 0. and istart < iend:
            iend -= 1 # exclude trailing zero
        if istart == iend:
            continue
        if verbose: print((istart, iend))
        x, y = xarr[istart:iend+1], yarr[istart:iend+1]
        try:
            spline = scipy.interpolate.InterpolatedUnivariateSpline(x, y, k=4)
        except:
            print(f"Warning: Could not findLocalMinima() within {(istart, iend)}!")
            newRanges.append((istart, iend))
            continue
        #if verbose: print(spline(x))
        deriv = spline.derivative()
        #if verbose: print(deriv(x))
        roots = deriv.roots()
        # get indices of roots and ignore any duplicate indices
        rootIdx = set(np.argmin(np.abs(xarr[:,np.newaxis]-roots[np.newaxis,:]), axis=0))
        rootIdx.add(istart); rootIdx.add(iend)
        rootIdx = sorted(rootIdx)
        #if rootIdx[0] == istart: # omit the first root at the beginning
        #    rootIdx = rootIdx[1:]
        if verbose: print((istart, iend), len(roots), roots, rootIdx)
        if doPlot:
            plt.subplot(1,len(peakRanges), ip+1)
            radGrid = np.linspace(x[0], x[-1], 200)
            plt.plot(x, y, label="data")
            plt.plot(radGrid, spline(radGrid), label="spline"),
            plt.ylabel("data & spline approx.")
            handles1, labels1 = plt.gca().get_legend_handles_labels()
            [plotVertBar(plt, xarr[i], spline(radGrid).max(), color="blue", ls=":") for i in rootIdx]
            plt.gca().twinx()
            plt.plot(radGrid, deriv(radGrid), label="deriv. spline", color="green")
            plt.ylabel("1st derivative")
            handles2, labels2 = plt.gca().get_legend_handles_labels()
            plt.grid(); plt.legend(handles1+handles2, labels1+labels2)
        peakBoundaries = rootIdx[::2]
        if verbose: print(peakBoundaries)
        newRanges += [tuple(peakBoundaries[i:i+2]) for i in range(len(peakBoundaries)-1)]
    if verbose: print(newRanges)
    return newRanges

def getLargestPeaks(peakRanges, xarr, yarr, count=1):
    def peakRangeArea(peakRange):
        return integrate(xarr[peakRange[0]:peakRange[1]+1], yarr[peakRange[0]:peakRange[1]+1])
    return sorted(peakRanges, key=peakRangeArea, reverse=True)[:count]

class Moments(dict):
    @staticmethod
    def nthMoment(x, weights, n):
        """Calculates the nth moment of the given distribution weights."""
        center = 0
        if n > 0: # calculate the mean first
            center = np.average(x, weights=weights) if sum(weights) else 0.
            #          np.sqrt(u**2)/len(u) # center uncertainty
        if n == 1:
            return center # the mean
        var = 1.
        if n > 1:
            var = np.sum(weights*(x-center)**2) / np.sum(weights)
        if n == 2:
            return var # the variance
        return np.sum(weights*(x-center)**n) / np.sum(weights) / var**n
    @classmethod
    def fromData(cls, x, y):
        store = cls()
        mean, var, skew, kurt = [cls.nthMoment(x, y, i) for i in range(1,5)]
        store['area'] = integrate(x, y)
        store['mean'] = mean
        store['var'] = var
        store['skew'] = skew
        store['kurt'] = kurt
        return store
    @property
    def area(self):
        return self['area']
    @property
    def mean(self):
        return self['mean']
    @property
    def var(self):
        return self['var']
    @property
    def skew(self):
        return self['skew']
    @property
    def kurt(self):
        return self['kurt']
    def __str__(self):
        return "\n".join(
            ["{: <4s}: {: 9.2g}".format(k, self[k])
             for k in ("area", "mean", "var", "skew", "kurt")]
        )

def distrParFromDistrib(mean, var, N=1.):
    # SASfit manual, 6.4. Log-Normal distribution
    median = mean**2/np.sqrt(var + mean**2)
    sigma = np.sqrt(np.log(mean**2/median**2))
    #print("momentToDistrPar", mean, var, "->", median, sigma)
    return N, sigma, median # return in the order used elsewhere for distrPar

class Distribution:
    x, y, u = None, None, None
    peaks = None # list of peak (start, end) indices pointing into x,y,u
    color = None
    plotAxes, plotAxisIdx = None, 0

    def __init__(self, xvec, yvec, uvec, maxPeakCount=None):
        xvec = xvec.values if isinstance(xvec, pd.Series) else xvec
        yvec = yvec.values if isinstance(yvec, pd.Series) else yvec
        uvec = uvec.values if isinstance(uvec, pd.Series) else uvec
        self.x, self.y, self.u = normalizeDistrib(xvec, yvec, uvec)
        self.peaks = findPeakRanges(self.x, self.y, tol=1e-6)
        # refine the peak ranges containing multiple maxima
        self.peaks = findLocalMinima(self.peaks, self.x, self.y)
        # For a given list of peaks (by start/end indices) return only those
        # whose ratio of amount to uncertainty ratio is always below the given max. ratio
        #maxRatio = 1.5
        #self.peakRanges = [(istart, iend) for istart, iend in self.peakRanges
        #                    if maxRatio > 1/np.median(self.y[istart:iend+1]/self.u[istart:iend+1])]
        # Sort the peaks by area and use the largest (last) only, assuming monomodal distributions
        if maxPeakCount:
            self.peaks = getLargestPeaks(self.peaks, self.x, self.y, count=maxPeakCount)

    def peakData(self, peakRange):
        return (self.x[peakRange[0]:peakRange[1]+1],
                self.y[peakRange[0]:peakRange[1]+1],
                self.u[peakRange[0]:peakRange[1]+1])

    @staticmethod
    def getBarWidth(xvec):
        return np.concatenate((np.diff(xvec)[:1], np.diff(xvec)))

    def plotPeak(self, peakRange, moments, distrPar, showFullRange=False, ax=None):
        """*showFullRange*: Set the x range to cover the whole distribution instead of the peak only."""
        x, y, u = self.peakData(peakRange)
        if not ax:
            ax = plt.gca()
        mom, momLo, momHi = moments
        dp, dpLo, dpHi = distrPar
        #ax.plot(x, y, 'o', color=cls.color)
        lbl, fmt = [], "{: <7s} {: 9.2g} ±{: 9.2g}"
        for k in "area", "median", "var", "skew", "kurt":
            if k == "median":
                lbl.append(fmt.format("median:", dp[-1], max(abs(dp[-1]-dpLo[-1]), abs(dpHi[-1]-dp[-1]))))
            else:
                lbl.append(fmt.format(k+':', mom[k], max(abs(mom[k]-momLo[k]), abs(momHi[k]-mom[k]))))
        lbl.append("LogNorm: "+distrParToText(dp)[0])
        ax.bar(x, y, width=self.getBarWidth(x), color=self.color, alpha=0.5, label="\n".join(lbl))
        ax.fill_between(x, np.maximum(0, y-u), y+u,
                        color='red', lw=0, alpha=0.1,
                        label=f"uncertainties (lvl: {1/np.median(y/u):.3g})")
        if showFullRange:
            ax.set_xlim((self.x.min(), self.x.max()))
        ax.set_xlabel(f"Radius (m)")
        ax.legend(prop=font_manager.FontProperties(family='monospace')); ax.grid(True);

    def plot(self, ax, distPar, name=""):
        """plot complete distribution as loaded from file"""
        lbl = ("from file, " + name
               + area(self.x, self.y, showArea=True)
               +"\n"+distrParLatex(distPar[0]))
        ax.fill_between(self.x, self.y,
               #width=GenericResult.getBarWidth(self.x),
               color=self.color, alpha=0.5, label=lbl)
        #ax.errorbar(self.x, self.y, yerr=self.u, lw=lineWidth()*2, label=lbl)
        ax.fill_between(self.x, np.maximum(0, self.y-self.u), self.y+self.u,
                        color='red', lw=0, alpha=0.1, label="uncertainties")
        ax.set_xlabel(f"Radius (m)")
        ax.legend(); ax.grid(); ax.set_xscale("log")

    def peakDistrPar(self, plotAxes=None, plotAxisStart=0, **plotPeakKwargs):
        distrPar = []
        moments = []
        for i, peakRange in enumerate(self.peaks): # for each peak
            x, y, u = self.peakData(peakRange)
            N = integrate(x, y)
            mom = Moments.fromData(x, y)
            momLo = Moments.fromData(x, np.maximum(0, y-u))
            momHi = Moments.fromData(x, y+u)
            dptmp = distrParFromDistrib(mom.mean, mom.var, N=N)
            dptmpLo = distrParFromDistrib(momLo.mean, momLo.var, N=N)
            dptmpHi = distrParFromDistrib(momHi.mean, momHi.var, N=N)
            distrPar.append(dptmp)
            moments.append(mom)
            if plotAxes is not None:
                plotPeakKwargs['ax'] = plotAxes[plotAxisStart+i]
                self.plotPeak(peakRange, (mom,momLo,momHi), (dptmp,dptmpLo,dptmpHi), **plotPeakKwargs)
        return distrPar, moments

def distrParToText(distrPar):
    numPars = 3
    if len(distrPar) > numPars:
        fmt = "R_{i}={:3.0f} s_{i}={:0.2f} N_{i}={:.3g}"
    else:
        fmt = "R={:3.0f} s={:0.2f} N={:.3g}"
    return [fmt.format(p[2]*1e9, p[1], p[0], i = i)
            for i, p in enumerate(grouper(distrPar, numPars))]

def distrParToFilename(distrPar, prefix=''):
    return '_'.join([prefix] + distrParToText(distrPar)).replace(' ', '_')

def distrParLatex(distrPar, *kwargs):
    return "\n".join(['$'+txt.replace(' ',r'\;')+'$' for txt in distrParToText(distrPar)])

def distrParFromFilename(fn):
    fn = fn.split('=')
    fn = [elem.lstrip('_') for elem in fn]
    fn = [(elem.split('_', maxsplit=1) if elem[0].isnumeric() else [elem]) for elem in fn]
    fn = list(itertools.chain(*fn))
    return list(itertools.chain(*[(float(grp[5]), float(grp[3]), float(grp[1])*1e-9)
                                  for grp in grouper(fn, 6)]))

def test():
    """Some testing."""
    distrPar = (1, 0.2, 40e-9)
    print("distrPar:      ", list(grouper(distrPar, 3)))
    print("distrParToText:", distrParToText(distrPar))
    print("distrParLatex: ", distrParLatex(distrPar))
    print("distrParToFilename:  ", distrParToFilename(distrPar))
    print("distrParFromFilename:", distrParFromFilename(distrParToFilename(distrPar)))
    print("distrParFromFilename:", distrParFromFilename(distrParToFilename(distrPar, "lognorm")))
    print()
    distrPar = (1, 0.2, 40e-9)+(1, 0.1, 10e-9)
    print("distrPar:      ", list(grouper(distrPar, 3)))
    print("distrParToText:", distrParToText(distrPar))
    print("distrParLatex: ", distrParLatex(distrPar))
    print("distrParToFilename:  ", distrParToFilename(distrPar))
    print("distrParFromFilename:", distrParFromFilename(distrParToFilename(distrPar)))
    print("distrParFromFilename:", distrParFromFilename(distrParToFilename(distrPar, "lognorm")))
