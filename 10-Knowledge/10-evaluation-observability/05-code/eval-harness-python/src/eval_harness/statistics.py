"""Wilson 二项区间及 HumanEval pass@k；前提由调用者明确保证。"""
from math import comb, sqrt


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n < 1 or not 0 <= successes <= n or z <= 0:
        raise ValueError("require 0 <= successes <= n, n > 0, z > 0")
    p = successes / n
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n)) / denominator
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / denominator
    return max(0.0,center-half), min(1.0,center+half)


def pass_at_k(n: int, c: int, k: int) -> float:
    if not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    return 1.0 if n-c < k else 1 - comb(n-c,k) / comb(n,k)
