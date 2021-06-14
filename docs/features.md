# Features

## Table of Contents

[TOC]



An instance of `Matrix` is a **mutable** object modelling a mathematical matrix. It implements common matrix operations and properties and is completely **1-indexed**.

Even though it's mutable, it provides a few methods that return a new matrix instance.

For demonstrations of the features described here, see the [sample files](../samples/).

## Matrix Initialization

This can be done in two major ways:

### Via the class constructor

The Matrix class constructor accepts two forms of arguments:

1. Given two positive integers; the number of rows and columns respectively.

   - `Matrix(rows, cols)`

       - initializes as a null matrix of the given dimension.

2. Given a 2-D iterable of real numbers.

   - `Matrix(array, zfill=False)`

   - If all rows have the same length, the matrix is initialized taking the array in row-major order.

   - If row lengths don't match but _zfill_ is `True`, the rows of the resulting matrix are padded with zeros to the right to match up.

**NOTE:** The constructor arguments can only be passed positionally, not by name.

### Using the provided utility functions

The library provided the following functions at the top level for generating matrix instances:

1. `unit_matrix(n)`
   - Returns a "n by n" unit matrix.
2. `randint_matrix(nrow, ncol, _range)`
   - Returns a matrix with random integer elements where the third argument '_range' should be a `range` instance representing the range of integers from which the random elements are to be selected.
   - All arguments must be positional.
3. `random_matrix(nrow, ncol, start, stop)`
   - Returns a matrix with random floating-point elements where:
     - _start_ is the minimum value of an element.
     - _stop_ is the maximum value of an element.
   - All arguments must be positional.

## Matrix object interactions

The `Matrix` class implements the following python object interactions.

### Intelligent string representation

Calling `str(matrix)` returns a string representation of the matrix.

- The element with longest string representation in a column determines that column's width.
- No matter how much the matrix and it's elements change, the string is smartly adjusted to give the best representation.
- Calling `print(matrix)` simply writes this string representation to STDOUT.

### Subscription

A subscription can be performed on a matrix in get:

1. The element at the given coordinate, if the subscript is a tuple of **integers** `(row, col)`.
   - e.g `matrix[1, 2]`
   - Indices less than 1 are not allowed.

2. a new `Matrix` instance made up of the selected rows and columns (called a "block-slice"), if the subscript is a tuple of **slices**.

   - e.g `matrix[::2, 3:4]`

   - the first slice selects rows.
   - the second slice selects columns.
   - any 'stop' out of range is "forgiven".
   - Indices or steps less than 1 are not allowed.

These forms of subscription can also be used in an assignment to replace the element or block-slice.

- The value assigned to an element subscription must be a real number.
- While that assigned to a block-slice must be a 2D array (iterable of iterables) of real numbers of that same dimension.

They also support augmented assignments, as supported by the object returned by the form of subscription.

**Note:**

- Both rows and Columns are **indexed starting from `1`**.
- A **slice includes `stop`**.

### Truth Value

A matrix has a truth values of `False` is it's a null matrix, and `True` otherwise.

- This property can be used in truth-value testing.

### Membership test for elements

A matrix can be tested if it contains a certain element.

### Iteration over elements

Iterating over a matrix instance yields it's elements in order starting from the first row.

- `iter(matrix)` returns a generator.
- The generator can be set to any vaild row and column of the matrix from which to continue iteration using its `.send()` method.

### Per-element rounding

Calling `round()` on `Matrix` instances rounds each element as though it were called on each element directly.

## Matrix object properties

The `Matrix` class provides the common matrix properties as object attributes:

- `nrow` -> Number of rows
* `ncol` -> Number of columns
- `size` -> Matrix size or dimension as a tuple `(nrow, ncol)`.
- `determinant` -> Determinant
  - Raises an error for non-square matrices.
- `diagonal` -> Principal diagonal elements as a list.
  - Raises an error for non-square matrices.
- `trace` -> Trace of the matrix
  - Raises an error for non-square matrices.

## Matrix Operations

The `Matrix` class implements the following matrix operations. The same rules as in mathematics apply.

All these operations return a new `Matrix` instance except stated otherwise.

### Via unary operators

- Negation: `-m`
- Inverse: `~m

### Via binary operators

* Equality comparison: `m1 == m2`
* Addition: `m1 + m2`
* Subtraction: `m1 - m2`
* Scalar multiplication: `m * c` or `c * m`
* Matrix multiplication: `m1 @ m2`
* Division (by scalar): `m / c`
* Augmentation: `m1 | m2`

### Via explicit methods

- Transpose: This is implemented by two methods:
  - `transpose()` -> Returns a transposed copy.
  - `itranspose()`  -> Transposes the matrix **in-place**.
- Row reduction (**In-place**): Implemented as instance mathods:
  - `reduce_lower_tri()`  -> Reduces all elements in the lower triangle to zeros.
  - `reduce_upper_tri()`  -> Reduces all elements in the upper triangle to zeros.

## Tests for matrix properties and special matrices

A `Matrix` class provides methods that can be used to check common matrix properties and special matrices:

* `is_diagonal()` -> Diagonality
* `is_null()` -> Nullity. Inverse of `bool(matrix)`.
* `is_orthogonal()` -> Orthogonality
* `is_square()` -> Squareness
* `is_symmetry()` -> Symmetry
* Triangularity: Implemented as three methods:
  * `is_upper_triangular()`
  * `is_lower_triangular()`
  * `is_triangular()`
* `is_unit()` -> Identity/Unit matrix
* **staticmethod** `is_conformable(m1, m2)` -> Conformability.

## Matrix views

These are views of the matrix object (i.e they don't replicate the matrix data), kinda like how `.keys()` and `.values()` are to `dict`.

Note that these objects "expire" (become invalid) if the matrix is resized i.e if you create a matrix view object and then resize the matrix by any means, the previously created matrix view object becomes invalid and any operation on it raises an error.

### `Rows`, `Columns` `RowsSlice`, `ColumnsSlice` instances.

These objects provide a view over multiple rows or columns of a matrix.

- `Rows` and `Columns` instances cover all rows and columns respectively. 
  - They can be retrieved using the matrix attributes `rows` and `columns` respectively.
  - Every matrix has only one each of these instances.
- `RowsSlice` and `ColumnsSlice` instances cover a slice (selection) of the rows or columns respectively.
  - They can be gotten by slicing the `Rows` or `Columns` instance of a matrix.

These objects support the following operations:

- Subscription
  - Single row/column Indexing.
  - Slicing of multiple rows/columns (Yes, a slice of rows/columns can still be sliced further! :sunglasses:)
  * A slice of a `RowsSlice` instance returns another `RowsSlice` instance that is a view over the matrix rows selected from the former slice.
- Row/column assignment and deletion (`RowsSlice` and  `ColumnsSlice` **DO NOT** support these).
  - Deleting a row/column changes the size of the matrix.
- Length (number of rows/columns "in" the view) via `len()`.
- Iteration through rows/columns.

### `Row` and `Column` instances

These objects provide a view over a single row or column of a matrix.

- They can be gotten by indexing a `Rows`, `Columns`, `RowsSlice`, or `ColumnsSlice` instance of a matrix.

They support the following operations:

* String representation
* Single element indexing
* Multiple element slicing (returns a list)
* Equality comparison
* Mathematical operations (Also supports augmented assignment of these operations):
  * Addition and subtraction of rows and/or columns (Element-wise)
  * Multiplication and Division by scalar
  * Multiplication and Division by row/column (i.e inter-operation of two rows/columns element-by-element)
* Row/column length with `len()`
* Membership tests
* Iteration through elements
* Pivot index (**`Row` only**): implemented as instance method `pivot_index()`; returns the index of the leading non-zero element.

**NOTE** on Row/Column mathematical operations:

* Each binary operation returns a **list** containing the result of the operation.
* Augmented assignments counterparts of these operations perform **in-place** operations i.e affect the matrix itself.
* Due to this difference,  if `row = m.rows[1]`, then `row += row` is very different from `row = row + row`.
  * In the former, the corresponding row (row 1) of the matrix _m_ is modified and _row_ references a **`Row`** instance after the operation.
  * While in the latter, the matrix row remains unchanged and _row_ references a **`list`** instance after the operation.

## Other operations on matrices

The `Matrix` class implements a few other operations as methods. These operations are performed **in-place** (except the comparison, obviously!):

* `flip_x()` and `flip_y()` -> Horizontal and vertical flip.
* `rotate_right()` and `rotate_left()` -> Clockwise and anti-clockwise rotation.
* `copy()` -> Returns a totally un-linked copy of the matrix.
* `resize(nrow, ncol)` -> Resizes the matrix to a "nrow by ncol" matrix.
  * Pads with zeros when extending the matrix on either or both axes.
* **staticmethod** `compare_rounded(m1, m2, [ndigits])` -> Rounded comparison
  * _ndigits_ is the same as for `round()`.
  * Comapares two matrices as if the elements were rounded.
  * Useful for comparing matrices of floating-point elements and is the method recommended for such.

