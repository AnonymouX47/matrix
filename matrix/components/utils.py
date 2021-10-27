"""
Utilities for matrix components

Most importantly created to prevent circular imports.
"""

from operator import setitem

__all__ = ("MethodDecoMeta",)


class MethodDecoMeta(type):
    """
    Decorates specified methods of a class, including those inherited.
    Inherited methods will be overriden since decorated methods
    will be stored in the new class' namespace.
    Can decorate multiple sets of methods with different decorators.

    Args:
        - The positional arguments are the same as for `type()`.
        - 'decorated' -> A dictionary mapping each decorator to an iterable
        of strings containing the names of the methods to be decorated
        with that particular decorator.
        e.g {deco1: ["__add__", "__sub__"], deco2: ("cool", "show")}
        Note:
            - Leverages on the hashability of functions and classes.
            - The decorators should accept only one argumnent,
                the object to be decorated.
            - Any other argument to the decorator can be externally
                passed using `functools.partial` or the likes.

    NOTE:
    - For **non-instance methods**, the decorator should expect and return
    a function object. The extraction and re-creation of the appropriate
    method wrapper will be handled by this metaclass.
    - To use multiple decorators on the same method, simply include
    the method name in the iterables for the different decorators
    **with the decorators in the desired order**.
    - This metaclass can also be used for modification of any attribute
    of the class, not just methods but note that the decorator must take
    this into consideration.
    """

    def __new__(cls, name, bases, namespace, *, decorated=None, **kwds):
        """
        Updates attributes in the namespace of the new class
        using the decorators and order specified in 'decorated'.
        """

        # The mro will be needed for the resolution of inherited attributes.
        new_cls = type.__new__(cls, name, bases, namespace, **kwds)

        # Subclasses of an instance might not want to decorated anything.
        if decorated is None:
            return new_cls

        if not isinstance(decorated, dict):
            raise TypeError("'decorated' must be a dictionary.")

        error = 0
        errors = (
            None,
            TypeError("The values in 'decorated' must contain strings only."),
            TypeError("The decorators must be callable."),
            TypeError("All values in 'decorated' must be iterable."),
        )

        # It's **less costly** to ask for forgiveness than permission
        # since any program using this shouldn't even proceed
        # in the case of any of these errors.

        # Also, it's safe to raise errors after partial modification
        # of the namespace since the class won't be created
        # and in a case where the metaclass is explicity called,
        # the namespace dict normally shouldn't be used for anything else.
        try:
            for deco, attrs in decorated.items():
                for attr in attrs:
                    if not isinstance(attr, str):
                        error = 1
                        return  # A `break` is not sufficient in a nested loop.
                    try:
                        # Standard Attribute Resolution (with possible repetition)
                        for _cls in new_cls.__mro__ + cls.__mro__:
                            if attr in _cls.__dict__:
                                obj = _cls.__dict__.get(attr)
                                setitem(
                                    namespace,
                                    attr,
                                    (
                                        classmethod(deco(obj.__func__))
                                        if isinstance(obj, classmethod)
                                        else staticmethod(deco(obj.__func__))
                                        if isinstance(obj, staticmethod)
                                        else deco(obj)
                                    ),
                                )
                                break
                        else:
                            raise AttributeError("The class has no attribute %r." % attr)
                    except TypeError as err:
                        print(err)
                        error = 2
                        return  # A `break` is not sufficient in a nested loop.
        except TypeError:
            error = 3
        finally:
            if error:
                raise errors[error]

        return type.__new__(cls, name, bases, namespace, **kwds)
