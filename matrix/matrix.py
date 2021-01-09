"""Definition of the various classes."""


class Matrix:
    """
    The main matrix definition.

    The properties here are used to:
    - ensure the "public" attribute is unwritable.
    - make sure potential subclasses have a means of access to the "private" attribute."
    """

    __slots__ = ("__array", "nrow", "ncol", "__rows", "__columns")

    def __init__(self, rows_array = None, cols_zfill = None):
        """
        - Given two integers, it's initialized as a zero matrix of that dimension.
        - Given a 2-D iterable of integers:
          - If all rows have the same length, initialized as if the array is row-major.
          - If row lengths don't match but `cols_zfill is True`,
            zero-fill to the right to match.
        """

        if isinstance(rows_array, int) and isinstance(cols_zfill, int):
            self.__array = [[0] * cols_zfill for _ in range(rows_array)]
            self.nrow, self.ncol = rows_array, cols_zfill
        else:
            raise TypeError("Constructor arguments must either be two integers "
                            "OR a 2D iterable of integers and an optional boolean.")

        self.__rows = Rows(self)
        self.__columns = Columns(self)

    _array = property(doc="Gets underlying array of the matrix.")
    @_array.getter
    def _array(self): return self.__array

    rows = property(doc="Gets Rows() object of the matrix.")
    @rows.getter
    def rows(self): return self.__rows

    columns = property(doc="Gets Colums() object of the matrix.")
    @columns.getter
    def columns(self): return self.__columns


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

