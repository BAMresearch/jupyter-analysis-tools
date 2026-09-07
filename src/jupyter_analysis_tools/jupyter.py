# -*- coding: utf-8 -*-
# jupyter.py

import locale
import os
import sys
from pathlib import Path

from .utils import isWindows


def setLocaleUTF8():
    """Fix the Jupyter locale which is not UTF-8 by default on Windows."""
    locOld = locale.getpreferredencoding(False).lower()

    def getpreferredencoding(do_setlocale=True):
        return "utf-8"

    locale.getpreferredencoding = getpreferredencoding
    locNew = locale.getpreferredencoding(False)
    if locOld != locNew:
        print(f"Updated locale from {locOld} -> {locNew}.")


def addEnvScriptsToPATH():
    """Prepends the *Scripts* directory of the current Python environment base directory to systems
    PATH variable.

    It is intended for Conda (Miniforge) environments on Windows that do not have this in their PATH
    environment variable, causing them to miss many commands provided from this location.
    """
    envPath = [p for p in sys.path if p.endswith("Lib")]
    if not envPath:
        return  # probably not a Miniforge environment
    envPath = envPath[0]
    envPath = Path(envPath).parent / "Scripts"
    sep = ";" if isWindows() else ":"
    environPATH = os.environ["PATH"].split(sep)
    if envPath.exists() and str(envPath) not in environPATH:
        environPATH = [str(envPath)] + environPATH
        os.environ["PATH"] = sep.join(environPATH)


def ensureMiniforgeInPATH():
    """Ensure the active Miniforge environment is on PATH for Jupyter/Conda commands on Windows."""
    if not isWindows():
        return

    envpath = Path(sys.executable).parent
    paths = os.environ["PATH"].split(";")
    if "miniforge" not in str(envpath):
        return
    if any(envpath.name in item for item in paths):
        return

    lst = [
        str(envpath),
        str(envpath / "Library/mingw-w64/bin"),
        str(envpath / "Library/usr/bin"),
        str(envpath / "Library/bin"),
        str(envpath / "Scripts"),
        str(envpath / "bin"),
        str(envpath.parent.parent / "condabin"),
    ]
    os.environ["PATH"] = ";".join(lst + paths)
    os.environ["CONDA_PREFIX"] = str(envpath)
    os.environ["CONDA_DEFAULT_ENV"] = envpath.name


def setPackage(globalsdict):
    """Sets the current directory of the notebook as python package to make relative module imports
    work.

    Usage: `setPackage(globals())`
    """
    path = Path().resolve()
    searchpath = str(path.parent)
    if searchpath not in sys.path:
        sys.path.insert(0, searchpath)
    globalsdict["__package__"] = path.name
    globalsdict["__name__"] = path.name
    print(f"Setting the current directory as package '{path.name}': \n  {path}.")
