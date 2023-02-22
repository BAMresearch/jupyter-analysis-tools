# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from os.path import abspath, dirname, join

import toml

base_path = dirname(dirname(abspath(__file__)))
project_meta = toml.load(join(base_path, 'pyproject.toml'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'Jupyter Analysis Tools'
year = '2022'
author = 'Ingo Breßler'
copyright = '{0}, {1}'.format(year, author)
version = '0.1.0'
release = version

autodoc_mock_imports = ["ipykernel", "notebook", "pandas", "ipywidgets"]

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': (join(project_meta['project']['urls']['repository'], 'issues', '%s'), '#%s'),
    'pr': (join(project_meta['project']['urls']['repository'], 'pull', '%s'), 'PR #%s'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'furo'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

linkcheck_ignore = [
    join(
        project_meta['project']['urls']['documentation'],
        project_meta['tool']['coverage']['report']['path'],
    )
    + r'.*',
]
