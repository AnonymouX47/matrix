"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from math import ceil
from numbers import Real

from ..utils import adjust_slice, valid_container
from .elements import to_Element

__all__ = ("Rows",)

class Rows:
    """
    A (pseudo-container) view over the rows of a matrix.
    Implements direct row read/write operations.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix",)

    def __init__(self, matrix):
        """See class Description."""

        self.__matrix = matrix

    def __repr__(self):
        return f"<Rows of {self.__matrix!r}>"

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
            return tuple(map(tuple, self.__matrix._array[sub]))

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
                self.__matrix._Matrix__nrow -= 1
            else:
                raise IndexError("Index out of range.")
        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            if (diff := ceil((sub.stop-sub.start) / sub.step)) == self.__matrix.nrow:
                raise ValueError("Emptying the matrix isn't allowed.")
            del self.__matrix._array[sub]
            self.__matrix._Matrix__nrow -= diff
        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __iter__(self):
        return map(tuple, self.__matrix._array)


class Row:
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
    __slots__ = ("__matrix", "__index")

    def __init__(self, matrix, index):
        """See class Description."""

        self.__matrix = matrix
        self.__index = index

    def __repr__(self):
        return f"<Row {self.__index + 1} of {self.__matrix!r}>"

    def __str__(self):
        return f"Row({self.__matrix._array[self.__index]})"

    def __getitem__(self, sub):
        """
        Returns:
        - the ith element of the row, if 'sub' is an integer, i.
        - a list of the elements selected by the slice, if 'sub' is a slice.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                return self.__matrix._array[self.__index][sub-1]
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
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
            if 0 < sub <= self.__matrix.nrow:
                if isinstance(value, (Real, Decimal)):
                    self.__matrix._array[self.__index][sub-1] = to_Element(value)
                else:
                    raise TypeError("Matrix elements can only be real numbers.")
            else:
                raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            value = valid_container(value, ceil((sub.stop-sub.start) / sub.step))
            self.__matrix._array[self.__index][sub] = value

        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        return self.__matrix.ncol

    def __iter__(self):
        return iter(self.__matrix._array[self.__index])

