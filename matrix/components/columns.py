"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from numbers import Real

from .elements import to_Element

__all__ = ("Columns",)

class Columns:
    """A (pseudo-container) view over the colums of a matrix.
    Implements direct column read/write operations.
    """

    __slots__ = ("__matrix",)

    def __init__(self, matrix):
        """See class Description."""

        self.__matrix = matrix

    def __repr__(self):
        return f"<Columns of {self.__matrix!r} at {id(self):#x}>"

    def __getitem__(self, sub):
        """
        Returns:
        - the ith column, if subscript is an integer, i.
        - columns selected by the slice, if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                sub -= 1
                return tuple([row[sub] for row in self.__matrix._array])
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            if (valid_slice(sub)
                and (sub.start or self.__matrix.ncol) <= self.__matrix.ncol):
                sub = adjust_slice(sub, self.__matrix.ncol)
                return tuple([tuple([row[col] for row in self.__matrix._array])
                            for col in range(*sub.indices(self.__matrix.ncol))])

            raise ValueError("start, stop or step of a slice must be > 0."
                "Also Make sure `start <= stop` if both are specified"
                " and that start is less than number of rows/columns as applicable.")

        raise TypeError("Subscript must either be an integer or a slice.")

    def __setitem__(self, sub, value):
        """
        Sets the elements in the column specifed by 'sub'
        to the items of the iterable 'value'.

        sub: can only be an integer.
        value: an iterable of real numbers.
          - whose length must be equal to that of the column.
          - i.e `len(value) == matrix.nrow`.
        """

        if not isinstance(sub, int):
            raise TypeError("Subscript for column assigment must be an integer.")

        if 0 < sub <= self.__matrix.ncol:
            try:
                array = tuple(value)
            except TypeError:
                raise TypeError("The assigned object must be iterable.") from None
            if not all((isinstance(x, (Decimal, Real)) for x in value)):
                raise TypeError("The object must be an iterable of real numbers.")
            if len(array) != self.__matrix.nrow:
                raise ValueError("The iterable is not of an appropriate length.")

            for row, element in zip(self.__matrix._array, array):
                row[sub-1] = to_Element(element)
        else:
            raise IndexError("Index out of range.")

    def __iter__(self):
        return zip(*self.__matrix._array)

