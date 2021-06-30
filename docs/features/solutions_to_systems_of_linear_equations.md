# Solutions to systems of linear equations

This can be achieved in two ways using the package:

* Gaussian Elimination: A convenience function `solve_linear_system()` is provided at the package's top-level for this.
  * The  function accepts only two arguments, the matrix of coefficients and the matrix of constants and return a tuple containing the solution set.
* Inverse method i.e `x = ~A @ b`.

NOTE: The shouldn't be any much performance difference between the two means since the inverse operation also uses Gaussian Elimination.

