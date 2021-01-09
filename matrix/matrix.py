#!/usr/bin/env python3.8

"""Definitions of the various classes."""


class InitDocMeta(type):
    """A metaclass that sets the docstring of it's instances' `__init__` to the class'"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set `__init__` method's docstring to that of the class.
        self.__init__.__doc__ = self.__doc__


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
            minlen, maxlen, self.__nrow, array = self.__check_iterable(rows_array)

            if maxlen == 0:
                raise ValueError("The inner iterables are empty.\n"
                                "\tBoth dimensions must be greater than zero.")

            if minlen == maxlen:
                self.__array = array
                self.__ncol = maxlen
            elif cols_zfill:
                self.__array = array
                self.resize(self.__nrow, maxlen)
            else:
                raise ValueError("'zfill' should be `True`"
                                " when the array has variable row lengths.")
        else:
            raise TypeError("Constructor arguments must either be two positive integers"
                            " OR a 2D iterable of integers and an optional boolean.")

        self.__rows = Rows(self)
        self.__columns = Columns(self)


    _array = property(lambda self: self.__array, doc="Gets underlying array of the matrix.")

    rows = property(lambda self: self.__rows, doc="Gets Rows() object of the matrix.")

    columns = property(lambda self: self.__columns, doc="Gets Colums() object of the matrix.")

    nrow = property(lambda self: self.__nrow, doc="Gets number of rows of the matrix.")

    ncol = property(lambda self: self.__ncol, doc="Gets number of columns of the matrix.")


    @staticmethod
    def __check_iterable(iterable):
        """
        Checks if `iterable` represents a two dimensional array of integers.

        If so, returns the
        - shortest row lenght,
        - longest row lenght,
        - number of rows,
        - resulting array as a list.
        """

        try:
            array = [[int(element) for element in row] for row in iterable]
        except TypeError:
            raise TypeError("The array argument should be an iterable"
                            " of iterables of integers.") from None

        lengths = [len(row) for row in array]

        return min(lengths), max(lengths), len(array), array


class Rows:
    """
    A (pseudo-container) view over the rows of a matrix.
    Implements direct row read/write operations.
    """

    def __init__(self, matrix):
        pass


class Columns:
    """A (pseudo-container) view over the colums of a matrix.
    Implements direct column read/write operations.
    """

    def __init__(self, matrix):
        pass

