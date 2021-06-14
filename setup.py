from setuptools import setup, find_packages

setup(
    name="matrix",
    version="0.0.1",
    author="AnonymouX47",
    description="A python package for matrix operations and manipulations.",
    url="https://github.com/AnonymouX47/matrix",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(where="."),
    python_requires=">=3.8",
)

