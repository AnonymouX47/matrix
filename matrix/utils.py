"""Definitions of utility classes and functions meant for the main classes."""

from decimal import Decimal
from math import ceil
from numbers import Real

from .components import to_Element

def display_slice(s: slice):
    """Returns a colon-separated string representation of a slice."""

    # `or` can't be used in case the attribute is 0.
    return "{}:{}{}".format(*(x if x is not None else '' for x in (s.start, s.stop)),
                            f":{s.step}" if s.step is not None else '')

def display_adj_slice(s: slice):
    """Returns a colon-separated string representation of a slice."""

    return "{}:{}{}".format(s.start + 1, s.stop, f":{s.step}" if s.step > 1 else '')

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
            raise ValueError("%r -> 'start' of slice is out of range (max: %d)."
                            % (display_slice(s), length))
    elif None is not s.start > s.stop:
        raise ValueError("'start' > 'stop' in slice %r."
                        % display_slice(s))

    s = s.indices(length)

    # Leaves the 'stop' attribute unchanged
    # since matrixes include the (1-indexed) 'stop' index for slicing operations.
    return slice(max(0, s[0]-1), *s[1:])


def slice_length(s: slice):
    """Returns the number of items selected by an **adjusted** slice."""

    return ceil((s.stop-s.start) / s.step)


def slice_index(s: slice, index: int):
    """
    's' -> An adjusted slice for a sequence.
    'index' -> A (0-based) index of the sequence produced by 's'.

    Returns the equivaluent of 'index' for the original sequence sliced by 's'.
    """

    return s.start + index * s.step


def original_slice(s1: slice, s2: slice):
    """
    's1' -> An adjusted slice for a sequence.
    's2' -> An adjusted slice of the sequence produced by 's1'.

    Returns the equivalent of 's2' for the original sequence sliced by 's1'.
    """

    return slice(slice_index(s1, s2.start),
                slice_index(s1, s2.stop-1) + 1,
                s1.step * s2.step
                )


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


def is_iterable(obj):
    """Checks if obj is iterable."""
    try:
        iter(obj)
    except TypeError:
        return False

    return True

