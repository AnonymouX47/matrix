"""Definitions of utility classes and functions meant for the main classes."""

def adjust_slice(s: slice, stop: int) -> slice:
    """
    Changes a slice for a 1-indexed sequence to the equivalent 0-index form.

    'stop' is the length of the sequence for which the slice is being adjusted.
    """

    s = s.indices(stop)

    # Leaves the 'stop' attribute unchanged
    # since matrixes include the (1-indexed) 'stop' index for slicing operations.
    return slice(max(0, s[0]-1), *s[1:])


def valid_slice(s: slice):
    """Returns a boolean indicating if the given slice is valid for a matrix."""

    return (all(x is None or x > 0 for x in (s.start, s.stop, s.step))
            and (s.stop is None or (s.start or 1) <= s.stop))


def check_iterable(iterable):
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
        raise TypeError("The array should be an iterable"
                        " of iterables of integers.") from None

    if array:
        lengths = [len(row) for row in array]
    else:
        raise TypeError("The given iterable is empty.")

    return min(lengths), max(lengths), len(array), array


class InitDocMeta(type):
    """A metaclass that sets the docstring of it's instances' `__init__` to the class'"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set `__init__` method's docstring to that of the class.
        self.__init__.__doc__ = self.__doc__

