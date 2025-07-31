#!/usr/bin/env python
"""Setup script for ml-pipeline package."""

from setuptools import setup, find_packages

setup(
    name="ml-pipeline",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "scikit-learn>=1.3.0",
        "seaborn>=0.12.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "train-model=training.train:main",
            "deploy-model=scripts.deploy_model:main",
        ],
    },
)