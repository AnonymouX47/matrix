"""Definitions of Exception classes"""


class MatrixException(Exception):
    """Baseclass of matrix exceptions."""


class BrokenMatrixView(MatrixException, RuntimeError):
    """
    Raised for errors related to resizing a matrix.
    It's just for the sake of specificity (e.g during error-handling).

    Args:
        - args -> tuple of all positional args passed to the class constructor.
        - view_obj -> object that triggered the error. Stored as an instance
        attribute with the same name.
    """

    def __init__(self, *args, view_obj=None):
        super().__init__(*args)
        self.obj = view_obj


class InvalidDimension(MatrixException, ValueError):
    """
    Raised for errors related to incorrect or incompatible
    matrix dimensions.

    Args:
        - matrices -> a tuple containing the matrix/matrices responsible
        for the error. Stored as an instance attribute with the same name.
    """

    def __init__(self, *args, matrices=None):
        super().__init__(*args)
        self.matrices = matrices


class ZeroDeterminant(MatrixException, ArithmeticError):
    """
    Raised when a matrix of non-zero determinant is required.

    Args:
        - matrix -> The matrix with zero determinant that triggered the exception.
    """

    def __init__(self, *args, matrix):
        super().__init__(*args)
        self.matrix = matrix
