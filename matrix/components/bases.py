"""Baseclasses of rows and columns classes."""

from ..utils import mangled_attr

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

