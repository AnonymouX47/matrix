"""
Definitions for the matrix element.

Implemented and used this type because:
- It has much better support across different real number types.
- It retains integers as they're and the availabilty of big integers.
- It has better floating-point support than `float`, with extended precision.
"""

from decimal import Decimal
from functools import wraps

from .utils import MethodDecoMeta

__all__ = ("Element", "to_Element")


def numeric_deco(func):
    """
    Decorates inherited numeric methods of a class
    to support inter-operations with `float` instances.
    """

    @wraps(func)
    def wrapper(self, other, *args):
        result = func(self, other, *args)

        if result is NotImplemented and isinstance(other, float):
            result = func(
                self, Decimal(other if other.is_integer() else str(other)), *args
            )

        return result if result is NotImplemented else type(self)(result)

    return wrapper


def unary_deco(func):
    """
    Decorates inherited unary operation methods of a class
    to ensure results are of the proper type.
    """

    @wraps(func)
    def wrapper(self):
        return type(self)(func(self))

    return wrapper


numerics = [
    fmt.format(name)
    for fmt in ("__{}__", "__r{}__")
    for name in ("add sub mul truediv floordiv mod divmod pow").split(" ")
]
unaries = map("__{}__".format, "abs pos neg".split(" "))


class Element(
    Decimal,
    metaclass=MethodDecoMeta,
    decorated={numeric_deco: numerics, unary_deco: unaries},
):
    """
    A matrix element.

    Implements support for inter-operations with `float` instances
    since `decimal.Decimal` doesn't support operations with floats.
    Also, results of Decimal() methods are converted to Element() instances.
    """

    # mainly to disable abitrary atributes.
    __slots__ = ()

    def __repr__(self):
        return "%s(%r)" % (__class__.__name__, self.__str__())

    def __round__(self, *args):
        result = super().__round__(*args)

        return result if isinstance(result, int) else __class__(result)


def to_Element(value):
    """
    Converts a number to an `Element` instance in "the best way possible".

    This is required majorly to:
    - ensure better correctness and accuracy of future operations between the converted element and other elements.
    - to retain/gain the advantage of Python's big integers when possible.

    This is needed mainly due to the limited precision of `float`
    and "weird" results produced by `decimal.Decimal`'s default `float` conversion.
    """

    # Importing `..utils` while loading this module will result in circular import
    # since `..utils` imports [this function] from this module.
    from ..utils import ROUND_LIMIT

    limit = Element(f"1e-{ROUND_LIMIT}")
    if isinstance(value, float) and not value.is_integer():
        value = Element(str(value))
    elif isinstance(value, str):
        value = Element(value)

    return Element(round(value) if 0 < abs(value - round(value)) < limit else value)
