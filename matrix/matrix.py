"""Definitions of the various classes."""

from itertools import starmap

from .utils import *


class Matrix:
    """
    The main matrix definition.

    The properties here are used to:
    - ensure the "public" attribute is unwritable.
    - make sure potential subclasses have a means of access to the "private" attribute."

    A matrix can be constructed in two ways:
    - Given two positive integers, it's initialized as a zero matrix of that dimension.
      e.g

      >>> print(Matrix(2, 2))
      —————————
      | 0 | 0 |
      —————————
      | 0 | 0 |
      —————————

    - Given a 2-D iterable of integers:
      - If all rows have the same length, initialized as if the array is row-major.
      - If row lengths don't match but `zfill is True`, zero-fill to the right to match.
    """

    __slots__ = ("__array", "__nrow", "__ncol", "__rows", "__columns")


    # Implicit Operations

    def __init__(self, rows_array=None, cols_zfill=None):
        """
        Two signatures:

        class Matrix(rows: int, cols: int)

        OR

        class Matrix(array: iterable, zfill: bool = False)
        """

        if isinstance(rows_array, int) and isinstance(cols_zfill, int):
            rows, cols = rows_array, cols_zfill

            if rows > 0 and cols > 0:
                self.__array = [[0] * cols for _ in range(rows)]
                self.__nrow, self.__ncol = rows, cols
            else:
                raise ValueError("Both dimensions must be positive integers.")
        elif hasattr(rows_array, "__iter__") and isinstance(cols_zfill, (type(None), bool)):
            minlen, maxlen, self.__nrow, array = check_iterable(rows_array)

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
                            " OR a 2D iterable of integers and an optional boolean.")

        self.__rows = Rows(self)
        self.__columns = Columns(self)


    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, self.__nrow, self.__ncol)

    def __str__(self):
        """
        Number with longest str() in a column determines that column's width.
        The longest number must either be the most +ve or most -ve.
        """

        column_widths = [max(map(len, map(str, (min(column), max(column)))))
                        for column in self.__columns]
        width_fmt = [f"^{width}" for width in column_widths]

        bar = '\u2015' * (sum(column_widths) + self.__ncol * 3  + 1)

        return (bar
            + ('\n' + bar).join('\n| ' + ' | '.join(starmap(format, zip(row, width_fmt))) + ' |'
                                for row in self.__array)
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
          - slices out of range are "forgiven".
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
                    raise IndexError("Row and/or Column index is/are"
                                    " either out of range or negative.")

            elif all(isinstance(x, slice) for x in sub):
                if not all(map(valid_slice, sub)):
                    raise ValueError("start, stop or step of a slice cannot be negative."
                                    " Also make sure `start <= stop` in the slices.")

                rows, cols = starmap(adjust_slice, zip(sub, self.size))
                return type(self)(row[cols] for row in self.__array[rows])

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
        - a Matrix instance or 2D array of integers with appropriate dimensions,
          if 'sub' references a "block-slice".
        """

        if isinstance(sub, tuple) and len(sub) == 2:

            if all(isinstance(x, int) for x in sub):
                row, col = sub
                if 0 < row <= self.__nrow and 0 < col <= self.__ncol:
                    if isinstance(value, int):
                        self.__array[row - 1][col - 1] = value
                    else:
                        raise TypeError("Matrix elements can only be integers,"
                                        f" not {type(value)}() objects.")
                else:
                    raise IndexError("Row and/or Column index is/are"
                                    " either out of range or negative.")

            elif all(isinstance(x, slice) for x in sub):
                if not all(map(valid_slice, sub)):
                    raise ValueError("start, stop or step of a slice cannot be negative."
                                    " Also make sure `start <= stop` in the slices.")

                rows, cols = starmap(adjust_slice, zip(sub, self.size))

                if isinstance(value, __class__):
                    array = value.__array
                    checks = (value.__ncol == cols.stop - cols.start
                              and value.__nrow == rows.stop - rows.start)
                else:
                    minlen, maxlen, nrow, array = check_iterable(value)
                    checks = (minlen == maxlen
                              and maxlen == cols.stop - cols.start
                              and nrow == rows.stop - rows.start)

                if checks:
                    for row, _slice in zip(self.__array[rows], array):
                        row[cols] = _slice
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

        if not all(x is None or isinstance(x, int) for x in (nrow, ncol)):
            # At least one value given for new dimnsion is of a wrong type.
            raise TypeError("Any specified dimension must be an integer.")

        if any(None is not x < 1 for x in (nrow, ncol)):
            # At least one of the new dimensions given is less than 1.
            raise ValueError("Any specified dimension must be +ve.")

        # Number of rows
        if nrow:  # 'nrow' can only be either None or a +ve integer at this point.
            diff = nrow - self.__nrow
            if diff > 0:
                self.__array.extend([[0] * self.__ncol] * diff)
            elif diff < 0:
                # Delete the last `-diff` rows (**in-place**).
                self.__array[:] = self.__array[:diff]
            self.__nrow = nrow

        # Number of columns
        if ncol:  # 'ncol' can only be either None or a +ve integer at this point.
            if pad_rows:
                for row in self.__array: row.extend([0] * (ncol - len(row)))
                self.__ncol = ncol
                return

            diff = ncol - self.__ncol
            if diff > 0:
                for row in self.__array: row.extend([0] * diff)
            elif diff < 0:
                # Delete the last `-diff` elements in each row (**in-place**).
                for row in self.__array: row[:] = row[:diff]
            self.__ncol = ncol
        elif pad_rows:
            raise ValueError("Number of columns not specified for padding.")


class Rows:
    """
    A (pseudo-container) view over the rows of a matrix.
    Implements direct row read/write operations.
    """

    def __init__(self, matrix):
        self.__matrix = matrix

    def __iter__(self):
        return (row.copy() for row in self.__matrix._array)


class Columns:
    """A (pseudo-container) view over the colums of a matrix.
    Implements direct column read/write operations.
    """

    def __init__(self, matrix):
        self.__matrix = matrix

    def __iter__(self):
        return ([row[col] for row in self.__matrix._array]
                for col in range(self.__matrix.ncol))

