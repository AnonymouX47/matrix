"""Definitions of utility classes and functions meant for the main classes."""

def adjust_slice(s, stop):
    """Changes a slice object for a 1-indexed sequence to the equivalent 0-index form"""

    s = s.indices(stop)
    return slice(max(0, s[0]-1), *s[1:])

def valid_slice(s):
    return all((x or 0) >= 0 for x in (s.start, s.stop, s.step))

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

    lengths = [len(row) for row in array]

    return min(lengths), max(lengths), len(array), array


class InitDocMeta(type):
    """A metaclass that sets the docstring of it's instances' `__init__` to the class'"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set `__init__` method's docstring to that of the class.
        self.__init__.__doc__ = self.__doc__

