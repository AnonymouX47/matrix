"""Definitions of utility classes and functions meant for the main classes."""

from decimal import Decimal
from numbers import Real

from .components import to_Element

def display_slice(s: slice):
    """Returns a colon-separated string representation of a slice."""

    # `or` can't be used in case the attribute is 0.
    return "{}:{}{}".format(*(x if x is not None else '' for x in (s.start, s.stop)),
                            f":{s.step}" if s.step is not None else '')

def adjust_slice(s: slice, length: int) -> slice:
    """
    Changes a slice for a 1-indexed sequence to the equivalent 0-index form.

    'stop' is the length of the sequence for which the slice is being adjusted.
    """

    if any(None is not x < 1 for x in (s.start, s.stop, s.step)):
        raise ValueError("%r -> 'start', 'stop' or 'step' is less than 1."
                        % display_slice(s))
    if s.stop is None:
        if None is not s.start > length:
            raise ValueError("%r -> 'start' of slice is greater than matrix dimension."
                            % display_slice(s))
    elif None is not s.start > s.stop:
        raise ValueError("'start' > 'stop' in slice %r."
                        % display_slice(s))

    s = s.indices(length)

    # Leaves the 'stop' attribute unchanged
    # since matrixes include the (1-indexed) 'stop' index for slicing operations.
    return slice(max(0, s[0]-1), *s[1:])


def valid_2D_iterable(iterable):
    """
    Checks if `iterable` represents a two dimensional array of real numbers.

    If so, returns the
    - shortest row lenght,
    - longest row lenght,
    - number of rows,
    - resulting array as a list of matrix elements.
    """

    try:
        array = [[element for element in row] for row in iterable]
    except TypeError:
        raise TypeError("The array must be an iterable of iterables.") from None

    if array:
        if not all((isinstance(x, (Decimal, Real)) for row in array for x in row)):
            raise TypeError("The inner iterables must contain real numbers only.")
        lengths = [len(row) for row in array]
    else:
        raise TypeError("The given iterable is empty.")

    return (min(lengths), max(lengths), len(array),
            [[to_Element(x) for x in row] for row in array])


def valid_container(iterable, length=None):
    """
    Checks if 'iterable' is a valid container of matrix elements, of size 'length'.

    If so, returns a list of matrix elements derived from 'iterable'.
    """

    try:
        container = tuple(iterable)
    except TypeError:
        raise TypeError("The object isn't iterable.") from None
    if not all((isinstance(x, (Decimal, Real)) for x in container)):
        raise TypeError("The object must be an iterable of real numbers.")
    if None is not length != len(container):
        raise ValueError("The iterable is not of an appropriate length.")

    return [to_Element(x) for x in container]


class InitDocMeta(type):
    """A metaclass that sets the docstring of it's instances' `__init__` to the class'"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set `__init__` method's docstring to that of the class.
        self.__init__.__doc__ = self.__doc__


def is_iterable(obj):
    """Checks if obj is iterable."""
    try:
        iter(obj)
    except TypeError:
        return False

    return True

