# -*- coding: utf-8 -*-
# tests/jupyter.py

import os
from pathlib import Path

from jupyter_analysis_tools.jupyter import addEnvScriptsToPATH as jupyter_addEnvScriptsToPATH
from jupyter_analysis_tools.jupyter import ensureMiniforgeInPATH
from jupyter_analysis_tools.jupyter import setLocaleUTF8 as jupyter_setLocaleUTF8
from jupyter_analysis_tools.jupyter import setPackage as jupyter_setPackage


def test_jupyter_helpers_are_exposed_from_jupyter_module():
    assert callable(jupyter_setLocaleUTF8)
    assert callable(jupyter_addEnvScriptsToPATH)
    assert callable(jupyter_setPackage)


def test_ensureMiniforgeInPATH(monkeypatch):
    original_path = os.environ.get("PATH", "")
    original_prefix = os.environ.get("CONDA_PREFIX")
    original_default = os.environ.get("CONDA_DEFAULT_ENV")

    fake_env = Path(r"C:\Users\me\miniforge3\envs\myenv")
    fake_python = fake_env / "python.exe"
    fake_path = r"C:\Windows\System32;C:\Windows"

    monkeypatch.setattr("jupyter_analysis_tools.jupyter.isWindows", lambda: True)
    monkeypatch.setattr("jupyter_analysis_tools.jupyter.sys.executable", str(fake_python))
    os.environ["PATH"] = fake_path

    ensureMiniforgeInPATH()

    assert os.environ["CONDA_PREFIX"] == str(fake_env)
    assert os.environ["CONDA_DEFAULT_ENV"] == fake_env.name
    paths = os.environ["PATH"].split(";")
    assert str(fake_env) == paths[0]
    assert str(fake_env / "Library/mingw-w64/bin") == paths[1]
    assert str(fake_env / "Library/usr/bin") == paths[2]
    assert str(fake_env / "Library/bin") == paths[3]
    assert str(fake_env / "Scripts") == paths[4]
    assert str(fake_env / "bin") == paths[5]
    assert str(fake_env.parent.parent / "condabin") == paths[6]
    assert fake_path == ";".join(paths[7:])

    os.environ["PATH"] = original_path
    if original_prefix is None:
        os.environ.pop("CONDA_PREFIX", None)
    else:
        os.environ["CONDA_PREFIX"] = original_prefix
    if original_default is None:
        os.environ.pop("CONDA_DEFAULT_ENV", None)
    else:
        os.environ["CONDA_DEFAULT_ENV"] = original_default
