# Tests for matrix properties and special matrices

A `Matrix` class provides methods that can be used to check common matrix properties and special matrices:

These methods **never raise errors**, they just return `True` or `False`.

* `is_diagonal()` -> Diagonality
* `is_null()` -> Nullity. Inverse of `bool(matrix)`.
* `is_orthogonal()` -> Orthogonality
* `is_square()` -> Squareness
* `is_symmetric()` -> Symmetry
* `is_skew_symetric()` -> Skew-symmetry
* Triangularity: Implemented as three methods:
  * `is_upper_triangular()`
  * `is_lower_triangular()`
  * `is_triangular()`
* `is_unit()` -> Identity/Unit matrix
* **staticmethod** `is_conformable(m1, m2)` -> Conformability.

