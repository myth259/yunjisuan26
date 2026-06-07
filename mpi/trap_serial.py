# trap_serial.py — 梯形积分（串行）
# ∫[0,π] sin(x) dx = 2.0
import math
import time


def f(x):
    return math.sin(x)


def trapezoidal(a, b, n):
    """梯形法积分，n 等分"""
    h = (b - a) / n
    total = (f(a) + f(b)) / 2.0
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


if __name__ == "__main__":
    a, b = 0.0, math.pi
    N = 100_000_000  # 1亿个区间

    start = time.time()
    result = trapezoidal(a, b, N)
    elapsed = time.time() - start

    print(f"=== Serial Trapezoidal Integration ===")
    print(f"  f(x) = sin(x), 区间 [{a}, {b}]")
    print(f"  区间数 N = {N:,}")
    print(f"  积分结果 = {result:.10f}")
    print(f"  理论值   = 2.0000000000")
    print(f"  误差     = {abs(result - 2.0):.10e}")
    print(f"  耗时     = {elapsed:.4f}s")
