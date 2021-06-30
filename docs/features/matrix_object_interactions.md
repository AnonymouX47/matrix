# Matrix Object Interactions

The `Matrix` class implements the following python object interactions.

## Intelligent string representation

Calling `str(matrix)` returns a string representation of the matrix.
- The element with the longest string representation in a column determines that column's width.
- All elements are centered in their columns
- No matter how much the matrix and it's elements change, the string is smartly adjusted to give the best representation.
- Calling `print(matrix)` simply writes this string representation to STDOUT.

## Subscription

**Note:**
- Both rows and Columns are **1-indexed** i.e indexing starts from `1`.
- A **slice** always includes the **`stop` index**.

A subscription can be performed on a matrix to get:
1. The element at the given coordinate, if the subscript is a tuple of **integers** `(row, col)`.
   - e.g `matrix[1, 2]`
   - Indices less than 1 are not allowed.
2. a new `Matrix` instance, the **intersection** of the selected rows and columns (called a "block-slice"), if the subscript is a tuple of **slices**.
   - e.g `matrix[::2, 3:4]`
   - the first slice selects rows.
   - the second slice selects columns.
   - any 'stop' greater than the number of rows/columns is "forgiven".
   - Indices or steps less than 1 are not allowed.

These forms of subscription can also be used in an assignment to replace the element or block-slice.
- The value assigned to an element subscription must be a real number.
- While that assigned to a block-slice must be a 2D array (iterable of iterables) of real numbers of the same dimension as the matrix that would normally be returned by the block-slice.

They also support augmented assignments, as supported by the object returned by the form of subscription.

## Truth-value Testing

A matrix has a truth values of `False` is it's a null matrix, and `True` otherwise.
- This property can be used in truth-value testing.

## Membership test for elements

A matrix can be tested if it contains a certain element.

## Iteration over elements

Iterating over a matrix instance yields it's elements in order starting from the first row.
- `iter(matrix)` returns a generator-iterator.
- It raises a `RuntimeError` if the matrix is resized during iteration.
- The generator also has an **advanced** usage. Itcan be set to any vaild row and column of the matrix from which to continue iteration using its `send()` method.
  - It accepts two forms of arguments:
    - An integer, continues yielding fom the start of the specified row.
    - a tuple `(row, col)` of integers; the row and column of the next element to yield.
    - The generator raises a `StopIteration` and closes if given any other type of argument.
  - The `send()` method returns  the element at the specified position, so the next value yielded will be the next element.
  - The generator raises a `StopIteration` and closes if any given index is out of range.

## Per-element rounding

This can be done in two ways:
- Calling `round()` on `Matrix` instances returns a **new instance** with each element rounded as though it were called on each element directly.
- Instance method `round([ndigits])` rounds the matrix **In-place**.

