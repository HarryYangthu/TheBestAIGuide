"""Wilson 二项区间及 HumanEval pass@k；前提由调用者明确保证。"""
from math import comb, isfinite, sqrt


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """成功次数/试验次数必须是整数；z 为有限正数。返回概率区间 (low, high)。"""
    # bool 是 int 的子类，仍不是这里的计数；NaN 不能落入概率计算。
    if (type(successes) is not int or type(n) is not int
            or n < 1 or not 0 <= successes <= n
            or type(z) not in (int, float) or not isfinite(z) or z <= 0):
        raise ValueError("require integer 0 <= successes <= n, n > 0, finite z > 0")
    p = successes / n
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n)) / denominator
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / denominator
    return max(0.0, center-half), min(1.0, center+half)


def pass_at_k(n: int, c: int, k: int) -> float:
    """n 个候选中 c 个成功，无放回取 k 个，至少一个成功的组合估计。"""
    if (any(type(value) is not int for value in (n, c, k))
            or not 0 <= c <= n or not 1 <= k <= n):
        raise ValueError("require integer 0 <= c <= n and 1 <= k <= n")
    # 失败候选少于 k 个时，不可能取到全失败组合。
    return 1.0 if n-c < k else 1 - comb(n-c, k) / comb(n, k)
