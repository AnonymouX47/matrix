#! /usr/bin/env pytest

from random import randint
import pytest

from matrix.utils import *


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
    pass

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
    # By theory, if `slice_index()` works properly, this also works properly.
    pass

def test_is_iterable():
    for obj in ([], (), '', {}, (x for x in 'x'), b'', set()):
        assert is_iterable(obj)
    for obj in (2, 2., 2j):
        assert not is_iterable(obj)

