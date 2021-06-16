from setuptools import setup

with open('README.md') as f:
    long_desc = f.read()

setup(
    name="matrix",
    version="0.0.1",
    author="AnonymouX47",
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    packages=["matrix"],
    python_requires=">=3.8",
)

