"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from functools import partial
from numbers import Real

from ..utils import *
from .bases import *
from .elements import to_Element

__all__ = ("Rows",)

class Rows(RowsCols):
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
                return Row(self.__matrix, sub-1)
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
            self.__matrix._array[sub-1][:] = value
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
                del self.__matrix._array[sub-1]
                self.__matrix.__nrow -= 1
            else:
                raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            if (diff := slice_length(sub)) == self.__matrix.nrow:
                raise ValueError("Emptying the matrix isn't allowed.")
            del self.__matrix._array[sub]
            self.__matrix.__nrow -= diff
        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        return self.__matrix.nrow

    def __iter__(self):
        return MatrixIter(
                    map(partial(Row, self.__matrix), range(self.__matrix.nrow)),
                    self.__matrix)


class RowsSlice(RowsColumnsSlice):
    """A (pseudo-container) view over a slice of the rows of a matrix."""

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

        if isinstance(sub, int):
            if 0 < sub <= self.__length:
                return Row(self.__matrix, slice_index(self.__slice, sub-1))
            raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__length)
            return __class__(self.__matrix, original_slice(self.__slice, sub))

        raise TypeError("Subscript must either be an integer or a slice.")

    def __iter__(self):
        return MatrixIter(map(partial(Row, self.__matrix),
                                range(*self.__slice.indices(self.__slice.stop))),
                            self.__matrix)


class Row(RowColumn):
    """
    A single row of a matrix.

    'matrix' -> The underlying matrix whose row is being represented.
    'index' -> The (0-indexed) index of the row the object should represent.

    Instead of returning new lists or tuples as rows, this would:
    - be more efficient (both time and space).
      - prevents copying element references.
    - have direct access to the underlying matrix data.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __str__(self):
        return f"Row({self.__matrix._array[self.__index]})"

    def __getitem__(self, sub):
        """
        Returns:
        - the ith element of the row, if 'sub' is an integer, i.
        - a list of the elements selected by the slice, if 'sub' is a slice.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                return self.__matrix._array[self.__index][sub-1]
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

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                if isinstance(value, (Real, Decimal)):
                    self.__matrix._array[self.__index][sub-1] = to_Element(value)
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
        return self.__matrix.ncol

    def __iter__(self):
        return MatrixIter(iter(self.__matrix._array[self.__index]), self.__matrix)

