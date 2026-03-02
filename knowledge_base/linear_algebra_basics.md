# Linear Algebra Basics

## Vectors
- Dot product: a·b = a₁b₁ + a₂b₂ + ... ; |a| = √(a·a)
- a·b = |a||b| cos θ; orthogonal when a·b = 0

## Matrices
- Matrix multiplication: (AB)_{ij} = Σ_k A_{ik} B_{kj}; columns of A must equal rows of B
- Determinant 2×2: det([[a,b],[c,d]]) = ad - bc
- Inverse: A A⁻¹ = I; exists iff det(A) ≠ 0. For 2×2: A⁻¹ = (1/det(A)) [[d,-b],[-c,a]]

## Linear systems
- Ax = b: unique solution if A invertible; infinite if dependent; none if inconsistent
- Row reduction / Gaussian elimination to solve

## Eigenvalues (basics)
- λ is eigenvalue of A if Av = λv for some v ≠ 0; solve det(A - λI) = 0
- For 2×2: λ² - (trace)λ + det = 0
