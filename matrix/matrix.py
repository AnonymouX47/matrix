"""Definitions of the various classes."""

import decimal
from math import prod
from multiprocessing import Pool
from operator import add, itemgetter, mul, sub

from .components import *
from . import utils  # Only meant to be used for `ROUND_LIMIT`
from .utils import *

__all__ = ("Matrix", "unit_matrix")

@mangled_attr(_del=False)
class Matrix:
    """
    The main matrix definition.

    The properties here are used to:
    - ensure the "public" attribute is unwritable.
    - provide a means of access to the "private" attribute.

    A matrix can be constructed in two ways:
    - Given two positive integers:
      - `Matrix(rows: int, cols: int)`
      - initializes as a null matrix of the given dimension.

    - Given a 2-D iterable of real numbers:
      - `Matrix(array: iterable, zfill: bool = False)`
      - If all rows have the same length, the matrix is initialized
      taking the array in row-major order.
      - If row lengths don't match but _zfill_ is `True`,
      the rows of the resulting matrix are padded with zeros
      to the right to match up.

    NOTE: All in-place operations guarantee that the outer underlying
    list object will not change in an instance's lifetime, though the nested
    ones will, depending on the operation performed.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ("__array", "__nrow", "__ncol", "__rows", "__columns")


    # Implicit Operations

    def __init__(self, rows_array=None, cols_zfill=None, /):
        """See class Description."""

        if isinstance(rows_array, int) and isinstance(cols_zfill, int):
            rows, cols = rows_array, cols_zfill

            if rows > 0 < cols:
                self.__array = [[Element(0)] * cols for _ in range(rows)]
                self.__nrow, self.__ncol = rows, cols
            else:
                raise InvalidDimension(
                        "Matrix dimensions must be greater than zero.")
        elif is_iterable(rows_array) and isinstance(cols_zfill, (type(None), bool)):
            minlen, maxlen, self.__nrow, array = valid_2D_iterable(rows_array)

            if maxlen == 0:
                raise ValueError("The inner iterables are empty.")

            if minlen == maxlen:
                self.__array = array
                self.__ncol = maxlen
            elif cols_zfill:
                self.__array = array
                self.resize(ncol=maxlen, pad_rows=True)
            else:
                raise ValueError("'zfill' should be `True`"
                                " when the array has variable row lengths.")
        else:
            raise TypeError("Constructor arguments must either be two positive integers"
                            " OR a 2D iterable of real numbers and an optional boolean.")

        self.__rows = Rows(self)
        self.__columns = Columns(self)


    def __repr__(self):

        return (f"<{self.__nrow}x{self.__ncol} "
                f"{type(self).__name__} at {id(self):#x}>")

    def __str__(self):

        # Element with longest str() in a column determines that column's width.

        # Format each element
        rows_strs = [["%.4g" % element for element in row] for row in self.__array]

        # Get lengths of longest formatted strings in each column
        column_widths = [max(map(len, map(itemgetter(i), rows_strs)))
                        for i in range(self.__ncol)]

        # Generate the format_spec for each column
        # specifying the width (plus a padding of 2) and center-align
        fmt_strs = ["^%d" % (width + 2) for width in column_widths]

        # (column widths + one plus and two padding spaces per column - one plus)
        bar = '+' + '\u2015' * (sum(column_widths) + self.__ncol * 3 - 1) + '+'
        mid_bar = ( '|' + '+'.join('\u2015' * (width + 2)
                                    for width in column_widths) + '|')

        return (bar
        + ('\n' + mid_bar).join('\n|' + '|'.join(map(format, row, fmt_strs)) + '|'
                                for row in rows_strs)
        + '\n' + bar)


    def __getitem__(self, sub):
        """
        Returns:
        - element at given position, if `sub` is a tuple of integers `(row, col)`.
          e.g `matrix[1, 2]`
          - Indices must be in range
        - a new Matrix instance, if `sub` is a tuple of slices.
          e.g `matrix[::2, 3:4]`
          - the first slice selects rows.
          - the second slice selects columns.
          - any 'stop' greater than the number of rows/columns is "forgiven".
          - any 'step' less than 1 is not allowed.

        NOTE:
          - Both rows and columns are **indexed starting from `1`**.
          - A **slice includes `stop`**.
        """

        if isinstance(sub, tuple) and len(sub) == 2:

            if all(isinstance(x, int) for x in sub):
                row, col = sub
                if 0 < row <= self.__nrow and 0 < col <= self.__ncol:
                    return self.__array[row - 1][col - 1]
                else:
                    raise IndexError("Row and/or Column index is/are out of range.")

            elif all(isinstance(x, slice) for x in sub):
                row_slice, col_slice = map(adjust_slice, sub, self.size)
                return type(self)(row[col_slice] for row in self.__array[row_slice])

            else:
                raise TypeError(
                        "Matrixes only support subscription of elements or submatrices.")
        else:
            raise TypeError(
                "Subscript element must be a tuple of integers or slices\n"
                "\t(with or without parenthesis).") from None

    def __setitem__(self, sub, value):
        """
        Subscript is interpreted just as for get operation.

        'value' must be:
        - an integer, if 'sub' references an element.
        - a Matrix instance or 2D array of real numbers with appropriate dimensions,
          if 'sub' references a "block-slice".
        """

        if isinstance(sub, tuple) and len(sub) == 2:

            if all(isinstance(x, int) for x in sub):
                row, col = sub
                if 0 < row <= self.__nrow and 0 < col <= self.__ncol:
                    if isinstance(value, (Decimal, Real)):
                        self.__array[row - 1][col - 1] = to_Element(value)
                    else:
                        raise TypeError("Matrix elements can only be real numbers,"
                                f" not {type(value).__name__!r} objects.")
                else:
                    raise IndexError("Row and/or Column index is/are out of range.")

            elif all(isinstance(x, slice) for x in sub):
                row_slice, col_slice = map(adjust_slice, sub, self.size)

                if isinstance(value, __class__):
                    array = value.__array
                    checks = (value.__ncol == slice_length(col_slice)
                                and value.__nrow == slice_length(row_slice)
                                )
                else:
                    minlen, maxlen, nrow, array = valid_2D_iterable(value)
                    checks = (minlen == maxlen
                                and maxlen == slice_length(col_slice)
                                and nrow == slice_length(row_slice)
                                )

                if checks:
                    for row, _row in zip(self.__array[row_slice], array):
                        row[col_slice] = _row
                else:
                    raise ValueError("The array is not of an appropriate dimension"
                                     " for the given block-slice.")
            else:
                raise TypeError(
                    "Matrixes only support subscription of elements or submatrices.")
        else:
            raise TypeError(
                "Subscript element must be a tuple of integers or slices"
                " (with or without parenthesis).") from None


    def __iter__(self):
        """
        Returns a generator that yields the *elements* of the matrix.
        Raises a `RuntimeError` if the matrix is resized during iteration.

        The generator can be set to any vaild row and column of the matrix
        from which to continue iteration using the send() method.

        NOTE:
        1. Recall that the matrix is *1-indexed* when using the send method.
        2. `MatrixIter()` isn't used here:
           - to allow for the advanced usage without extra performance cost.
           - cos it's purpose can simply be achieved thus, with better performace.
        """

        size = self.size  # for comparison during iteration
        r = 0
        while r < self.__nrow:
            c = 0
            row = self.__array[r]
            while c < self.__ncol:
                r_c = (yield row[c])

                if size != self.size:
                    raise RuntimeError(
                                    "The matrix was resized during iteration.",
                                    view_obj=self)

                if r_c is not None:
                    if isinstance(r_c, tuple) and len(r_c) == 2:
                        # It's the only way to prevent a -ve or zero index
                        if not (0 < r_c[0] <= self.__nrow and 0 < r_c[1] <= self.__ncol):
                            return "Coordinate out of range."
                        r, c = r_c[0] - 1, r_c[1] - 2
                        row = self.__array[r]
                    elif isinstance(r_c, int):
                        # It's the only way to prevent a -ve or zero index
                        if r_c < 1:
                            return "Row index out of range."
                        r = r_c - 2
                        break
                    else: return "Wrong type of argument."
                c += 1
            r += 1

    def __contains__(self, item):
        """
        Returns `True` if 'item' is an element in the matrix, otherwise `False`.

        'item' must be an integer.
        """
        
        if not isinstance(item, (Decimal, Real)):
            raise TypeError("Matrix elements are only real numbers.")

        item = to_Element(item)
        return any(item in row for row in self.__array)

    def __round__(self, ndigits=None):
        """Applies the specified rounding to each matrix element."""

        new = __class__(*self.size)
        new.__array = [[round(x, ndigits) for x in row] for row in self.__array]

        return new

    def __pos__(self):
        """Returns an unchanged copy of the matrix."""

        return self.copy()

    def __neg__(self):
        """Returns a copy of the matrix with each element negated."""

        return self.copy() * -1

    def __bool__(self):
        """
        Truthiness of a matrix.

        `False` if the matrix is null, otherwise `True`.
        """

        return not self.is_null()


    ## Matrix operations

    def __eq__(self, other):
        """Matrix Equality"""

        if not isinstance(other, __class__):
            return NotImplemented

        return self.size == other.size and self.__array == other.__array

    def __add__(self, other):
        """
        Matrix Addition.

        Both operands must be matrices and be of the same dimension.
        """

        if not isinstance(other, __class__):
            return NotImplemented

        if self.size != other.size:
            raise InvalidDimension(
                    "The matrices must be of equal size for `+`.",
                    matrices=(self, other)
                    )

        new = __class__(*self.size)
        new.__array = [list(map(add, *pair))
                        for pair in zip(self.__array, other.__array)]

        return new

    def __sub__(self, other):
        """
        Matrix Subtraction.

        Both operands must be matrices and be of the same dimension.
        """

        if not isinstance(other, __class__):
            return NotImplemented

        if self.size != other.size:
            raise InvalidDimension(
                    "The matrices must be of equal size for `-`.",
                    matrices=(self, other)
                    )

        new = __class__(*self.size)
        new.__array = [list(map(sub, *pair))
                        for pair in zip(self.__array, other.__array)]

        return new

    def __mul__(self, other):
        """
        Scalar multiplication.

        'other' must be be a real number.
        """

        if not isinstance(other, (Decimal, Real)):
            return NotImplemented

        new = __class__(*self.size)
        new.__array = [[element * other for element in row] for row in self.__array]

        # Due to floating-point limitations
        new.__round()

        return new

    def __rmul__(self, other):
        """
        Reflected scalar multiplication (to support scalars as left operand).

        'other' must be be a real number.
        """

        return self.__mul__(other)

    def __matmul__(self, other):
        """
        Matrix multiplication.

        'other' must be be a matrix.
        """

        if not isinstance(other, __class__):
            return NotImplemented

        if not self.is_conformable(self, other):
            raise InvalidDimension(
                    "The matrices are not conformable in the given order",
                    matrices=(self, other)
                    )

        new = __class__(self.__nrow, other.__ncol)
        columns = tuple(zip(*other.__array))
        new.__array = [[sum(map(mul, row, col)) for col in columns]
                        for row in self.__array]

        # Due to floating-point limitations
        new.__round()

        return new

    def __truediv__(self, other):
        """
        Division by scalar.

        'other' must be be a real number.
        """

        if not isinstance(other, (Decimal, Real)):
            return NotImplemented

        new = __class__(*self.size)
        new.__array = [[element / other for element in row] for row in self.__array]

        # Due to floating-point limitations
        new.__round()

        return new

    def __pow__(self, exp):
        """Repeated matrix multilication"""

        if not isinstance(exp, int): return NotImplemented

        if 1 > exp != -1: raise ValueError("Matrix exponent can only be -1 or >=1.")

        if exp == -1: return ~self

        new = self.copy()
        # Delibrately didn't use in-place multiplaction or augmented assignment
        for _ in range(exp - 1): new = new.__matmul__(self)

        return new

    def __invert__(self):
        """Matrix Inverse"""

        if self.__nrow != self.__ncol:
            raise InvalidDimension(
                    "This matrix in non-square, hence it's non-invertible.",
                    matrices=(self,)
                    )

        nrow = self.__nrow
        augmented = self | unit_matrix(nrow)
        augmented.reduce_lower_tri()
        try:
            augmented.back_substitution()
        except ZeroDeterminant as err:
            # Shows that the zero determinant is the reason for non-invertibility
            raise ValueError("This matrix is non-invertible.") from err
        inverse = augmented[:, nrow+1:]

        return inverse

    def __or__(self, other):
        """Matrix Augmentation"""

        if not isinstance(other, __class__):
            return Notimplemented
        if self.__nrow != other.__nrow:
            raise InvalidDimension(
                    "The number of rows the matrices must be equal.")

        new = self.copy()
        for row1, row2 in zip(new.__array, other.__array):
            row1.extend(row2)
        new.__ncol += other.__ncol

        return new

    ## In-place Operations
    ##
    ## These ensure the matrix object (and its underlying list object)
    ## remain unchanged.

    def __iadd__(self, other):
        if (result := self.__add__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __isub__(self, other):
        if (result := self.__sub__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __imul__(self, other):
        if (result := self.__mul__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __imatmul__(self, other):
        if (result := self.__matmul__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __itruediv__(self, other):
        if (result := self.__truediv__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __ipow__(self, other):
        if (result := self.__pow__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result

    def __ior__(self, other):
        if (result := self.__or__(other)) is not NotImplemented:
            self.__array[:] = result.__array
            return self

        return result


    # Properties

    _array = property(lambda self: self.__array,
                        doc="Underlying array of the matrix.")

    rows = property(lambda self: self.__rows,
                    doc="Rows() instance of the matrix.")

    columns = property(lambda self: self.__columns,
                        doc="Columns() instance of the matrix.")

    nrow = property(lambda self: self.__nrow,
                    doc="Number of rows of the matrix.")

    ncol = property(lambda self: self.__ncol,
                    doc="Number of columns of the matrix.")

    size = property(lambda self: (self.__nrow, self.__ncol),
                    doc="Dimension of the matrix.")

    trace = property(lambda self: sum(self.diagonal),
                    doc="Trace of the matrix.")

    @property
    def determinant(self):
        """Determinant of the matrix."""

        if self.__nrow != self.__ncol:
            raise InvalidDimension(
                    "This matrix in non-square, hence has no determinant.",
                    matrices=(self,)
                    )

        matrix = self.copy()
        matrix.reduce_lower_tri()

        det = prod([row[i] for i, row in enumerate(matrix.__array)])

        return (Element(round(det))
                if abs(det - round(det)) < Element("1e-12")
                else det)

    @property
    def diagonal(self):
        """Principal diagonal of a square matrix."""

        if self.__nrow != self.__ncol:
            raise InvalidDimension("The matrix is not square.", matrices=(self,))

        return [row[i] for i, row in enumerate(self.__array)]

    @diagonal.setter
    def diagonal(self, value):
        """
        Sets the elements on the principal diagonal of a square matrix
        to the contents of 'value'.
        """

        if self.__nrow != self.__ncol:
            raise InvalidDimension("The matrix is not square.", matrices=(self,))

        value = valid_container(value, self.__nrow)
        for i, row in enumerate(self.__array):
            row[i] = value[i]


    # Explicit Operations

    ## Matrix Operations

    def minor(self, i, j):
        """Returns the minor of element at [i, j]"""

        if self.__nrow != self.__ncol:
            raise InvalidDimension(
                    "This matrix in non-square, hence it's elements have no minors.",
                    matrices=(self,)
                    )

        submatrix = self.copy()
        del submatrix.__rows[i]
        del submatrix.__columns[j]

        return submatrix.determinant

    def transpose(self):
        """Transposes the matrix **in-place**,"""

        self.__array[:] = map(list, zip(*self.__array))
        self.__ncol, self.__nrow = self.size

    def transposed(self):
        """
        Returns the transpose of a matrix (self) as a new matrix
        and leaves the original (self) unchanged.
        """

        new = self.copy()
        new.transpose()

        return new

    def reduce_lower_tri(self):
        """
        Reduces the lower triangle of the matrix.
        Also works on non-square matrices.

        Implements the Forward Elimination step of Gaussian Elimiation.
        Reduces the matrix to row echelon form.
        """

        if self.__ncol >= self.__nrow:
            array = self.__array
            nrow = self.__nrow

            # NOTE: All indices in here are zero-based
            # since the underlying array is being used directly.

            # Any number with a magnitude below 'limit'
            # is considered a zero, due to floating-point limitations
            limit = Element(f"1e-{utils.ROUND_LIMIT}")

            j = 0  # Row currenly being used to reduce those below it.
            # Column of pivot element on row j
            # and of elements being reduced to zero at that step
            k = 0
            while k < nrow and j < nrow-1:
                if abs(array[j][k]) < limit:
                    if not any(array[j][k+1:]):
                        # row j is a zero row, move to the bottom
                        array.insert(nrow, array.pop(j))
                        # In case the row now at j also has a zero at column k
                        continue
                    else:
                        # Find next row below with a non-zero element on column k
                        for i in range(j+1, nrow):
                            if abs(array[i][k]) > limit:
                                # Move row i **above** row j since it has
                                # a non-zero element on that same column j.
                                # There can never exist a row **below** row j
                                # that has a non-zero element **before** column k.
                                array.insert(j, array.pop(i))
                                break
                        else:  # All elements **below** array[j][k] are zeros
                            # Move on to next column, still on the same row j
                            k += 1
                            continue
                # Use row j to reduce those below it,
                # reducing all elements below on column k to zeros
                for i in range(j+1, nrow):
                    # Row operation is redundant if array[i][k] is zero
                    # Also prevents having `-0` elements
                    if abs(array[i][k]) > limit:
                        mult = array[i][k] / array[j][k]
                        array[i] = [x - y*mult for x, y in zip(array[i], array[j])]
                j += 1
                k += 1
        else:
            self.flip_x(); self.flip_y()
            self.reduce_upper_tri()
            self.flip_x(); self.flip_y()

        self.__round()

    def reduce_upper_tri(self, *, as_square=False):
        """
        Reduces the upper triangle of the matrix.
        Also works on non-square matrices.

        Impliments part of Back Substition step of Gaussian Elimination.
        Reduces a matrix to sort of a "transposed row echelon" form.

        Args:
            - as_square -> If true, row reduction is performed as if
            it were a square matrix of the shorter dimension,
            though row operations still affect the  entire row.
            Useful in cases of augmented matrices, for example.
        """

        if self.__nrow >= self.__ncol or as_square:
            array = self.__array
            min_dim = min(self.__nrow, self.__ncol)

            # NOTE: All indices in here are zero-based
            # since the underlying array is being used directly.

            # Any number with a magnitude below 'limit'
            # is considered a zero, due to floating-point limitations
            limit = Element(f"1e-{utils.ROUND_LIMIT}")

            j = min_dim - 1  # Row currenly being used to reduce those above it.
            # Column of "reverse-pivot" element on row j
            # and of elements being reduced to zero at that step
            k = j
            while k >= 0 and j > 0:
                if abs(array[j][k]) < limit:
                    if not any(array[j][:k]):
                        # row j is a zero row, move to the top
                        array.insert(0, array.pop(j))
                        # In case the row now at j also has a zero at column k
                        continue
                    else:
                        # Find next row above with a non-zero element on column k
                        for i in range(j-1, -1, -1):
                            if abs(array[i][k]) > limit:
                                # Move row i **below** row j since it has
                                # a non-zero element on that same column j.
                                # There can never exist a row **above** row j
                                # that has a non-zero element **after** column k.
                                # Note that every row below i (including row j)
                                # would've moved up an index after popping row i.
                                array.insert(j, array.pop(i))
                                break
                        else:  # All elements **above** array[j][k] are zeros
                            # Move on to previous column, still on the same row j
                            k -= 1
                            continue
                # Use row j to reduce those above it,
                # reducing all elements above on column k to zeros
                for i in range(j-1, -1, -1):
                    # Row operation is redundant if array[i][k] is zero
                    # Also prevents having `-0` elements
                    if abs(array[i][k]) > limit:
                        mult = array[i][k] / array[j][k]
                        array[i] = [x - y*mult for x, y in zip(array[i], array[j])]
                j -= 1
                k -= 1
        else:
            self.flip_x(); self.flip_y()
            self.reduce_lower_tri()
            self.flip_x(); self.flip_y()

        self.__round()

    def reduced_row_echelon(self):
        """Transforms the matrix to Reduced Row Echelon form"""

        self.reduce_lower_tri()

        array = self.__array
        for i in range(self.__nrow):
            # Avoids division by zero and redundant division by 1
            if (j := self.rows[i+1].pivot_index) and (pivot := array[i][j-1]) != 1:
                # Prevents having `-0` as elements.
                array[i] = [x / pivot if x else Element(0) for x in array[i]]

    def back_substitution(self):
        """
        Back Substitution step of Gausian Elimination performed **in-place**.
        Leaves the matrix in reduced row echelon form.

        Raises:
            `ValueError` if the lower triangle of the matrix is not "zeroed-out".
            `ZeroDeterminant` if determinant of the matrix is zero.
        """

        if not self.is_upper_triangular(as_square=True):
            raise ValueError(
                    "All elements below the principal diagonal must be zeros"
                    " (Forward Elimination comes before Back Substitution)."
                    )

        array = self.__array

        if not all(row[i] for i, row in enumerate(array)):
            raise ZeroDeterminant(
                        "The determinant of this matrix is zero.",
                        matrix=self
                        ) from None

        self.reduce_upper_tri(as_square=True)

        # Ensures the matrix is in reduced row echelon form.
        # The pivot on each row will be the diagonal element
        # since the matrix is non-singular and already reduced.
        for i in range(self.__nrow):
            # Avoids redundant division by 1.
            if (d_i := array[i][i]) != 1:
                # Prevents having `-0` as elements.
                array[i] = [x / d_i if x else Element(0) for x in array[i]]

        # Due to floating-point limitations
        self.__round()


    ## Other operations

    def round(self, ndigits=None):
        """Rounds the matrix elements in-place"""

        self.__array[:] = [[round(x, ndigits) for x in row] for row in self.__array]

    @staticmethod
    def compare_rounded(mat1, mat2, ndigits=None):
        """
        Comapares two matrices as if the elements were rounded.
        Useful for comparing matrices of floating-point elements
        and is the method recommended for such.

        Args:
            - mat1, mat2 -> subject matrices
            - ndigits -> an integer, the number of decimal places after which any
            difference is irrelevant. Defaults to `ROUND_LIMIT` if not given.
        """

        limit = Element(f"1e-{utils.ROUND_LIMIT}"
                        if ndigits is None
                        else f"1e-{ndigits}"
                        )

        return all(all(abs(x - y) < limit for x, y in zip(row1, row2))
                    for row1, row2 in zip(mat1.__array, mat2.__array)
                    )

    def copy(self):
        """Creates and returns a new copy of a matrix."""

        # Much faster than passing the array to Matrix().
        new = __class__(*self.size)
        new.__array = [row.copy() for row in self.__array]

        return new

    def flip_x(self):
        """Flips the columns of the matrix in-place (i.e horizontally)."""

        for row in self.__array: row.reverse()

    def flip_y(self):
        """Flips the rows of the matrix in-place (i.e vertically)."""

        self.__array.reverse()

    def resize(self, nrow: int = None, ncol: int = None, *, pad_rows=False):
        """
        Resizes the matrix.

        Truncates, if the new dimension is less than the current
        on either or both axes.
        Zero-fills, if the new dimension is greater than the current
        on either or both axes.

        If 'pad_rows' is true, pad each row of the underlying array
        to match up to the given number of columns.
        NOTE: this argument is meant for internal use only.
        """

        if not all(isinstance(x, (type(None), int)) for x in (nrow, ncol)):
            # At least one value given for new dimnsion is of a wrong type.
            raise TypeError("Any specified dimension must be an integer.")

        if any(None is not x < 1 for x in (nrow, ncol)):
            # At least one of the new dimensions given is less than 1.
            raise ValueError("Any specified dimension must be greater than zero.")

        # Number of rows
        if nrow:  # 'nrow' can only be either None or a +ve integer at this point.
            diff = nrow - self.__nrow
            if diff > 0:
                self.__array.extend([[Element(0)] * self.__ncol] * diff)
            elif diff < 0:
                del self.__array[diff:]
            self.__nrow = nrow

        # Number of columns
        if ncol:  # 'ncol' can only be either None or a +ve integer at this point.
            if pad_rows:
                if any(len(row) > ncol for row in self.__array):
                    raise ValueError("Specified number of columns is"
                                     " less than length of longest row.")
                for row in self.__array:
                    row.extend([Element(0)] * (ncol - len(row)))
                self.__ncol = ncol
                return

            diff = ncol - self.__ncol
            if diff > 0:
                for row in self.__array:
                    row.extend([Element(0)] * diff)
            elif diff < 0:
                for row in self.__array: del row[diff:]
            self.__ncol = ncol
        elif pad_rows:
            raise ValueError("Number of columns not specified for padding.")

    def rotate_left(self):
        """Rotate the matrix 90 degrees anti-clockwise."""

        self.transpose()
        self.flip_y()

    def rotate_right(self):
        """Rotate the matrix 90 degrees clockwise."""

        self.transpose()
        self.flip_x()

    def __round(self, ndigits=None):
        """
        Rounds the elements of the matrix that should normally be integers,
        **in-place**.

        Args:
            - ndigits -> The number of decimal places after which
            figures are considered insignifcant. Defaults to `ROUND_LIMIT`.

        NOTE: Meant for internal use only.
        """

        # Did not hard-code this to `ROUND_LIMIT`
        # in case it needs to be used differently.
        limit = Element(f"1e-{utils.ROUND_LIMIT}"
                        if ndigits is None
                        else f"1e-{ndigits}"
                        )
        self.__array[:] = [[Element(round(x))
                                    if abs(x - round(x)) < limit
                                    else x
                                for x in row]
                            for row in self.__array]


    ## Matrix Properties

    def is_diagonal(self):
        """Returns `True` if the matrix is diagonal and `False` otherwise."""

        # `-1` here to avoid `n-1` in the loop condition, two while loops below.
        array, n = self.__array, self.__nrow-1

        if n+1 != self.__ncol: return False  # matrix is not sqaure

        # No zero on principal diagonal
        i = 0
        while i <= n:
            if not array[i][i]: return False
            i += 1

        # All elements off the principal diagonal must be zeros.
        i = 0
        while i < n:
            j = i+1
            while j <= n:
                # Testing diagonally-opposite squares together.
                if array[i][j] or array[j][i]: return False
                j += 1
            i += 1

        return True

    def is_null(self):
        """Returns `True` if the matrix is null and `False` otherwise."""

        return not any(map(any, self.__array))

    def is_orthogonal(self):
        """Returns `True` if the matrix is orthogonal and `False` otherwise."""

        return (m @ m.transposed()).is_unit()

    def is_square(self):
        """Returns `True` if the matrix is square and `False` otherwise."""

        return self.__nrow == self.__ncol

    def is_symmetric(self):
        """Returns `True` if the matrix is symmetric and `False` otherwise."""

        # `-1` here to avoid `n-1` in the loop condition below.
        array, n = self.__array, self.__nrow-1

        if n+1 != self.__ncol: return False  # matrix is not sqaure

        i = 0
        while i < n:
            j = i+1
            while j <= n:
                if array[i][j] != array[j][i]: return False
                j += 1
            i += 1

        return True

    def is_triangular(self):
        """Returns `True` if the matrix is triangular and `False` otherwise."""

        return self.is_upper_triangular() or self.is_upper_triangular()

    def is_unit(self):
        """Returns `True` if a unit matrix and `False` otherwise."""

        if not self.is_diagonal(): return False

        array, n = self.__array, self.__nrow
        i = 0
        while i < n:
            if array[i][i] != 1: return False
            i += 1

        return True

    def is_skew_symmetric(self):
        """Returns `True` if the matrix is skew-symmetric and `False` otherwise."""

        # `-1` here to avoid `n-1` in the loop condition below.
        array, n = self.__array, self.__nrow-1

        if n+1 != self.__ncol: return False  # matrix is not sqaure

        # All zeros on principal diagonal
        i = 0
        while i <= n:
            if array[i][i]: return False
            i += 1

        i = 0
        while i < n:
            j = i+1
            while j <= n:
                if array[i][j] != -array[j][i]: return False
                j += 1
            i += 1

        return True

    def is_lower_triangular(self):
        """Returns `True` if the matrix is lower triangular and `False` otherwise."""

        # `-1` here to avoid `n-1` in the loop condition below.
        array, n = self.__array, self.__nrow-1

        if n+1 != self.__ncol: return False  # matrix is not sqaure

        # All elements **above** the principal diagonal must be zeros.
        i = 0
        while i < n:
            j = i + 1
            while j <= n:
                if array[i][j]: return False
                j += 1
            i += 1

        return True

    def is_upper_triangular(self, *, as_square=False):
        """
        Returns `True` if the matrix is upper triangular and `False` otherwise.
        Args:
            - as_square -> If true, the matrix should be taken as being square.
            Meant for internal use.
        """

        array = self.__array

        # `-1` here is to avoid `n-1` in the loop condition below.
        n = self.__nrow - 1

        if n+1 != self.__ncol:
            if not as_square:
                return False  # matrix is not sqaure and not explicitly allowed

            # Not expecting vertically rectangular matrices but min dimension is
            # used so as to avoid IndexError in case such a matrix is passed in.
            # `-1` here is to avoid `n-1` in the loop condition below.
            n = min(n, self.__ncol - 1)

        # All elements **below** the principal diagonal must be zeros.
        j = 0
        while j < n:
            i = j + 1
            while i <= n:
                if array[i][j]: return False
                i += 1
            j += 1

        return True

    @staticmethod
    def is_conformable(lhs, rhs):
        """
        Returns `True` if matrix 'self' is conformable with 'other',
        otherwise `False`.
        """

        if not isinstance(lhs, __class__):
            raise TypeError("Only matrices can be tested for conformability.")

        return lhs.__ncol == rhs.__nrow


# Register classes that access Matrix attributes with mangled names.
Matrix._register(Rows, Columns)


# Utility functions

def unit_matrix(n: int):
    """
    Creates a nxn unit matrix.

    Args:
        - n -> the size of the square matrix.
    Returns:
        - A nxn unit matrix.
    Raises:
        - `TypeError` -> if n is not an integer.
        - `InvalidDimension` -> if n is less than 1.
    """

    if not isinstance(n, int):
        raise TypeError("Matrix dimension must be an integer.")
    if n < 1:
        raise InvalidDimension("Matrix dimension must be greater than zero.")

    new = Matrix(n, n)
    array = new._array
    for i in range(n):
        array[i][i] = 1

    return new

