# Features

An instance of the `Matrix` class is a **mutable** object modelling a mathematical matrix.
- It implements common matrix operations and properties.
- It is completely **1-indexed**.
- The **_stop_** index is always **included** in any **slice**.

Every matrix element is an instance of a subclass (`Element`) of python's `decimal.Decimal` so they support all operations and methods implemented by `decimal.Decimal` but the subclass, `Element` implements support for inter-operation with `float` instances.

Even though a `Matrix` instance mutable, it provides a few methods that return a new matrix instance.

For demonstrations of the features described here, see the [sample files](https://github.com/AnonymouX47/matrix/tree/main/samples).

## Sub-sections

- [Matrix Initialization](matrix_initialization.md)
- [Matrix Object Interactions](matrix_object_interactions.md)
- [Matrix Properties](matrix_properties.md)
- [Matrix Operations](matrix_operations.md)
- [Tests for matrix properties and special matrices](tests_for_matrix_properties_and_special_matrices.md)
- [Matrix views](matrix_views.md)
- [Other operations on matrices](other_operations_on_matrices.md)
- [Solutions to systems of linear equations](solutions_to_systems_of_linear_equations.md)

