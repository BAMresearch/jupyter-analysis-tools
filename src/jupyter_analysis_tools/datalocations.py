# -*- coding: utf-8 -*-
# datalocations.py

import os
import shutil
import tempfile
from pathlib import Path

from .utils import indent, isList


def getWorkDir(workDir=None, skip=False):
    """Find a local work dir for temporary files, created during analysis.
    The default is *$HOME/data*."""
    if skip:  # stay in the current directory if desired
        return Path(".").absolute()
    if not workDir or (isinstance(workDir, str) and not len(workDir)):
        workDir = Path.home() / "data"
    else:
        workDir = Path(workDir).resolve()
    if not workDir.is_dir():
        workDir.mkdir(workDir, parents=True, exist_ok=True)
    print("Using '{}' as working directory.".format(workDir))
    return workDir


def copy_tree_without_metadata(source, destination):
    source = Path(source)
    destination = Path(destination)

    for path in source.rglob("*"):
        relative = path.relative_to(source)
        target = destination / relative

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)  # contents only; no timestamps or permissions


def prepareWorkDir(workDir, srcDir, useExisting=False):
    """Create a temporary working directory and copy
    the input data (series) to it if not already present."""
    workDir = Path(workDir)
    srcDir = Path(srcDir)
    # source dir has to exist
    if not srcDir.is_dir():
        raise RuntimeError(f"Provided source directory '{srcDir}' not found!")
    # no separate work dir requested?
    if workDir.samefile(Path()):
        print(f"Working in current directory '{workDir}'.")
        return srcDir  # nothing to do
    prefix = srcDir.name + "_"
    if useExisting:  # use an existing work dir, avoid copying
        dirs = workDir.glob(prefix + "*")
        if dirs:
            return list(dirs)[0]  # use the first match
        print("No existing work dir found, creating a new one.")
    # copy all data from src dir to a newly created work dir
    workDir = tempfile.mkdtemp(dir=workDir, prefix=prefix)
    print("Copying data to {}:".format(workDir))
    copy_tree_without_metadata(srcDir, workDir)
    return workDir


def printFileList(fnlst, numParts=2, limit=20):
    def printlst(lst):
        return [print(indent, fn) for fn in lst]

    def shorten(lst):
        return [os.path.join(*Path(fn).parts[-numParts:]) for fn in lst]

    if len(fnlst) > limit:
        printlst(shorten(fnlst[:3]))
        print(indent, "[...]")
        printlst(shorten(fnlst[-3:]))
    else:
        printlst(shorten(fnlst))


def getDataDirs(dataDir, noWorkDir=False, reuseWorkDir=True, workDir=None):
    """Create a local work dir with a copy of the input data and for storing the results.
    (Data might reside in synced folders which creates massive traffic once batch processing
    results get replaced repeately.)

    Parameters
    ----------
    noWorkDir: bool
        False: Copy input data to a new working dir (default),
        True: otherwise, use data where it is.
    reuseWorkDir: bool
        False: Create a new working dir each time,
        True: reuse the work dir if it exists already (default).

    Returns
    -------
    A list of absolute directory paths.
    """
    basedir = getWorkDir(workDir=workDir, skip=noWorkDir)
    workDir = prepareWorkDir(basedir, dataDir, useExisting=reuseWorkDir)
    print("Entering '{}':".format(workDir))
    dirs = sorted([dn for dn in Path(workDir).iterdir() if dn.is_dir()])
    dirs.append(Path(workDir))
    # [print(os.path.join(*dn.parts[-2:])) for dn in dirs]
    printFileList(dirs, numParts=1)
    return dirs


def getDataFiles(dataDirs, include=None, exclude=None, caseSensitive=False):
    """Return absolute file paths from given directories."""

    def getFiles(dn, include=None):
        if not include:
            include = "*"
        if not isList(include):
            include = (include,)
        return [
            path for inc in include for path in Path(dn).glob(inc, case_sensitive=caseSensitive)
        ]

    if not exclude:
        exclude = ()
    if not isList(exclude):
        exclude = (exclude,)
    if not isList(dataDirs):
        dataDirs = (dataDirs,)

    files = [
        fn
        for dn in dataDirs
        for fn in getFiles(dn, include)
        if not any([(ex in str(fn)) for ex in exclude])
    ]
    print("{} files to be analyzed in subdirectories.".format(len(files)))
    return sorted(files)
