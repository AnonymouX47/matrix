"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from math import ceil
from numbers import Real

from ..utils import adjust_slice
from .elements import to_Element

__all__ = ("Rows",)

class Rows:
    """
    A (pseudo-container) view over the rows of a matrix.
    Implements direct row read/write operations.
    """

    __slots__ = ("__matrix",)

    def __init__(self, matrix):
        """See class Description."""

        self.__matrix = matrix

    def __repr__(self):
        return f"<Rows of {self.__matrix!r} at {id(self):#x}>"

    def __getitem__(self, sub):
        """
        Returns the:
        - ith row, if subscript is an integer, i.
        - rows selected by the slice, if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                return self.__matrix._array[sub-1]
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
            try:
                array = tuple(value)
            except TypeError:
                raise TypeError("The assigned object must be iterable.") from None
            if not all((isinstance(x, (Decimal, Real)) for x in value)):
                raise TypeError("The object must be an iterable of real numbers.")
            if len(array) != self.__matrix.ncol:
                raise ValueError("The iterable is not of an appropriate length.")

            self.__matrix._array[sub-1][:] = [to_Element(x) for x in array]
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

