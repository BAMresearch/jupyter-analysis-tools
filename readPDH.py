# -*- coding: utf-8 -*-
# readPDH.py

def readPDH(ifname):
    # function for reading SAXS data files in pdh-format
    q, I, IError = [], [], []

    # q-range of interest 
    qmin = 0.001; qmax = 7.0

    qlims = [qmin, qmax] # min, max
    with open(ifname, 'r') as ifile:
        for i in range(5):
            inline = ifile.readline()

        inline = ifile.readline()
        while inline != '<?xml version="1.0" encoding="utf-8"?>\n':
            if ((float(inline.split("  ")[1]) < qlims[1]) & (float(inline.split("  ")[1]) >= qlims[0])):
                q.append( float(inline.split("  ")[1]) )
                I.append( float(inline.split("  ")[2]) )
                IError.append(  float(inline.split("  ")[1]) )
                             
            inline = ifile.readline()

    ifile.close()
    return q, I, IError  
