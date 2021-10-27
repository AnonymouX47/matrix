"""Baseclasses of rows and columns classes."""

from abc import ABCMeta, abstractmethod
from decimal import Decimal
from numbers import Real
from operator import add, mul, truediv, sub

from .elements import Element
from .. import utils  # Only meant to be used for `ROUND_LIMIT`
from ..exceptions import BrokenMatrixView
from ..utils import (
    display_adj_slice,
    is_iterable,
    mangled_attr,
    slice_length,
    valid_container,
)

__all__ = ("RowsColumns", "RowsColumnsSlice", "RowColumn")


@mangled_attr(_set=False, _del=False)
class RowsColumns(metaclass=ABCMeta):
    """Baseclass of Rows() and Columns()."""

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix",)

    def __init__(self, matrix):
        """See class Description."""

        self.__matrix = matrix

    def __repr__(self):
        return f"<{type(self).__name__} of {self.__matrix!r}>"

    @abstractmethod
    def __getitem__(self, sub):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, sub, value):
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, sub):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError


@mangled_attr(_set=False, _del=False)
class RowsColumnsSlice(metaclass=ABCMeta):
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
            raise BrokenMatrixView(
                "The matrix has been resized after"
                f" this matrix-view ({self!r}) was created.",
                view_obj=self,
            )

    @abstractmethod
    def __getitem__(self, sub):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError


@mangled_attr(_set=False, _del=False)
class RowColumn(metaclass=ABCMeta):
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
        Point-wise addition.

        'other' must be an iterable of real numbers
        with same length as the row/column.
        """

        self.__validity_check()

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(add, self._fast_iter(), other._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(add, self._fast_iter(), other)))

        return NotImplemented

    def __radd__(self, other) -> list:
        """Reflected point-wise addition."""

        return self.__add__(other)

    def __sub__(self, other) -> list:
        """
        Point-wise subtraction.

        'other' must be an iterable of real numbers
        with same length as the row/column.
        """

        self.__validity_check()

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(sub, self._fast_iter(), other._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(sub, self._fast_iter(), other)))

        return NotImplemented

    def __rsub__(self, other) -> list:
        """Reflected point-wise subtraction."""

        self.__validity_check()

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(sub, other._fast_iter(), self._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(sub, other, self._fast_iter())))

        return NotImplemented

    def __mul__(self, other) -> list:
        """
        Scalar multiplication.

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
        Point-wise multiplication.

        'other' must be an iterable of real numbers
        with same length as the row/column.
        """

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(mul, self._fast_iter(), other._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(mul, self._fast_iter(), other)))

        return NotImplemented

    def __rmatmul__(self, other):
        """Reflected point-wise multiplication"""

        return self.__matmul__(other)

    def __truediv__(self, other) -> list:
        """
        Scalar or point-wise division.

        'other' must be a real number
        or iterable of real numbers with same length as the row/column.
        """

        self.__validity_check()

        if isinstance(other, (Real, Decimal)):
            return _rounded([elem / other for elem in self._fast_iter()])

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(truediv, self._fast_iter(), other._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(truediv, self._fast_iter(), other)))

        return NotImplemented

    def __rtruediv__(self, other) -> list:
        """
        Reflected point-wise division
        (Scalar division shouldn't be reflected)
        """

        self.__validity_check()

        if isinstance(other, __class__):
            if len(self) == len(other):
                return _rounded(list(map(truediv, other._fast_iter(), self._fast_iter())))
            raise ValueError("The rows/columns must be of equal length.")

        if is_iterable(other):
            other = valid_container(other, len(self))
            return _rounded(list(map(truediv, other, self._fast_iter())))

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
            raise BrokenMatrixView(
                "The matrix has been resized after"
                f" this matrix-view ({self!r}) was created.",
                view_obj=self,
            )

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, sub):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, sub, value):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, item):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __iadd__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __isub__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __imul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __imatmul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __itruediv__(self, other):
        raise NotImplementedError


# Utility functions


def _rounded(row_col: list) -> list:
    limit = Element(f"1e-{utils.ROUND_LIMIT}")

    return [Element(round(x)) if 0 < abs(x - round(x)) < limit else x for x in row_col]
