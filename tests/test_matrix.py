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


m = Matrix([[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]
          )

class TestObjectInteractions:
    def test_str(self):
        # Lines of the string representation must have uniform length
        for _ in range(50):
            ncol = randint(1, 100)
            m = Matrix(
                        (
                          (randint(0, 1000000) for _ in range(ncol))
                          for _ in range(randint(1, 100))
                        )
                      )
            lines = str(m).splitlines()
            length = len(lines[0])
            assert all(len(line) == length for line in lines)

    def test_getitem(self):
        m = Matrix(4, 4)
        arr = m._array
        # Single element
        assert isinstance(m[1, 4], Element)
        assert all(m[i+1, j+1] == arr[i][j] for i in range(4) for j in range(4))
        ## Out of range indices
        for sub in ((3, 0), (2, 5), (0, 3), (5, 2)):
            with pytest.raises(IndexError, match=".* Column .*"):
                m[sub]
        # Block-slice
        copy = m[:, :]
        assert isinstance(copy, Matrix)
        assert copy._array == m._array
        # Wrong subscript types
        for sub in (3, (2, 3.0), (3, 3, 3), (3, slice(None)), [2, 3]):
            with pytest.raises(TypeError):
                m[sub]

    def test_setitem(self):
        m = Matrix(4, 4)
        # Single element
        m[1, 1] = 20
        assert m[1, 1] == 20
        ## Wrong element types
        for elem in (2j, '2', [2], (2,)):
            with pytest.raises(TypeError, match=".* real numbers, .*"):
                m[2, 2] = elem
        ## Out of range indices
        for sub in ((3, 0), (2, 5), (0, 3), (5, 2)):
            with pytest.raises(IndexError, match=".* Column .*"):
                m[sub] = 0
        # Block-slice
        m[:2, :2] = [[20, 20]] * 2
        arr = m._array
        assert [arr[0][:2], arr[1][:2]] == [[20, 20]] * 2
        # Wrong subscript types
        for sub in (3, (2, 3.0), (3, 3, 3), (3, slice(None)), [2, 3]):
            with pytest.raises(TypeError):
                m[sub] = 0
        # Incompatible dimension
        with pytest.raises(InvalidDimension):
            for array in ([[]], [2, 2], [[2, 2]], [[2], [2]], [[2, 0], [2]]):
                m[:2, :2] = array

    def test_iter(self):
        m = randint_matrix(4, 4, range(1, 10))
        # Generator yields elements
        for elem in m: assert isinstance(elem, Element)
        # All elements
        assert len((*m,)) == m.nrow * m.ncol
        assert [*m] == sum(m._array, start=[])
        # Resize during iteration
        m_iter = iter(m)
        next(m_iter)
        m.resize(ncol=3)
        with pytest.raises(RuntimeError, match=".* resized .*"):
            next(m_iter)

        # Advanced use
        m = Matrix([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]]
                  )
        m_iter = iter(m)
        next(m_iter)
        ## Setting row
        assert m_iter.send(2) == m[2, 1]
        assert next(m_iter) == m[2, 2]
        assert all(m_iter.send(r) == m[r, 1] for r in range(1, m.nrow+1))
        ## Setting row and column
        assert m_iter.send((1, 3)) == m[1, 3]
        assert next(m_iter) == m[2, 1]
        assert all(m_iter.send((r, c)) == m[r, c]
                    for r in range(1, m.nrow+1)
                        for c in range(1, m.ncol+1)
                  )
        ## Out of range indices
        for arg in (-1, 0, 4):
            with pytest.raises(StopIteration, match="Row index .*"):
                m_iter = iter(m)
                next(m_iter)
                m_iter.send(arg)
        for arg in ((4, 3), (1, 0), (-1, 4), (0, 4)):
            with pytest.raises(StopIteration, match="Coordinate .*"):
                m_iter = iter(m)
                next(m_iter)
                m_iter.send(arg)
        ## Wrong type
        for arg in (3.0, (2, 3.0), (2.0, 3), (2.0, 3.0), [1, 2], '2'):
            with pytest.raises(StopIteration, match="Wrong type .*"):
                m_iter = iter(m)
                next(m_iter)
                m_iter.send(arg)

    def test_membership(self):
        assert all(elem in m for elem in range(1, 10))
        for x in ('1', 'b', int, [1], [1, 2, 3], (1,)):
            with pytest.raises(TypeError):
                x in m

    def test_round(self):
        assert m is not +m
        assert m._array == m._array
        assert m._array is not (+m)._array
        assert all(isinstance(elem, Element) for elem in round(m))

    def test_pos(self):
        assert m is not +m
        assert m._array == m._array
        assert m._array is not (+m)._array

    def test_neg(self):
        assert all(x == -y
                    for r1, r2 in zip(m._array, (-m)._array)
                        for x, y in zip(r1, r2)
                  )
    def test_bool(self):
        assert not bool(Matrix(1, 1))
        for _ in range(50):
            assert not Matrix(randint(1, 1001), randint(1, 1001))
        for _ in range(50):
            m = Matrix(randint(1, 1001), randint(1, 1001))
            m[1, 1] = 1
            assert m

