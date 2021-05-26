# -*- coding: utf-8 -*-
# distrib.py

import pandas as pd
import numpy as np
import scipy.integrate

from .utils import grouper

def integrate(xvec, yvec):
    return abs(scipy.integrate.simps(yvec, x=xvec))

def normalizeDistrib(x, y, u=None):
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
        ranges.append((start, end))
    for idx in indexGroups:
        appendPeakRange(istart, indices[idx]) # add the new range to the list
        istart = indices[idx+1]               # start new range
    appendPeakRange(istart, indices[-1])
    #print("findPeakRanges", ranges)
    return ranges

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

def distrParFromPeakRanges(xvec, yvec, uvec, peakRanges, plot=None):
    distrPar = []
    moments = []
    for i, pr in enumerate(peakRanges): # for each peak
        x = xvec.values[pr[0]:pr[1]+1]
        y = yvec.values[pr[0]:pr[1]+1]
        u = uvec.values[pr[0]:pr[1]+1]
        N = integrate(x, y)
        mom = Moments.fromData(x, y)
        momLo = Moments.fromData(x, np.maximum(0, y-u))
        momHi = Moments.fromData(x, y+u)
        dptmp = distrParFromDistrib(mom.mean, mom.var, N=N)
        dptmpLo = distrParFromDistrib(momLo.mean, momLo.var, N=N)
        dptmpHi = distrParFromDistrib(momHi.mean, momHi.var, N=N)
        if plot:
            ax = plot['axes'][i+plot['startIdx']]
            plot['func'](ax, pr, (x,y,u), (xvec,yvec,uvec), (mom,momLo,momHi), (dptmp,dptmpLo,dptmpHi))
        distrPar.append(dptmp)
        moments.append(mom)
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
