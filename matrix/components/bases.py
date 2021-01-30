"""Baseclasses of rows and columns classes."""

from ..utils import display_adj_slice, mangled_attr, slice_length

@mangled_attr(_set=False, _del=False)
class RowsCols:
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
    __slots__ = ("__matrix", "__slice", "__slice_disp", "__length")

    def __init__(self, matrix, slice_):
        """See class Description."""

        self.__matrix = matrix
        self.__slice = slice_
        self.__slice_disp = display_adj_slice(slice_)
        self.__length = slice_length(slice_)

    def __repr__(self):
        return f"<{type(self).__name__[:-5]} [{self.__slice_disp}] of {self.__matrix!r}>"

    def __len__(self):
        return self.__length


@mangled_attr(_set=False, _del=False)
class RowColumn:
    """Baseclass of Row() and Column()."""

    # mainly to disable abitrary atributes.
    __slots__ = ("__matrix", "__index")

    def __init__(self, matrix, index):
        """See class Description."""

        self.__matrix = matrix
        self.__index = index

    def __repr__(self):
        return f"<{type(self).__name__} {self.__index + 1} of {self.__matrix!r}>"

