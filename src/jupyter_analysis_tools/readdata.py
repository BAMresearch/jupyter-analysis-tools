# -*- coding: utf-8 -*-
# readdata.py

import json
import warnings
import xml.etree.ElementTree as et
from pathlib import Path

import pandas as pd


def readdata(fpath, q_range=None, read_csv_args=None, print_filename=True):
    """Read a datafile pandas Dataframe
    extract a file_name
    select q-range: q_min <= q <= q_max
    """
    fpath = Path(fpath)
    if print_filename:
        print(f"Reading file '{str(fpath)}'")
    if read_csv_args is None:
        read_csv_args = dict()
    if "sep" not in read_csv_args:
        read_csv_args.update(sep=r"\s+")
    if "names" not in read_csv_args:
        read_csv_args.update(names=("q", "I", "e"))
    if "index_col" not in read_csv_args:
        read_csv_args.update(index_col=False)
    # print("f_read_data, read_csv_args:", read_csv_args) # for debugging

    file_ext = fpath.suffix
    if file_ext.lower() == ".pdh":  # for PDH files
        nrows = pd.read_csv(
            fpath,
            skiprows=2,
            nrows=1,
            usecols=[
                0,
            ],
            sep=r"\s+",
            header=None,
        ).values[0, 0]
        read_csv_args.update(skiprows=5, nrows=nrows)
    df = pd.read_csv(fpath, **read_csv_args)

    # select q-range
    if q_range is not None:
        q_min, q_max = q_range
        df = df[(df.q > q_min) & (df.q < q_max)]

    filename = fpath.stem.split("[")[0]
    return df, filename

