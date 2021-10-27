# matrix

```
              __      _
  __ _  ___ _/ /_____(_)_ __
 /  ' \/ _ `/ __/ __/ /\ \ /
/_/_/_/\_,_/\__/_/ /_//_\_\

```

A python package for matrix operations and manipulations.

## Contents

* [Back-Story](#back-story)
* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Uninstallation](#uninstallation)
* [Contributing](#contributing)

## Back-Story

I had just completed my "Journey through the Docs", studying the Core Python aspect of the Python Docs (majorly the Library & Language References, wherever else those referred me to and whatever else I needed to fully understand things) with interactive sessions, testing things out and making notes.

Then I needed something to put to (real) practice all the things I had learned.
I wanted something purely **Standard** Python, no 3rd-party libraries and seemed this project would be a good place to start.

The project was actually concieved in the course of my "Journey through the Docs" but only stayed on my TODO list till after.

It's been interesting so far and the project actually turned out to incoparate a lot of what I learned... though, definitely not all. :smile:

**NOTE:** This project is not intended to be a "re-invention of any wheel", it's just me practicing.
I actually didn't test out or go through any similar project in the course of developing this.

## Features

This is just an outline of the major features of the library. For the complete feature list, detailed descriptions and project documentation, see the [documentation](https://anonymoux47.github.io/matrix/).

### Matrix initialization. Via:
* The class constructor
* Utility functions to generate:
  * Unit matrices.
  * Matrices filled with random integer elements.
  * Matrices filled with random floating-point elements.

### Matrix object interactions
* Intelligent string representation
* Subscription
  * Single-element indexing, assignment and deletion
  * Block-slice (sub-matrix) subscription and assignment.
* Truthiness
* Membership test for elements
* Iteration over elements
* Per-element rounding

### Matrix object properties
* Size
* Number of rows
* Number of columns
* Determinant
* Principal diagonal
* Trace
* Rank

### Matrix Operations
* Negation
* Equality comparison
* Addition and subtraction
* Scalar multiplication
* Matrix multiplication
* Exponentiation (Repeated matrix multiplication)
* Division (by scalar)
* Inverse
* Transpose
* Augmentation
* Row reduction
  * Row Echelon form (Forward elimination)
  * Reduced Row Echelon form
  * Back substitution

### Tests for matrix properties and special matrices
* Diagonality
* Nullity
* Orthogonality
* Squareness
* Symmetry
* Triangularity
* Identity matrix
* Conformability

### Matrix views
These are views of the matrix object, like `.keys()` and `.values()` are to `dict`.

* Rows and Columns (and their slices). Support:
  * Single row/column Indexing
  * Slicing of multiple rows/columns (Yes, a slice of rows/columns can still be sliced further! :sunglasses:)
  * Row/column assignment and deletion (Rows/Columns slices **DO NOT** support these).
  * Length (number of rows/columns "in" the view)
  * Iteration over rows/columns
* Row and column. Support:
  * String representation
  * Single element indexing
  * Multiple element slicing
  * Equality comparison
  * Mathematical operations (Also supports augmented assignment of these operations):
    * Addition and subtraction of rows and/or columns (Element-wise)
    * Multiplication and Division by scalar
    * Multiplication and Division by row/column (i.e inter-operation of two rows/columns element-by-element)
    * **NOTE:** Augmented assignments of these operations are performed **in-place** i.e affect the matrix itself.
  * Row/column length
  * Membership tests
  * Iteration over elements

### Other operations on matrices
* Horizontal and vertical flip
* Clockwise and anti-clockwise rotation
* Matrix copy
* Matrix resize
* Rounded comparison

### Solutions to systems of linear equations
* Gaussian elimination
* Gauss-Jordan elimination
* Inverse method


## Installation

### Requirements
- Python >= 3.8

### Install from PyPI
NOTE: You must have the `pip` python package installed (usually is, by default)

Run
```sh
pip install matrix-47
```
OR
```sh
python -m pip install matrix-47
```

### Install from source
Download and unzip [this repository](https://github.com/AnonymouX47/matrix/archive/refs/heads/main.zip) or run
```sh
git clone https://github.com/AnonymouX47/matrix
```

Change your Working Directory to the local repository; run
```sh
cd matrix
```

Then, run
```sh
pip install .

```

* * *

Instead, you might run
```sh
python -i test.py
```
to just test out the library without installing the package (but will be limited to only that interactive session).

**NOTE:** On Windows, the Python executables must've been added to `PATH` (For help, check [here](https://datatofish.com/add-python-to-windows-path/)).


## Usage

Quick example:
```python
>>> from matrix import Matrix
>>> print(Matrix(4, 4))
+―――――――――――――――+
| 0 | 0 | 0 | 0 |
|―――+―――+―――+―――|
| 0 | 0 | 0 | 0 |
|―――+―――+―――+―――|
| 0 | 0 | 0 | 0 |
|―――+―――+―――+―――|
| 0 | 0 | 0 | 0 |
+―――――――――――――――+
```

For more usage examples, check the [samples](https://github.com/AnonymouX47/matrix/tree/main/samples).

For the complete feature list and descriptions, see [Feature Description](https://anonymoux47.github.io/matrix/features/).


## Uninstallation

To uninstall the package, run
```sh
pip uninstall matrix-47
```


## Contributing

If you find any bug, please create an **Issue** in the [Issues section](https://github.com/AnonymouX47/matrix/issues).
Please make sure you check other issues first, to make sure you don't create a duplicate. Thank you :smiley:

