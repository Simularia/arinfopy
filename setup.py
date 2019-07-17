import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="arinfopy",
    version="2.3.3.9999",
    author="Giuseppe Carlino",
    author_email="g.carlino@simularia.it",
    description=("A module to read ADSO/BIN information."),
    long_description=read('README.md'),
    license="GNU GPLv2",
    packages=['.']
)
