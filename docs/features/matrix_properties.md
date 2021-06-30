# Matrix Properties

The `Matrix` class provides the common matrix properties as object attributes:
- `nrow` -> Number of rows
- `ncol` -> Number of columns
- `size` -> Matrix size or dimension, as a tuple `(nrow, ncol)`.
- `determinant` -> Determinant
  - Raises an error for non-square matrices.
- `diagonal` -> Returns principal diagonal elements, as a list.
  - Raises an error for non-square matrices.
  - Setting this attribute modifies the matrix i.e sets the diagonal elements.
- `trace` -> Trace of the matrix
  - Raises an error for non-square matrices.
- `rank` -> Rank of the matrix

