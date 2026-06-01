# setup.py
"""Compatibility shim for legacy `python setup.py ...` workflows.

Project metadata lives in pyproject.toml.
"""

from setuptools import setup


if __name__ == "__main__":
    setup()
