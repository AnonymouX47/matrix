# Matrix views

These are views of the matrix object (i.e they don't replicate the matrix data), kinda like how `.keys()` and `.values()` are to `dict`.

Note that these objects "expire" (become invalid) if the matrix is resized i.e if you create a matrix view object and then resize the matrix by any means, the previously created matrix view object becomes invalid and any operation on it raises an error.

## `Rows`, `Columns` `RowsSlice`, `ColumnsSlice` instances.

These objects provide a view over multiple rows or columns of a matrix.

- `Rows` and `Columns` instances cover all rows and columns respectively. 
  - They can be retrieved using the matrix attributes `rows` and `columns` respectively.
  - Every matrix has only one each of these instances.
- `RowsSlice` and `ColumnsSlice` instances cover a slice (selection) of the rows or columns respectively.
  - They can be gotten by slicing the `Rows` or `Columns` instance of a matrix.

These objects support the following operations:
- Subscription
  - Single row/column Indexing.
  - Slicing.
    - A slice of a `RowsSlice` instance returns another `RowsSlice` instance that is a view over the matrix rows selected from the former slice. Similarly for `ColumnSlice`.
- Row/column assignment and deletion (`RowsSlice` and  `ColumnsSlice` **DO NOT** support these yet).
  - Can only modify single rows, not a slice of rows but can delete a slice of rows.
  - Assigned object can be any iterable of real numbers.
  - Augmented assigment counterparts of operations supported by `Row` and `Column` also work and update the row/column of the matrix.
  - Deleting a row/column changes the size of the matrix.
  - Emptying a matrix is not allowed.
- Length (number of rows/columns "in" the view) via `len()`.
- Iteration through rows/columns.

## `Row` and `Column` instances

These objects provide a view over a single row or column of a matrix.
- They can be gotten by indexing a `Rows`, `Columns`, `RowsSlice`, or `ColumnsSlice` instance of a matrix.

They support the following operations:

* String representation
* Subscription
  * Single element indexing
  * Multiple element slicing (returns a list)
  * The subscriptions can also be assignment targets to change the element or elements of the matrix.
  * Also, augmented assignment counterparts of operators supported by the matrix elements, update the elements of the matrix.
  * Augmented assignments won't work with Row/Column **slices** due to the fact that they return `list` objects.
  * Elements cannot be deleted.
* Equality comparison
* Arithmetic operations (Also supports augmented assignment counterparts of these operations):
  * Addition and subtraction of rows and/or columns (Element-wise)
  * Multiplication and Division by scalar
  * Multiplication and Division by row/column (i.e inter-operation of two rows/columns element-by-element)
* Row/column length with `len()`
* Membership tests
* Iteration through elements

`Row` objects have one property:

* `pivot_index` -> Pivot index.
  * gets the **1-based** index of the **leading non-zero** (pivot) element on that row.
  * returns `0` (zero) for a zero-row.

**NOTE** on Row/Column **arithmetic operations**:
* Each binary operation returns a **list** containing the result of the operation.
* Augmented assignments counterparts of these operations perform **in-place** operations i.e affect the matrix itself.
* Due to this difference,  if `row = m.rows[1]`, then `row += row` is very different from `row = row + row`.
  * In the former, the corresponding row (row 1) of the matrix _m_ is modified and _row_ references a **`Row`** instance after the operation.
  * While in the latter, the matrix row remains unchanged and _row_ references a **`list`** instance after the operation.
  * The only exception to this behaviour is when using subscripts of the `Rows` or `Columns` instance directly e.g `m.rows[1] = m.rows[1] * 2` is equivalent to `m.rows[1] *= 2`, in terms of end results.
  * Same applies to `Column`.

