# JEE Problem-Solving Strategies & Common Patterns

## General approach for JEE math
1. **Identify the type**: Is it algebraic, trigonometric, calculus-based, or combinatorial?
2. **Look for symmetry or substitution**: Many JEE problems simplify with a clever substitution.
3. **Check boundary/edge cases**: Domain restrictions, division by zero, square root of negatives.
4. **Work backwards**: If the answer options are given, substitute them to verify.

## Algebra — Key patterns
- Quadratic with unknown coefficients: use sum/product of roots, then verify discriminant ≥ 0.
- Modulus equations: split into cases (positive / negative argument).
- Logarithmic inequality: always check domain first (argument > 0, base > 0 and ≠ 1).

## Calculus — Key patterns
- **Derivative problems**: Apply chain rule for composite functions; use product/quotient rule explicitly.
- **Maxima/minima**: Set f'(x) = 0, check sign change of f'(x) or use f''(x) test.
- **Definite integrals**: Try the property ∫₀ᵃ f(x) dx = ∫₀ᵃ f(a−x) dx to simplify.
- **Limits**: Try L'Hôpital's rule only when the form is 0/0 or ∞/∞.

## Probability — Key patterns
- Always check if events are independent before multiplying probabilities.
- Conditional probability: P(A|B) = P(A∩B) / P(B).
- Bayes' theorem: P(Aᵢ|B) = P(B|Aᵢ)P(Aᵢ) / Σ P(B|Aⱼ)P(Aⱼ).
- Complementary counting: P(at least one) = 1 − P(none).

## Linear Algebra — Key patterns
- For a system Ax = b: find |A|; if |A| ≠ 0, unique solution; if |A| = 0, check consistency.
- Eigenvalue: det(A − λI) = 0. Eigenvector: (A − λI)v = 0.

## Common mistakes to avoid
- Forgetting ± when taking square roots.
- Dropping the constant of integration in indefinite integrals.
- Ignoring domain restrictions for trig inverse functions.
- Confusing permutation P(n,r) = n!/(n−r)! with combination C(n,r) = n!/(r!(n−r)!).
- L'Hôpital's rule applied to forms other than 0/0 or ∞/∞.
