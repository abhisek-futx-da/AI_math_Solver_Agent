# Probability - Formulas and Rules

## Basic definitions
- P(A) = number of favorable outcomes / total outcomes (classical)
- 0 ≤ P(A) ≤ 1; P(sample space) = 1
- P(A') = 1 - P(A)

## Addition rule
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
- If A, B mutually exclusive: P(A ∪ B) = P(A) + P(B)

## Conditional probability
- P(A|B) = P(A ∩ B) / P(B), P(B) > 0
- P(A ∩ B) = P(B) · P(A|B) = P(A) · P(B|A)

## Independence
- A, B independent iff P(A ∩ B) = P(A) · P(B) or P(A|B) = P(A)

## Bayes' theorem
- P(A|B) = P(B|A) P(A) / P(B)

## Common distributions
- Binomial: P(X=k) = C(n,k) p^k (1-p)^(n-k); E[X]=np, Var(X)=np(1-p)
- Constraints: 0 ≤ p ≤ 1, n positive integer, k = 0,1,...,n
