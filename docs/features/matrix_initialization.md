# Matrix Initialization

This can be done in two major ways:

## Via the class constructor

The Matrix class constructor accepts two forms of arguments:

1. Given two positive integers; the number of rows and columns respectively.
   - `Matrix(rows, cols)`
   - initializes as a null matrix of the given dimension.
2. Given a 2-D iterable of real numbers.
   - `Matrix(array, zfill=False)`
   - If all rows have the same length, the matrix is initialized taking the array in row-major order.
   - If row lengths don't match but _zfill_ is `True`, the rows of the resulting matrix are padded with zeros to the right to match up.

**NOTE:** The constructor arguments can only be passed positionally, not by keyword.

## Using the provided utility functions

The library provided the following functions at the top level for generating matrix instances:
1. `unit_matrix(n)`
   - Returns a "n by n" unit matrix.
2. `randint_matrix(nrow, ncol, _range)`
   - Returns a matrix with random integer elements where the third argument (_\_range_) should be a `range` instance representing the range of integers from which the random elements are to be selected.
   - All arguments must be positional.
3. `random_matrix(nrow, ncol, start, stop)`
   - Returns a matrix with random floating-point elements where:
     - _start_ is the minimum value of an element.
     - _stop_ is the maximum value of an element.
   - All arguments must be positional.

