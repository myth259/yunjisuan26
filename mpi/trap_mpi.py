# trap_mpi.py — 梯形积分（MPI 并行，阻塞通信）
# 算法：∫[0,π] sin(x) dx = 2.0，梯形法数值积分
# 通信模式：主从归约（Master-Worker Reduce）
# 数据流：各 Worker 计算 local_sum → MPI_Reduce → Rank 0 汇总输出
from mpi4py import MPI
import math
import time


def f(x):
    """被积函数 f(x) = sin(x)"""
    return math.sin(x)


if __name__ == "__main__":
    # ============================================================
    # [MPI 通信原语 1] MPI.COMM_WORLD — 获取全局通信域
    # 数据流向：所有进程共享同一个通信域，用于后续集合通信
    # ============================================================
    comm = MPI.COMM_WORLD

    # ============================================================
    # [MPI 通信原语 2] comm.Get_rank() — 获取当前进程编号
    # 返回值：0 ~ size-1 的整数，rank=0 为根进程负责汇总输出
    # ============================================================
    rank = comm.Get_rank()

    # ============================================================
    # [MPI 通信原语 3] comm.Get_size() — 获取总进程数
    # 用于后续块分解，决定每个进程处理多少区间
    # ============================================================
    size = comm.Get_size()

    a, b = 0.0, math.pi
    N = 100_000_000  # 总区间数

    h = (b - a) / N  # 步长，所有进程共享

    # ---- 块分解（Block Decomposition）-------------------------
    # 将区间 [a,b] 的 N 个子区间均匀分配给 size 个进程
    # 每个进程处理 n_local 个内部采样点
    n_local = N // size
    start = rank * n_local + 1  # 本进程起始采样点索引
    end = start + n_local        # 本进程结束采样点索引
    if rank == size - 1:
        end = N                   # 末进程处理剩余区间（负载均衡）

    # ---- 本地并行计算（各进程独立执行，无需通信）---------------
    local_sum = 0.0
    for i in range(start, end):
        x = a + i * h
        local_sum += f(x)

    # ============================================================
    # [MPI 通信原语 4] comm.reduce(local_sum, MPI.SUM, root=0)
    # 功能：将所有进程的 local_sum 归约求和，结果存入 rank=0
    # 数据流向：rank 0,1,2,3 → rank 0（树形归约，O(log₂P) 通信步）
    # 通信量：每个进程发送 1 个 double（8 字节）
    # ============================================================
    t_start = time.time()
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
    t_elapsed = time.time() - t_start

    # ---- 根进程输出最终结果 ------------------------------------
    if rank == 0:
        result = h * ((f(a) + f(b)) / 2.0 + total_sum)
        print(f"=== MPI Blocking {size}P ===")
        print(f"  f(x) = sin(x), 区间 [{a}, {b}]")
        print(f"  区间数 N = {N:,}")
        print(f"  进程数 = {size}")
        print(f"  积分结果 = {result:.10f}")
        print(f"  理论值   = 2.0000000000")
        print(f"  误差     = {abs(result - 2.0):.10e}")
        print(f"  通信+同步耗时 = {t_elapsed:.4f}s")
