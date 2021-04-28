# matrix

A python library for matrix operations and manipulations.

## Contents

* [Back-Story](#back-story)
* [Features](#features)
* [Usage](#usage)
* [TODO](#todo)

## Back-Story

I had just completed my "Journey through the Docs", finished studying the Python aspect of the Python Docs (majorly the Library & Language Reference, wherever else those referred me to and whatever else i needed to fully understand) with interactive sessions, testing things out.

Then i needed something to put to (real) practice all the things i had learned.
I wanted something purely **Standard** Python, no 3rd-party libraries and seemed this project would be a good place to start.

The project was actually concieved in the course of my "Journey through the Docs" but only stayed on my TODO list till after.

It's been interesting so far and the project actually turned out to incoparate a lot of what i learned... though, definitely not close to all. :smile:

**NOTE:** This project is not intended to be a "re-invention of any wheel", it's basically just me practicing.
I actually made sure i didn't test out or go through any other similar project, at least, till i had implemented all I originally planned to.

## Features

This is just an highlight of the major features of the library. For detailed explanation of the features, see the [documentation](docs/index.md).

* Matrix initialization via:
  * Class constructor
  * ...
* Matrix object interactions
  * Subscription
    * Single-element indexing, assignment and deletion
    * Block-slice (sub-matrix) subscription and assignment.
  * Truthiness
  * Iteration over elements
* Matrix properties
  * Size
  * Number of rows
  * Number of columns
  * Determinant
* Matrix views (These are views of the matrix object, like `.keys()` or `.values()` are to `dict`.)
  * Rows and Columns (and their slices). Support:
    * Single row/column Indexing
    * Slicing of multiple rows/columns (Yes, a slice of rows/columns can still be sliced further! :sunglasses:)
    * Row/column assignment and deletion
    * Iteration over rows/columns
  * Row and column. Support:
    * Single element indexing
    * Multiple element slicing

## Usage

...

## TODO

1. Solution to systems of linear equations (Coming up soon).
2. Reshaping matrices.
3. Flipping and rotating matrices.
4. Creating pre-filled matrices with ones, random numbers (integers or floats), optionally within a specified range, diagonal matrices, etc...
5. Initializing matrices from STDIN or files.
6. Implementation of methods to find eigenvalues and eigenvectors.
   * This requires a polynomial "solver" (at least for the basic approach) and I plan to work on that.
7. Probably Others...

Please note that I **do NOT** plan to implement any "more efficient" algorithms for the matrix operations in this project. It's not the point of this project (at least, as of now).