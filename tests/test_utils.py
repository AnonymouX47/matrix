#! /usr/bin/env pytest

import pytest

from matrix.utils import *
from matrix.components.elements import Element, to_Element


def test_display_slice():
    tests = (
                ((None,), ":"),
                ((None, 2), ":2"),
                ((None, None, 2), "::2"),
                ((None, 2, -1), ":2:-1"),
                ((2,), ":2"),
                ((2, 5), "2:5"),
                ((2, None, -1), "2::-1"),
                ((None, 2, -1), ":2:-1"),
                ((1, 5, -1), "1:5:-1"),
            )
    for args, string in tests:
        assert display_slice(slice(*args)) == string

def test_display_adj_slice():
    tests = (
                ((0, 4, 1), "1:4"),
                ((2, 4, 2), "3:4:2"),
            )
    for args, string in tests:
        assert display_adj_slice(slice(*args)) == string

def test_adjust_slice():
    tests = (
                # Whole slice
                (slice(5), slice(0, 5, 1)),
                (slice(1, 5), slice(0, 5, 1)),
                (slice(1, 5, 1), slice(0, 5, 1)),
                (slice(None, 5, 1), slice(0, 5, 1)),
                (slice(None, None, 1), slice(0, 5, 1)),
                (slice(None, None, None), slice(0, 5, 1)),
                (slice(1, None, 1), slice(0, 5, 1)),
                # With step > 1
                (slice(1, 5, 2), slice(0, 5, 2)),
                (slice(None, 5, 2), slice(0, 5, 2)),
                (slice(None, None, 2), slice(0, 5, 2)),
                (slice(1, None, 2), slice(0, 5, 2)),
                # Others
                (slice(3, 4), slice(2, 4, 1)),
                (slice(3, 6), slice(2, 5, 1)),
                (slice(100), slice(0, 5, 1)),
            )
    for s1, s2 in tests:
        adjust_slice(s1, 5) == s2

    tests = (
                (slice)
            )
    for s in (slice(0, None), slice(0), slice(None, None, 0), slice(-10)):
        with pytest.raises(ValueError, match=".* less than 1."):
            adjust_slice(s, 5)
    with pytest.raises(ValueError, match=".* 'start' of slice."):
        adjust_slice(slice(6, None), 5)
    with pytest.raises(ValueError, match="'start' > 'stop' .*"):
        adjust_slice(slice(6, 4), 5)

def test_slice_length():
    assert slice_length(slice(0, 4, 1)) == 4
    assert slice_length(slice(1, 4, 2)) == 2
    assert slice_length(slice(5, 6, 7)) == 1

def test_slice_index():
    tests = (
                ((0, 4, 1), 0, 0),
                ((0, 4, 1), 1, 1),
                ((0, 4, 2), 0, 0),
                ((0, 4, 2), 1, 2),
                ((1, 4, 1), 0, 1),
                ((1, 4, 1), 1, 2),
                ((1, 4, 2), 0, 1),
                ((1, 4, 2), 1, 3),
            )
    for args, index, result in tests:
        assert slice_index(slice(*args), index) == result

def test_original_slice():
    # Theoretically, if `slice_index()` works properly, this also works properly.
    pass

def test_is_iterable():
    for obj in ([], (), '', {}, (x for x in 'x'), b'', set()):
        assert is_iterable(obj)
    for obj in (2, 2., 2j):
        assert not is_iterable(obj)

def test_valid_container():
    it = range(5)
    for iterable in (it, list(it), tuple(it), (x for x in it)):
        it_ = valid_container(iterable)
        assert len(it) == len(it_)
        assert all(isinstance(x, Element) for x in it_)
        assert all(to_Element(x) == y for x, y in zip(it, it_))
    it = (5, 7.9, Element(6.9))
    for iterable in (it, list(it), (x for x in it)):
        it_ = valid_container(iterable)
        print(it, it_)
        assert len(it) == len(it_)
        assert all(isinstance(x, Element) for x in it_)
        # Excludes the gen_exp
        assert all(to_Element(x) == y for x, y in zip(it, it_))
    assert valid_container(range(2), 2)
    # Errors
    for x in (2, ['2']):
        with pytest.raises(TypeError):
            valid_container(x)
    with pytest.raises(ValueError):
        valid_container([2, 3], 3)

def test_valid_2D_iterable():
    it = [
           (5, 7.9, Element(6.9)),
           range(5),
           [],
           (x for x in range(10)),
         ]
    result = valid_2D_iterable(it)

    assert len(result) == 4
    assert result[0] == 0
    assert result[1] == 10
    assert result[2] == 4
    assert isinstance(result[3], list)
    assert all(isinstance(row, list) for row in result[3])
    assert all(
                # Excludes the gen_exp
                all(to_Element(x) == y for x, y in zip(r1, r2))
                for r1, r2 in zip(it, result[3])
              )
    # Errors
    for arg in (12, [[2], 2]):
        with pytest.raises(TypeError, match=".* iterable of iterables."):
            valid_2D_iterable(arg)
    with pytest.raises(TypeError, match=".* inner iterables."):
        valid_2D_iterable([(2, 3.0), [2j, 2.0]])
    with pytest.raises(ValueError, match=".* empty."):
        valid_2D_iterable([])



#Tests for mangled_attr()

@mangled_attr()
class A:
    __a_class = "A.a"
    def __init__(self):
        self.__a_self = "A().a"

@A._register
class TestA:
    def test(self):
        a = A()
        assert a.__a_class == "A.a"
        assert a.__a_self == "A().a"
        # Cannot be referenced via the class
        with pytest.raises(AttributeError):
            A.__a_class

class B(A):
    __b_class = "B.b"
    def __init__(self):
        super().__init__()
        self.__b_self = "B().b"

@B._register  # Is actually registered to A
class TestB:
    def test(self):
        b = B()
        assert b.__a_class == "A.a"
        assert b.__a_self == "A().a"
        # B was not decorated with `mangle_attr()`
        with pytest.raises(AttributeError):
            b.__b_class
        with pytest.raises(AttributeError):
            b.__b_self

@mangled_attr()
class C(B):
    __c_class = "C.c"
    def __init__(self):
        super().__init__()
        self.__c_self = "C().c"

# Multi-level decoration
@C._register
@B._register  # Is actually registered to A
class TestC:
    def test(self):
        c = C()
        assert c.__a_class == "A.a"
        assert c.__a_self == "A().a"
        assert c.__c_class == "C.c"
        assert c.__c_self == "C().c"
        with pytest.raises(AttributeError):
            c.__b_class
        with pytest.raises(AttributeError):
            c.__b_self

