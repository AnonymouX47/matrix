#! /usr/bin/env pytest

from random import randint
import pytest

from matrix import *
from matrix.components import Element

class TestInit:
    """Tests for matrix initialization"""

    def test_args(self):
        """Test for constructor arguments"""

        # Positional-only parameters
        with pytest.raises(TypeError, match=".* positional-only .*"):
            Matrix(rows_array=2)
        # Argument type combination.
        # If any should fail, pytest shows the args to Matrix.__init__()
        for args in ((4,), (2.0, 5), (5, 2.0), ([[2]], 1)):
            with pytest.raises(TypeError, match="Constructor arguments .*"):
                Matrix(*args)

    def test_size_init(self):
        """Test for Matrix initialization by size"""

        # Valid dimensions
        for _ in range(50):
            m, n = randint(1, 1000), randint(1, 1000)
            mat = Matrix(m, n)
            assert (mat.nrow == len(mat._array) == m
                    and mat.ncol == len(mat._array[0]) == n)
            assert all(not any(row) for row in mat._array)  # Null
        # Invalid dimensions
        for _ in range(50):
            with pytest.raises(InvalidDimension):
                Matrix(randint(-1000, 0), randint(-1000, 0))

    def test_array_init(self):
        """Tests for matrix initialization by array"""

        # Input checks
        ## Empty inner iterables
        with pytest.raises(ValueError, match=".* inner .*"):
            Matrix([[], []])
        ## No zfill
        for _ in range(50):
            ncol = randint(2, 100)
            nrow = randint(2, 100)
            array = [[1]*randint(0, ncol) for _ in range(nrow-2)] 
            array.insert(0, [1]*ncol)
            array.insert(nrow, [])
            with pytest.raises(ValueError, match=".*zfill.*"):
                Matrix(array)
        # With zfill
        for _ in range(50):
            ncol = randint(2, 100)
            nrow = randint(2, 100)
            lengths = [randint(0, ncol) for _ in range(nrow-1)] 
            array = [[1]*i for i in lengths] 
            long_row_index = randint(0, nrow-1)
            lengths.insert(long_row_index, ncol)
            array.insert(long_row_index, [1]*ncol)
            m = Matrix(array, True)
            assert all(len(row) == ncol and not any(row[i:])
                       for i, row in zip(lengths, m._array))

