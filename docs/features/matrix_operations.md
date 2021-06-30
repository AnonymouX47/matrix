# Matrix Operations

The `Matrix` class implements the following matrix operations. The same rules as in mathematics apply.

All these operations return a new `Matrix` instance except stated otherwise.

## Via unary operators

- Negation: `-m`
- Inverse: `~m`

## Via binary operators

* Equality comparison: `m1 == m2`
* Addition: `m1 + m2`
* Subtraction: `m1 - m2`
* Scalar multiplication: `m * c` or `c * m`
* Exponentiation (Repeated matrix multiplication): `m ** c`
* Matrix multiplication: `m1 @ m2`
* Division (by scalar): `m / c`
* Augmentation: `m1 | m2`

where _m_ is a matrix and _c_ is a real number.

The augmented assignment counterparts of these binary operators are also supported and perform the operations **in-place** i.e the matrix object remains unchanged.

## Via explicit methods

- Transpose: This is implemented by two methods:
  - `transposed()` -> Returns a transposed copy.
  - `transpose()`  -> Transposes the matrix **in-place**.
- Row reduction (all **In-place**): Implemented as instance methods:
  - `to_upper_triangular()`  -> Reduces a **square** matrix to an upper-triangular matrix.
  - `to_lower_triangular()`  -> Reduces a **square** matrix to a lower-triangular matrix.
  - `to_row_echelon()` -> Transforms the matrix to _row echelon_ form.
  - `to_reduced_row_echelon()` -> Transforms the matrix to _reduced row echelon_ form.
  - **Note:** The last two work on matrices of any shape.
- `forward_eliminate()` -> Performs _forward elimination_ on an **horizontal** matrix, **in-place**.
- `back_substitute()` -> Performs _back substitution_ on an **horizontal** matrix, **in-place**.
  - This operation **requires** that _forward elimination_ must've been performed on the matrix.

