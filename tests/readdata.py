# -*- coding: utf-8 -*-
# tests/readdata.py

from pathlib import Path

import numpy

from jupyter_analysis_tools import readdata

pathPDH1 = Path("testdata/S2842 water.pdh")
pathPDH2 = Path("testdata/S2843[9].pdh")  # desmeared silica measurement


def test_readdata1(capsys):
    assert pathPDH1.is_file()
    df, fn = readdata(pathPDH1)
    captured = capsys.readouterr()
    assert captured.out == "Reading file 'testdata\\S2842 water.pdh'\n"
    assert fn == "S2842 water"
    assert df.shape == (1280, 3)
    assert df.columns.tolist() == ["q", "I", "e"]
    assert df.dtypes.tolist() == [numpy.float64, numpy.float64, numpy.float64]
    # checking the first data values
    assert numpy.all(df.loc[:2].values == numpy.array(
            [[-1.005583e00, 5.555556e-08, 2.754402e-08],
             [-9.989474e-01, 3.611111e-07, 6.568830e-08],
             [-9.923112e-01, 3.055556e-07, 6.120415e-08]]))
    # and checking the last data values
    assert numpy.all(df.loc[df.shape[0] - 3 :].values == numpy.array(
            [[7.381979e00, 2.972222e-06, 1.792166e-07],
             [7.388376e00, 2.944444e-06, 1.436040e-07],
             [7.394774e00, 2.388889e-06, 1.548690e-07]]))
    assert numpy.all(df.median().values == numpy.array(
            [3.233221e00, 5.826389e-05, 8.835466e-07]))


def test_readdata2(capsys):
    # test another file with different naming scheme
    assert pathPDH2.is_file()
    df, fn = readdata(pathPDH2, print_filename=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert fn == "S2843"
    assert df.shape == (427, 3)
    assert df.columns.tolist() == ["q", "I", "e"]
    assert numpy.all(df.median().values == numpy.array(
            [1.470428, 0.01907878, 0.01353293]))
