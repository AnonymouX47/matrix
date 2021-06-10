"""Top-most package level."""

from .matrix import Matrix, unit_matrix
from .utils import (MatrixException, BrokenMatrixView, InvalidDimension,
                    ZeroDeterminant
                    )

# Exclude submodule names from displayed full names.
for obj in (Matrix, MatrixException, InvalidDimension, BrokenMatrixView,
            ZeroDeterminant, unit_matrix):
    obj.__module__ = "matrix"

