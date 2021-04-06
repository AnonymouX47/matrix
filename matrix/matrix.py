"""Definitions of the various classes."""

from operator import add, itemgetter, sub

from .components import *
from .utils import *

__all__ = ("Matrix",)

@mangled_attr(_del=False)
class Matrix:
    """
    The main matrix definition.

    The properties here are used to:
    - ensure the "public" attribute is unwritable.
    - provide a means of access to the "private" attribute.

    A matrix can be constructed in two ways:
    - Given two positive integers:
      `Matrix(rows: int, cols: int)`
      - initializes as a zero matrix of that dimension.

    - Given a 2-D iterable of real numbers:
      `Matrix(array: iterable, zfill: bool = False)`
      - If all rows have the same length, initialized as if the array is row-major.
      - If row lengths don't match but `zfill is True`, zero-fill to the right to match.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ("__array", "__nrow", "__ncol", "__rows", "__columns")


    # Implicit Operations

    def __init__(self, rows_array=None, cols_zfill=None):
        """See class Description."""

        if isinstance(rows_array, int) and isinstance(cols_zfill, int):
            rows, cols = rows_array, cols_zfill

            if rows > 0 and cols > 0:
                self.__array = [[Element(0)] * cols for _ in range(rows)]
                self.__nrow, self.__ncol = rows, cols
            else:
                raise ValueError("Both dimensions must be positive integers.")
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
        return f"<{type(self).__name__}{self.size} at {id(self):#x}>"

    def __str__(self):
        """
        Element with longest str() in a column determines that column's width.
        """

        # Format each element
        rows_strs = [["%.4g" % element for element in row] for row in self.__array]

        # Get lengths of longest formatted strings in each column
        column_widths = [max(map(len, map(itemgetter(i), rows_strs)))
                        for i in range(self.__ncol)]

        # Generate the format_spec for each column
        # specifying the width (plus a padding of 2) and center-align
        fmt_strs = ["^%d" % (width + 2) for width in column_widths]

        bar = '\u2015' * (sum(column_widths) + self.__ncol * 3  + 1)

        return (bar
            + ('\n' + bar).join('\n|' + '|'.join(map(format, row, fmt_strs)) + '|'
                                for row in rows_strs)
            + '\n' + bar)


    def __getitem__(self, sub):
        """
        Returns:
        - element at given position, if `sub` is a tuple of integers `(row, col)`.
          e.g `matrix[1, 2]`
          - Indices must be in range
          - Negative indices are not allowed.
        - a new Matrix instance, if `sub` is a tuple of slices.
          e.g `matrix[::2, 3:4]`
          - the first slice selects rows.
          - the second slice selects columns.
          - any 'stop' out of range is "forgiven".
          - Negative indices or steps are not allowed.

        NOTE:
          - Both Row and Column are **indexed starting from `1`**.
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
                    checks = (value.__ncol == col_slice.stop - col_slice.start
                              and value.__nrow == row_slice.stop - row_slice.start)
                else:
                    minlen, maxlen, nrow, array = valid_2D_iterable(value)
                    checks = (minlen == maxlen
                              and maxlen == col_slice.stop - col_slice.start
                              and nrow == row_slice.stop - row_slice.start)

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
                "Subscript element must be a tuple of integers or slices\n"
                "\t(with or without parenthesis).") from None


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
                    raise  MatrixResizeError("The matrix was resized during iteration.")

                if r_c:
                    if isinstance(r_c, tuple) and len(r_c) == 2:
                        r, c = r_c[0] - 1, r_c[1] - 2
                        row = self.__array[r]
                    elif isinstance(r_c, int):
                        r = r_c - 2
                        break
                c += 1
            r += 1

    def __contains__(self, item):
        """
        Returns `True` if 'item' is an element in the matrix, otherwise `False`.

        'item' must be an integer.
        """
        
        if not isinstance(item, (Decimal, Real)):
            raise TypeError("Matrix elements are only real numbers.")

        return any(item in row for row in self.__array)


    ## Matrix operations

    def __add__(self, other):
        """
        Matrix Addition.

        Both operands must be matrices and be of the same dimension.
        """

        if not isinstance(other, __class__):
            return NotImplemented

        if self.size != other.size:
            raise ValueError("The matrices must be of equal size for `+`.")

        new = __class__(*self.size)
        new.__array = [list(map(add, *pair)) for pair in zip(self.__array, other.__array)]

        return new

    def __sub__(self, other):
        """
        Matrix Subtraction.

        Both operands must be matrices and be of the same dimension.
        """

        if not isinstance(other, __class__):
            return NotImplemented

        if self.size != other.size:
            raise ValueError("The matrices must be of equal size for `-`.")

        new = __class__(*self.size)
        new.__array = [list(map(sub, *pair)) for pair in zip(self.__array, other.__array)]

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

        new = __class__(*self.size)
        raise NotImplementedError("Coming Soon...")

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

        return new


    # Properties

    _array = property(lambda self: self.__array,
                        doc="Gets underlying array of the matrix.")

    rows = property(lambda self: self.__rows,
                    doc="Gets Rows() instance of the matrix.")

    columns = property(lambda self: self.__columns,
                        doc="Gets Columns() instance of the matrix.")

    nrow = property(lambda self: self.__nrow,
                    doc="Gets number of rows of the matrix.")

    ncol = property(lambda self: self.__ncol,
                    doc="Gets number of columns of the matrix.")

    size = property(lambda self: (self.__nrow, self.__ncol),
                    doc="Gets dimension of the matrix.")


    # Explicit Operations

    def resize(self, nrow: int = None, ncol: int = None, *, pad_rows=False):
        """
        Resizes the matrix.

        Truncates, if the new dimension is less than the current for either or both axes.
        Zero-fills, if the new dimension is greater than the current on either or both axes.

        If 'pad_rows' is true, pad each row of the underlying array
        to match up to the given number of columns.
        NOTE: this argument is meant for internal use only.
        """

        if not all(isinstance(x, (type(None), int)) for x in (nrow, ncol)):
            # At least one value given for new dimnsion is of a wrong type.
            raise TypeError("Any specified dimension must be an integer.")

        if any(None is not x < 1 for x in (nrow, ncol)):
            # At least one of the new dimensions given is less than 1.
            raise ValueError("Any specified dimension must be +ve.")

        # Number of rows
        if nrow:  # 'nrow' can only be either None or a +ve integer at this point.
            diff = nrow - self.__nrow
            if diff > 0:
                self.__array.extend([[Element(0)] * self.__ncol] * diff)
            elif diff < 0:
                # Delete the last `-diff` rows (**in-place**).
                self.__array[:] = self.__array[:diff]
            self.__nrow = nrow

        # Number of columns
        if ncol:  # 'ncol' can only be either None or a +ve integer at this point.
            if pad_rows:
                if any(len(row) > ncol for row in self.__array):
                    raise ValueError("Specified number of columns is"
                                        " less than length of longest row.")
                for row in self.__array: row.extend([Element(0)] * (ncol - len(row)))
                self.__ncol = ncol
                return

            diff = ncol - self.__ncol
            if diff > 0:
                for row in self.__array: row.extend([Element(0)] * diff)
            elif diff < 0:
                # Delete the last `-diff` elements in each row (**in-place**).
                for row in self.__array: row[:] = row[:diff]
            self.__ncol = ncol
        elif pad_rows:
            raise ValueError("Number of columns not specified for padding.")

