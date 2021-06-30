# Other operations on matrices

The `Matrix` class implements a few other operations as methods. These operations are performed **in-place** (except the comparison, obviously!):

* `flip_x()` and `flip_y()` -> Horizontal and vertical flip.
* `rotate_right()` and `rotate_left()` -> Clockwise and anti-clockwise rotation.
* `copy()` -> Returns a totally un-linked copy of the matrix.
* `resize(nrow, ncol)` -> Resizes the matrix to a "nrow by ncol" matrix.
  * Pads with zeros when extending the matrix on either or both axes.
* **staticmethod** `compare_rounded(m1, m2, [ndigits])` -> Rounded comparison
  * _ndigits_ is the same as for `round()`.
  * Compares two matrices as if the elements were rounded.
  * Useful for comparing matrices of floating-point elements and is the method recommended for such.

