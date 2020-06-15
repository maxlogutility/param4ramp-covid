'''
Created on 2020/06/12

@author: rikiya
'''

from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["numpy>=1", "pandas>=1", "scikit-learn>=0.21", "docopt>=0.6"]

setup(
    name="param4ramp-covid",
    version="0.0.1",
    author="Rikiya Takahashi",
    author_email="Rikiya.Takahashi@gmail.com",
    description="Simulation-based Sensitivity Analysis for Contact Tracing Model",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/maxlogutility/param4ramp-covid/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved ::  BSD-2-Clause",
    ],
)