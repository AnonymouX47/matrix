"""Baseclasses of rows and columns classes."""

from decimal import Decimal
from numbers import Real
from operator import add, mul, truediv, sub

from .elements import Element
from ..utils import (display_adj_slice, mangled_attr, slice_length,
                    valid_container, BrokenMatrixView
                    )

@mangled_attr(_set=False, _del=False)
class RowsColumns:
    """Baseclass of Rows() and Columns()."""

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix",)

    def __init__(self, matrix):
        """See class Description."""

        self.__matrix = matrix

    def __repr__(self):
        return f"<{type(self).__name__} of {self.__matrix!r}>"


@mangled_attr(_set=False, _del=False)
class RowsColumnsSlice:
    """Baseclass of RowsSlice() and ColumnsSlice()."""

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix", "__slice", "__slice_disp", "__length", "__size_hash")

    def __init__(self, matrix, slice_):
        """See class Description."""

        self.__matrix = matrix
        self.__slice = slice_
        self.__slice_disp = display_adj_slice(slice_)
        self.__length = slice_length(slice_)
        self.__size_hash = hash(matrix.size)

    def __repr__(self):
        return f"<{type(self).__name__[:-5]} [{self.__slice_disp}] of {self.__matrix!r}>"

    def __len__(self):
        self.__validity_check()

        return self.__length

    def __validity_check(self):
        """
        Raises an error if the matrix has been resized
        since when a "matrix-view" instance was created.
        """

        if self.__size_hash != hash(self.__matrix.size):
            raise BrokenMatrixView("The matrix has been resized after"
                                    f" this matrix-view ({self!r}) was created.",
                                    view_obj=self)


@mangled_attr(_set=False, _del=False)
class RowColumn:
    """Baseclass of Row() and Column()."""

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix", "__index", "__size_hash")

    def __init__(self, matrix, index):
        """See class Description."""

        self.__matrix = matrix
        self.__index = index
        self.__size_hash = hash(matrix.size)

    def __repr__(self):
        return f"<{type(self).__name__} {self.__index + 1} of {self.__matrix!r}>"


    # The following operations must not return Row/Column instances
    # because they are views of the underlying matrix,
    # which is not being modified itself.

    def __add__(self, other) -> list:
        """
        Adds rows/columns element-by-element.

        Each operand must be either a `Row` or `Column` and be of equal length.
        """

        self.__validity_check()

        if not (isinstance(other, __class__) or valid_container(other)):
            return NotImplemented

        if len(self) != len(other):
            raise ValueError("The rows/columns must be of equal length.")

        return list(map(
                add,
                self._fast_iter(),
                other._fast_iter() if isinstance(other, __class__) else other
                ))

    def __sub__(self, other) -> list:
        """
        Subtracts rows/columns element-by-element.

        Each operand must be either a `Row` or `Column` and be of equal length.
        """

        self.__validity_check()

        if not (isinstance(other, __class__) or valid_container(other)):
            return NotImplemented

        if len(self) != len(other):
            raise ValueError("The rows/columns must be of equal length.")

        return list(map(
                sub,
                self._fast_iter(),
                other._fast_iter() if isinstance(other, __class__) else other
                ))

    def __mul__(self, other) -> list:
        """
        Multiply each element of row/column by scalar.

        'other' must be a real number.
        """

        self.__validity_check()

        if not isinstance(other, (Real, Decimal)):
            return NotImplemented

        return _rounded([elem * other for elem in self._fast_iter()])

    def __rmul__(self, other) -> list:
        """Reflected scalar multiplication."""

        return self.__mul__(other)

    def __matmul__(self, other):
        """
        Element-wise multiplication of rows/columns.

        The second operand must be a `Row`, `Column`
        or any iterable of real numbers and be of equal length.
        """

        if not (isinstance(other, __class__) or valid_container(other)):
            return NotImplemented

        if len(self) != len(other):
            raise ValueError("The rows/columns must be of equal length.")

        return _rounded(map(
                mul,
                self._fast_iter(),
                other._fast_iter() if isinstance(other, __class__) else other
                ))

    def __rmatmul__(self, other):
        """Reflected row/column element-wise multiplication"""

        return self.__matmul__(other)

    def __truediv__(self, other) -> list:
        """
        Divide row/column by scalar, element-by-element.

        'other' must be a real number.
        """

        self.__validity_check()

        if isinstance(other, (Real, Decimal)):
            return _rounded([elem / other for elem in self])
        elif isinstance(other, __class__) or valid_container(other):
            if len(self) != len(other):
                raise ValueError("The rows/columns must be of equal length.")
            return _rounded(map(
                    truediv,
                    self._fast_iter(),
                    other._fast_iter() if isinstance(other, __class__) else other
                    ))

        return NotImplemented

    def __bool__(self):
        """
        Returns `False` if all elements in the row/column are zeros
        and `True` otherwise.
        """

        return any(self._fast_iter())


    def __validity_check(self):
        """
        Raises an error if the matrix has been resized
        since when a "matrix-view" instance was created.
        """

        if self.__size_hash != hash(self.__matrix.size):
            raise BrokenMatrixView("The matrix has been resized after"
                                    f" this matrix-view ({self!r}) was created.",
                                    view_obj=self)


# Utility functions

def _rounded(row_col: list) -> list:
    return [Element(round(x))
                if abs(x - round(x)) < Element("1e-12")
                else x
            for x in row_col]

