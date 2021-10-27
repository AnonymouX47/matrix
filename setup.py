from setuptools import setup, find_packages
from matrix.__version__ import version

with open("README.md") as f:
    long_desc = f.read()

setup(
    name="matrix-47",
    version=version,
    author="AnonymouX47",
    author_email="feyidab01@gmail.com",
    description="A python package for matrix operations and manipulations.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/AnonymouX47/matrix",
    license="GPLv3.0",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    packages=find_packages("."),
    python_requires=">=3.8",
)
