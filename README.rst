========
Overview
========

Yet another Python library with helpers and utilities for data analysis and processing.

.. start-badges

| |version| |commits-since| |license|
| |build| |supported-versions| |wheel| |downloads|
| |tests| |coverage|
| |docs|

.. |docs| image:: https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/docs.yml/badge.svg
    :target: https://BAMresearch.github.io/jupyter-analysis-tools
    :alt: Documentation Status

.. |build| image:: https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/build.yml/badge.svg
    :target: https://test.pypi.org/project/jupyter-analysis-tools
    :alt: GitHub Actions Build Status

.. |tests| image:: https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/BAMresearch/jupyter-analysis-tools/actions
    :alt: GitHub Actions Tests Status

.. |coverage| image:: https://img.shields.io/endpoint?url=https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/cov.json
    :target: https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/
    :alt: Coverage report

.. |version| image:: https://img.shields.io/pypi/v/jupyter-analysis-tools.svg
    :target: https://test.pypi.org/project/jupyter-analysis-tools
    :alt: PyPI Package latest release

.. |license| image:: https://img.shields.io/pypi/l/jupyter-analysis-tools.svg
    :target: https://en.wikipedia.org/wiki/MIT license
    :alt: License

.. |wheel| image:: https://img.shields.io/pypi/wheel/jupyter-analysis-tools.svg
    :target: https://test.pypi.org/project/jupyter-analysis-tools#files
    :alt: PyPI Wheel

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/jupyter-analysis-tools.svg
    :target: https://test.pypi.org/project/jupyter-analysis-tools
    :alt: Supported versions

.. |commits-since| image:: https://img.shields.io/github/commits-since/BAMresearch/jupyter-analysis-tools/v0.1.2.svg
    :target: https://github.com/BAMresearch/jupyter-analysis-tools/compare/v0.1.2...main
    :alt: Commits since latest release

.. |downloads| image:: https://img.shields.io/pypi/dw/jupyter-analysis-tools.svg
    :target: https://test.pypi.org/project/jupyter-analysis-tools/
    :alt: Weekly PyPI downloads

.. end-badges


Installation
============

::

    pip install jupyter-analysis-tools

You can also install the in-development version with::

    pip install https://github.com/BAMresearch/jupyter-analysis-tools/archive/main.zip


Documentation
=============

https://BAMresearch.github.io/jupyter-analysis-tools

Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
