"""Definitions pertaining to the rows of a matrix."""

from decimal import Decimal
from functools import partial
from numbers import Real

from ..utils import *
from .bases import *
from .elements import to_Element

__all__ = ("Columns",)

class Columns(RowsCols):
    """A (pseudo-container) view over the columns of a matrix."""

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __getitem__(self, sub):
        """
        Returns the:
        - ith column, if subscript is an integer, i.
        - columns selected by the slice, if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                return Column(self.__matrix, sub-1)
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.ncol)
            return ColumnsSlice(self.__matrix, sub)

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
            value = valid_container(value, self.__matrix.nrow)
            for row, element in zip(self.__matrix._array, value):
                row[sub-1] = to_Element(element)
        else:
            raise IndexError("Index out of range.")

    def __delitem__(self, sub):
        """
        Deletes the:
        - ith column, if subscript is an integer, i.
        - columns selected by the slice, if subscript is a slice.

        NOTE:
        - Still 1-indexed and slice.stop is included.
        - Deleting all columns isn't allowed.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.ncol:
                sub -= 1
                for row in self.__matrix._array:
                    del row[sub]
                self.__matrix.__ncol -= 1
            else:
                raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.ncol)
            if (diff := slice_length(sub)) == self.__matrix.ncol:
                raise ValueError("Emptying the matrix isn't allowed.")
            for row in self.__matrix._array:
                del row[sub]
            self.__matrix.__ncol -= diff
        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        return self.__matrix.ncol

    def __iter__(self):
        return MatrixIter(
                map(partial(Column, self.__matrix), range(self.__matrix.ncol)),
                self.__matrix)


class ColumnsSlice(RowsColumnsSlice):
    """
    A (pseudo-container) view over a slice of the colums of a matrix.

    NOTE: An error is raised if an operation is performed on an instance
    after a matrix has been resized, if it was created before.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __getitem__(self, sub):
        """
        Returns the:
        - ith column, if subscript is an integer, i.
        - columns selected by the slice, if subscript is a slice.

        NOTE: Still 1-indexed and slice.stop is included.
        """

        self.validity_check()

        if isinstance(sub, int):
            if 0 < sub <= self.__length:
                return Column(self.__matrix, slice_index(self.__slice, sub-1))
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__length)
            return __class__(self.__matrix, original_slice(self.__slice, sub))

        raise TypeError("Subscript must either be an integer or a slice.")

    def __iter__(self):
        self.validity_check()

        return MatrixIter(map(partial(Column, self.__matrix),
                                range(*self.__slice.indices(self.__slice.stop))),
                        self.__matrix)


class Column(RowColumn):
    """
    A single column of a matrix.

    'matrix' -> The underlying matrix whose column is being represented.
    'index' -> The (0-indexed) index of the column the object should represent.

    Instead of returning new lists or tuples as columns, this would:
    - be more efficient (both time and space).
      - prevents copying element references.
    - have direct access to the underlying matrix data.

    NOTE: An error is raised if an operation is performed on an instance
    after a matrix has been resized, if it was created before.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __str__(self):
        self.validity_check()

        return f"Column({[row[self.__index] for row in self.__matrix._array]})"

    def __getitem__(self, sub):
        self.validity_check()

        """
        Returns:
        - the ith element of the column, if 'sub' is an integer, i.
        - a list of the elements selected by the slice, if 'sub' is a slice.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                return self.__matrix._array[sub-1][self.__index]
            raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            return [row[self.__index] for row in self.__matrix._array[sub]]

        raise TypeError("Subscript must either be an integer or a slice.")

    def __setitem__(self, sub, value):
        self.validity_check()

        """
        Sets:
        - the ith element of the column to 'value', if 'sub' is an integer, i.
        - the elements selected by the slice to the elements in iterable 'value',
          if 'sub' is a slice.
        """

        if isinstance(sub, int):
            if 0 < sub <= self.__matrix.nrow:
                if isinstance(value, (Real, Decimal)):
                    self.__matrix._array[sub-1][self.__index] = to_Element(value)
                else:
                    raise TypeError("Matrix elements can only be real numbers.")
            else:
                raise IndexError("Index out of range.")

        elif isinstance(sub, slice):
            sub = adjust_slice(sub, self.__matrix.nrow)
            value = valid_container(value, slice_length(sub))
            for row, element in zip(self.__matrix._array[sub], value):
                row[self.__index] = element

        else:
            raise TypeError("Subscript must either be an integer or a slice.")

    def __len__(self):
        self.validity_check()

        return self.__matrix.nrow

    def __iter__(self):
        self.validity_check()

        return MatrixIter((row[self.__index] for row in self.__matrix._array),
                            self.__matrix)

    def __contains__(self, item):
        self.validity_check()

        return any(item == row[self.__index] for row in self.__matrix._array)

    def __eq__(self, other):
        self.validity_check()

        if self.__matrix is other.__matrix and self.__index == other.__index:
            return True
        else:
            i1 = self.__index
            i2 = other.__index
            return all(r1[i1] == r2[i2] for r1, r2 in zip(self.__matrix._array,
                                                            other.__matrix._array))

