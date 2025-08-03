#!/usr/bin/env python
"""Setup script for ml-pipeline package."""

import os
import sys
from setuptools import setup, find_packages

# Add src to path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from __init__ import __version__

setup(
    name="ml-pipeline",
    version=__version__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "scikit-learn>=1.3.0",
        "seaborn>=0.12.0",
        "requests>=2.31.0",
        "boto3>=1.26.0",
        "pandas>=1.5.0",
    ],

)