"""
A python package for matrix operations and manipulations.

Author: AnonymouX47
Home-page: https://github.com/AnonymouX47/matrix
License: GPLv3.0

Copyright 2021
"""

from random import choices, random, randrange

from .exceptions import (
    MatrixException,
    BrokenMatrixView,
    InvalidDimension,
    ZeroDeterminant,
)
from .matrix import *
from . import utils  # Only meant to be used for `ROUND_LIMIT`

__all__ = (
    "Matrix",
    "MatrixException",
    "InvalidDimension",
    "BrokenMatrixView",
    "ZeroDeterminant",
    "unit_matrix",
    "randint_matrix",
    "random_matrix",
    "solve_linear_system",
    "set_round_limit",
)


def randint_matrix(nrow: int, ncol: int, _range, /):
    """
    Generates a matrix with random integer elements.

    Args:
        - nrow -> Number of rows.
        - ncol -> Number of columns.
        - _range -> A `range` instance representing the range of integers
        from which the random elements are selected.
    Returns:
        A Matrix instance.
    Raises:
        `TypeError` if the arguments are of innapropriate types.
        `ValueError` if 'nrow' or 'ncol' is less than 1.
        `ValueError` if the given range is empty.
    """

    if not all(isinstance(arg, int) for arg in (nrow, ncol)):
        raise TypeError("Matrix dimensions must be integers.")
    if not isinstance(_range, range):
        raise TypeError("'_range' must be an instance of type 'range'.")
    if nrow < 1 or ncol < 1:
        raise ValueError("Matrix dimensions must be greater than zero.")

    try:
        matrix = Matrix(choices(_range, k=ncol) for _ in range(nrow))
    except IndexError:
        raise ValueError("The given range is empty.") from None

    return matrix


def random_matrix(nrow: int, ncol: int, start: int, stop: int, /):
    """
    Generates a matrix with random floating-point elements.

    Args:
        - nrow -> Number of rows.
        - ncol -> Number of columns.
        - start -> Minimum value of an element.
        - stop -> Maximum value of an element.
    Returns:
        A Matrix instance.
    Raises:
        `TypeError` if not all the arguments are of type 'int'.
        `ValueError` if 'nrow' or 'ncol' is less than 1.
        `ValueError` if the given range is empty.
    """

    if not all(isinstance(arg, int) for arg in (nrow, ncol, start, stop)):
        raise TypeError("All arguments must be integers.")
    if nrow < 1 or ncol < 1:
        raise ValueError("Matrix dimensions must be greater than zero.")

    try:
        matrix = Matrix(
            (randrange(start, stop) + random() for _ in range(ncol)) for _ in range(nrow)
        )
    except ValueError:
        raise ValueError("The given range is empty.") from None

    return matrix


def solve_linear_system(coeff: Matrix, const: Matrix):
    """
    Solve a system of linear equations.

    Args:
        - coeff -> The matrix of coefficients.
        - const -> The matrix of constants.
    Returns:
        A tuple containing the solutions.
    Raises:
        - `ValueError` if the solutions are indeterminable.
    """

    if not all(isinstance(arg, Matrix) for arg in (coeff, const)):
        raise TypeError("The arguments must be matrices")
    if not coeff.is_square() or coeff.nrow != const.nrow or const.ncol > 1:
        raise InvalidDimension("The input matrices are of inappropriate dimensions.")

    augmented = coeff | const
    augmented.forward_eliminate()
    try:
        augmented.back_substitute()
    except ZeroDeterminant as err:
        raise ValueError("There are no unique solutions for the system.") from err

    return (*augmented.columns[augmented.ncol],)


def set_round_limit(ndigits: int):
    """
    Sets the global rounding/tolerance limit
    i.e the value below which any value is considered zero.
    This value is used to subdue floating-point issues in many operations.

    Args:
        - ndigits -> Number of decimal places after which
        figures are considered insignificant.
    Raises:
        `TypeError` if the argument is not an integer.
    """

    if not isinstance(ndigits, int):
        raise TypeError("The argument must be an integer.")

    utils.ROUND_LIMIT = ndigits
