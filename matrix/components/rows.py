"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from functools import partial
from numbers import Real

from .bases import *
from .elements import to_Element
from ..exceptions import InvalidDimension
from ..utils import (
    adjust_slice,
    slice_length,
    slice_index,
    original_slice,
    valid_container,
    MatrixIter,
)

__all__ = ("Rows",)


@RowsColumns._register
class Rows(RowsColumns):
    """A (pseudo-container) view over the rows of a matrix."""

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __getitem__(self, sub):
        """
        Returns the:
        - ith row, if subscript is an integer, i.
        - rows selected by the slice, if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                return Row(self.__matrix, sub - 1)
            raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            return RowsSlice(self.__matrix, sub)

        raise TypeError("Subscript must either be an integer or a slice.")

    def __setitem__(self, sub, value):
        """
        Sets the elements in the row specifed by 'sub'
        to the items of the iterable 'value'.

        sub: can only be an integer.
        value: an iterable of real numbers.
          - whose length must be equal to that of the row.
          - i.e `len(value) == matrix.ncol`.
        """

        if not isinstance(sub, int):
            raise TypeError("Subscript for row assigment must be an integer.")

        if 0 < sub <= self.__matrix.nrow:
            value = valid_container(value, self.__matrix.ncol)
            self.__matrix._array[sub - 1][:] = value
        else:
            raise IndexError("Index out of range.")

    def __delitem__(self, sub):
        """
        Deletes the:
        - ith row, if subscript is an integer, i.
        - rows selected by the slice, if subscript is a slice.

        NOTE:
        - Still 1-indexed and slice.stop is included.
        - Deleting all rows isn't allowed.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                if self.__matrix.nrow == 1:
                    raise InvalidDimension(
                        "Emptying the matrix isn't allowed.", matrices=(self.__matrix,)
                    )
                del self.__matrix._array[sub - 1]
                self.__matrix.__nrow -= 1
            else:
                raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            if (diff := slice_length(sub)) == self.__matrix.nrow:
                raise InvalidDimension("Emptying the matrix isn't allowed.")
            del self.__matrix._array[sub]
            self.__matrix.__nrow -= diff
        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        return self.__matrix.nrow

    def __iter__(self):
        return MatrixIter(
            map(partial(Row, self.__matrix), range(self.__matrix.nrow)), self.__matrix
        )


@RowsColumnsSlice._register
class RowsSlice(RowsColumnsSlice):
    """
    A (pseudo-container) view over a slice of the rows of a matrix.

    NOTE: An error is raised if an operation is performed on an instance
    after a matrix has been resized, if it was created before.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __getitem__(self, sub):
        """
        Returns the:
        - ith row, if subscript is an integer, i.
        - Rows() instance representing the rows selected by the slice,
          if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        self.__validity_check()

        if isinstance(sub, int):
            if 0 < sub <= self.__length:
                return Row(self.__matrix, slice_index(self.__slice, sub - 1))
            raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__length)
            return __class__(self.__matrix, original_slice(self.__slice, sub))

        raise TypeError("Subscript must either be an integer or a slice.")

    def __iter__(self):
        self.__validity_check()

        return MatrixIter(
            map(
                partial(Row, self.__matrix),
                range(*self.__slice.indices(self.__slice.stop)),
            ),
            self.__matrix,
        )


@RowColumn._register
class Row(RowColumn):
    """
    A single row of a matrix.

    Args:
        'matrix' -> The underlying matrix whose row is being represented.
        'index' -> The (0-indexed) index of the row the object should represent.

    Instead of returning new lists or tuples as rows, this would:
    - be more efficient (both time and space).
      - prevents copying element references.
    - have direct access to the underlying matrix data.

    NOTE: An error is raised if an operation is performed on an instance
    after a matrix has been resized, if it was created before.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __str__(self):
        self.__validity_check()

        return f"Row({self.__matrix._array[self.__index]})"

    def __getitem__(self, sub):
        """
        Returns:
        - the ith element of the row, if 'sub' is an integer, i.
        - a list of the elements selected by the slice, if 'sub' is a slice.
        """

        self.__validity_check()

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                return self.__matrix._array[self.__index][sub - 1]
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.ncol)
            return self.__matrix._array[self.__index][sub]

        raise TypeError("Subscript must either be an integer or a slice.")

    def __setitem__(self, sub, value):
        """
        Sets:
        - the ith element of the row to 'value', if 'sub' is an integer, i.
        - the elements selected by the slice to the elements in iterable 'value',
          if 'sub' is a slice.
        """

        self.__validity_check()

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                if isinstance(value, (Real, Decimal)):
                    self.__matrix._array[self.__index][sub - 1] = to_Element(value)
                else:
                    raise TypeError("Matrix elements can only be real numbers.")
            else:
                raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.ncol)
            value = valid_container(value, slice_length(sub))
            self.__matrix._array[self.__index][sub] = value

        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        self.__validity_check()

        return self.__matrix.ncol

    def __iter__(self):
        self.__validity_check()

        return MatrixIter(iter(self.__matrix._array[self.__index]), self.__matrix)

    def __contains__(self, item):
        self.__validity_check()

        if not isinstance(item, (Real, Decimal)):
            raise TypeError("Matrix elements are only real numbers.")

        return item in self.__matrix._array[self.__index]

    def __eq__(self, other):
        self.__validity_check()

        if not isinstance(other, __class__):
            return NotImplemented

        if self.__matrix is other.__matrix and self.__index == other.__index:
            return True
        else:
            lhs = self.__matrix._array[self.__index]
            rhs = other.__matrix._array[self.__index]

            return lhs == rhs

    # In-place operations
    # These modify the matrix directly

    def __iadd__(self, other):
        if (result := self.__add__(other)) is not NotImplemented:
            self.__matrix._array[self.__index] = result
            return self

        return result

    def __isub__(self, other):
        if (result := self.__sub__(other)) is not NotImplemented:
            self.__matrix._array[self.__index] = result
            return self

        return result

    def __imul__(self, other):
        if (result := self.__mul__(other)) is not NotImplemented:
            self.__matrix._array[self.__index] = result
            return self

        return result

    def __imatmul__(self, other):
        if (result := self.__matmul__(other)) is not NotImplemented:
            self.__matrix._array[self.__index] = result
            return self

        return result

    def __itruediv__(self, other):
        if (result := self.__truediv__(other)) is not NotImplemented:
            self.__matrix._array[self.__index] = result
            return self

        return result

    # Explicit

    @property
    def pivot_index(self):
        """Returns the index of the pivot (first non-zero) element of the row."""

        for i, elem in enumerate(self.__matrix._array[self.__index], 1):
            if elem:
                return i
        else:
            # Zero is never a possible index in the matrix
            return 0  # Zero row.

    def _fast_iter(self):
        """Meant to be used internally for faster iteration"""

        return iter(self.__matrix._array[self.__index])
