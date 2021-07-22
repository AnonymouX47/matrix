"""Definitions of utility classes and functions meant for the main classes."""

from decimal import Decimal
from functools import wraps
from math import ceil
from numbers import Real

from .components import to_Element


def display_slice(s: slice):
    """Returns a colon-separated string representation of a slice."""

    # `or` can't be used in case the attribute is 0.
    return "{}:{}{}".format(*(x if x is not None else '' for x in (s.start, s.stop)),
                            f":{s.step}" if s.step is not None else '')

def display_adj_slice(s: slice):
    """
    Returns a 1-based, colon-separated string representation of an **adjusted** slice.
    Expects slice objects returned by `adjust_slice()`.
    """

    return "{}:{}{}".format(s.start + 1, s.stop, f":{s.step}" if s.step > 1 else '')

def adjust_slice(s: slice, length: int) -> slice:
    """
    Changes a slice for a 1-indexed sequence to the equivalent 0-index form.

    'stop' is the length of the sequence for which the slice is being adjusted.
    """

    if any(None is not x < 1 for x in (s.start, s.stop, s.step)):
        raise ValueError("%r -> 'start', 'stop' or 'step' is less than 1."
                         % display_slice(s))
    if s.stop is None:  # 'stop' is not given...
        # Can't combine these two conditions,
        # so as not to affect the logic of the `elif` below.
        if None is not s.start > length:  # ...but 'start' is given and > `length`
            raise ValueError("%r -> 'start' of slice is out of range (max: %d)."
                             % (display_slice(s), length))
    elif None is not s.start > s.stop:
        # 'stop' is given and ('start' is given and > 'stop')
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

    # Allow the TypeError to be propagated if 'iterable' is not iterable.
    container = tuple(iterable)
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


def mangled_attr(*, _get=True, _set=True, _del=True):
    """
    Enables other classes to get, set and delete attributes having
    **mangled names** (defined in decorated classes), using the unmangled name.

    Args:
        The arguments that are true determine which methods will be decorated.
        Hence, which operations will be affected.

    Returns:
        a class decorator.

    - The other classes accessing the attributes must be decorated with or passed to
    the `_register` method of the class decorated with this function.
      - even subclasses of the class defining the attributes must be decorated
      with this method in order to access the mangled attributes.
    - Only works if the attribute is referenced within the other class's definition.
    - Works "recursively" for classes decorated with this function i.e
      - if class A is decorated by this function, and
      - B is a subclass of A and also decorated with this function
      - then, mangled attributes of both B and A can be directly accessed via
        an instance of B from within another class's definition.
      - etc...
    - Subclasses of the decorated class don't inherit this functionality,
    hence they must also be decorated with this function if desired.

    NOTE:
    - The method applied is not perfect and can give unwanted results if
    the name of the class from whose definition the attribute is referenced
    has at least a set of double underscores in-between, which is not expected.
    - This functionality comes at a slight cost, so if a mangled attribute has
    an **un-mangled** counterpart (e.g a [read-only] descriptor),
    that should be used **in the other classes** instead, whenever possible.
    """

    def deco(cls):
        """
        Overrides the getter, setter and/or deletter of cls and adds
        two extra attributes to the class (provided at least one of
        the methods is overriden):
          - '_register' -> A class method used to register other classes that
          access the mangled attributes.
          - '_registered' -> A set containing (modified) names of registered
          classes.

        Args:
            - cls -> The class to be decorated.
        Returns:
            The argument.
        """

        def retry_mangled(get_set_del):
            """
            Decorates the getter, setter or deleter of _cls_ to retry for mangled names
            after "re-mangling" the attribute name with the name of _cls_.
            """

            cls_name = cls.__name__

            @wraps(get_set_del)
            def wrapper(self, name, *args):
                # 'args' is only occupied for set operations.
                try:
                    return get_set_del(self, name, *args)
                except AttributeError as err:
                    split = name.split('__', 1)
                    if (len(split) == 2 and split[0] in cls._registered):
                        try:
                            return get_set_del(
                                            self,
                                            "_%s__%s" % (cls_name, split[1]),
                                            *args
                                            )
                        except AttributeError:
                            raise err from None
                    raise

            return wrapper


        if _get: cls.__getattribute__ = retry_mangled(cls.__getattribute__)
        if _set: cls.__setattr__ = retry_mangled(cls.__setattr__)
        if _del: cls.__delattr__ = retry_mangled(cls.__delattr__)

        if any((_get, _set, _del)):

            def _register(cls, *othercls):
                """
                Registers a/some class(es) for "re-mangling"
                of mangled attributes of _cls_ instances referenced within
                the definition of the other class(es).

                Args:
                    - cls -> Owner of the method.
                    - othercls -> The class/classes (in a tuple) to be registered.
                Returns:
                    The last argument or None if no argument was passed.
                Raises:
                    TypeError if an argument is not a class object.

                Note: It is to be set as a classmethod of the class (_cls_) having
                the attriutes with mangled names, hence can be used thus:
                    - with `@cls._register` in definition of another class
                    that accesses those attributes.
                    - Direct call to `cls._register(class1, ...)`
                    this way, it can accept multiple of the other classes at once.
                """

                for other in othercls:
                    if not isinstance(other, type):
                        raise TypeError("Only classes can be registered.")

                    # Leading underscores of the class name is stripped in mangled names.
                    cls._registered.add('_' + other.__name__.lstrip('_'))

                # Avoids an UnboundLocalError if no argument is given
                return other if othercls else None

            _register.__qualname__ = cls.__qualname__ + '._register'
            _register.__module__ = cls.__module__

            cls._register = classmethod(_register)
            cls._registered = set()

        return cls

    return deco


class MatrixIter:
    """
    Iterator class for matrix Rows and Columns.
    Mainly implemented to detect if a matrix resized upon iteration.
    Similar to the behaviour of dictionaries.

    - 'iterator' -> The underlying **iterator**,
      whose `next()` would be "yielded" on each iteration.
      This is to allow various classes with varying forms of iterations to use
      the same iterator class, and all have the benefit of the resize-detection.
    - 'matrix' -> The matrix whose component is being iterated over.

    ==NOTE:==
    1. Just as for dicts, the resize is not detected until
      the end of the current iteration or beginning of the next iteration.
      Hence, if the Error raised is handled, the matrix will be in the resized state.
    2. It achieves this definitely at the cost of performance.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ("__iter", "__matrix", "__size")

    def __init__(self, iterator, matrix):
        self.__iter = iter(iterator)  # iter() to ensure an iterator is stored.
        self.__matrix = matrix

        # for comparison of sizes during iteration,
        # to ensure the matrix hasn't been resized.
        self.__size = matrix.size

    def __iter__(self):
        return self

    def __next__(self):
        if self.__size != self.__matrix.size:
            raise BrokenMatrixView("The matrix was resized during iteration.",
                                    view_obj=self)

        return next(self.__iter)  # StopIteration is also propagated.


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


# The number of decimal places after which figures are considered insignificant.
# This value is used to subdue floating-point issues in many operations.
# Any number with a magnitude below 1e-(ROUND_LIMIT) is considered a zero.
ROUND_LIMIT = 12

