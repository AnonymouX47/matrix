"""
Definitions for the matrix element.

Implemented and used this type because:
- It has much better support across different real number types.
- It retains integers as they're and the availabilty of big integers.
- It has better floating-point support than `float`, with extended precision.
"""

from ..utils import Decimal

__all__ = ["Element", "to_Element"]


class Element(Decimal):
    """
    A matrix element.

    Had to implement support for inter-operations with `float` instances
    since `decimal.Decimal` doesn't support operations with floats.
    """

    __slots__ = ()

    def __repr__(self):
        return "%s(%r)" % (__class__.__name__, self.__str__())

    def __abs__(self):
        return __class__(super().__abs__())

    def __pos__(self):
        return __class__(super().__pos__())

    def __neg__(self):
        return __class__(super().__neg__())

    def __add__(self, other):
        result = super().__add__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__add__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __sub__(self, other):
        result = super().__sub__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__sub__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __mul__(self, other):
        result = super().__mul__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__mul__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __truediv__(self, other):
        result = super().__truediv__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__truediv__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __floordiv__(self, other):
        result = super().__floordiv__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__floordiv__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __mod__(self, other):
        result = super().__mod__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__mod__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __divmod__(self, other):
        result = super().__divmod__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__divmod__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __pow__(self, other, mod=None):
        result = super().__pow__(other, mod)

        if result is NotImplemented and isinstance(other, float):
            result = super().__pow__(
                        __class__(other if other.is_integer() else str(other)), mod)

        return result if result is NotImplemented else __class__(result)

    def __radd__(self, other):
        result = super().__radd__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__radd__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rsub__(self, other):
        result = super().__rsub__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rsub__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rmul__(self, other):
        result = super().__rmul__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rmul__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rtruediv__(self, other):
        result = super().__rtruediv__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rtruediv__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rfloordiv__(self, other):
        result = super().__rfloordiv__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rfloordiv__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rmod__(self, other):
        result = super().__rmod__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rmod__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rdivmod__(self, other):
        result = super().__rdivmod__(other)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rdivmod__(
                        __class__(other if other.is_integer() else str(other)))

        return result if result is NotImplemented else __class__(result)

    def __rpow__(self, other, mod=None):
        result = super().__rpow__(other, mod)

        if result is NotImplemented and isinstance(other, float):
            result = super().__rpow__(
                        __class__(other if other.is_integer() else str(other)), mod)

        return result if result is NotImplemented else __class__(result)


def to_Element(value):
    """
    Converts a `float` instance to an `Element` instance in "the best way possible".

    This is required majorly to:
    - ensure better correctness and accuracy of future operations between the converted element and other elements.
    - to retain/gain the advantage of Python's big integers when possible.

    This is needed mainly due to the limited precision of `float`
    and "weird" results produced by `decimal.Decimal`'s default `float` conversion.
    """

    if isinstance(value, float) and not value.is_integer():
        value = str(value)

    return Element(value)

