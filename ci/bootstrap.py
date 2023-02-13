#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess
import sys
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from os.path import relpath

import toml

base_path = dirname(dirname(abspath(__file__)))
templates_path = join(base_path, "ci", "templates")


def check_call(args):
    print("+", *args)
    subprocess.check_call(args)


def exec_in_env():
    env_path = join(base_path, ".tox", "bootstrap")
    if sys.platform == "win32":
        bin_path = join(env_path, "Scripts")
    else:
        bin_path = join(env_path, "bin")
    if not exists(env_path):
        import subprocess

        print("Making bootstrap env in: {0} ...".format(env_path))
        try:
            check_call([sys.executable, "-m", "venv", env_path])
        except subprocess.CalledProcessError:
            try:
                check_call([sys.executable, "-m", "virtualenv", env_path])
            except subprocess.CalledProcessError:
                check_call(["virtualenv", env_path])
        print("Installing `jinja2` into bootstrap environment...")
        check_call([join(bin_path, "pip"), "install", "jinja2", "tox"])
    python_executable = join(bin_path, "python")
    if not os.path.exists(python_executable):
        python_executable += '.exe'

    print("Re-executing with: {0}".format(python_executable))
    print("+ exec", python_executable, __file__, "--no-env")
    os.execv(python_executable, [python_executable, __file__, "--no-env"])


def main():
    import jinja2

    print("Project path: {0}".format(base_path))
    project_meta = toml.load(os.path.join(base_path, 'pyproject.toml'))

    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    tox_environments = [
        line.strip()
        # 'tox' need not be installed globally, but must be importable
        # by the Python that is running this script.
        # This uses sys.executable the same way that the call in
        # cookiecutter-pylibrary/hooks/post_gen_project.py
        # invokes this bootstrap.py itself.
        for line in subprocess.check_output(
            [sys.executable, '-m', 'tox', '--listenvs'], universal_newlines=True
        ).splitlines()
    ]
    tox_environments = [line for line in tox_environments if line.startswith('py')]

    for root, _, files in os.walk(templates_path):
        for name in files:
            if name == ".DS_Store":
                continue
            relative = relpath(root, templates_path)
            with open(join(base_path, relative, name), "w") as fh:
                fh.write(
                    jinja.get_template(join(relative, name)).render(
                        tox_environments=tox_environments,
                        url_docs=project_meta['project']['urls']['documentation'],
                        cov_report_path=project_meta['tool']['coverage']['report']['path'],
                    )
                )
            print("Wrote {}".format(name))
    print("DONE.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--no-env"]:
        main()
    elif not args:
        exec_in_env()
    else:
        print("Unexpected arguments {0}".format(args), file=sys.stderr)
        sys.exit(1)
