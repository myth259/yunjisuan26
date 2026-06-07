# trap_mpi_nb.py — 梯形积分（MPI 非阻塞通信，Isend/Irecv）
# 算法：同 trap_mpi.py，但用非阻塞通信实现计算与等待重叠
# 通信模式：点对点非阻塞（Rank 0 并发 Irecv，其他进程 Isend）
# 数据流：Rank 1,2,3 → Isend → Rank 0 → Irecv → Wait 汇总
from mpi4py import MPI
import math
import time
import numpy as np


def f(x):
    """被积函数 f(x) = sin(x)"""
    return math.sin(x)


if __name__ == "__main__":
    # ============================================================
    # [MPI 通信原语 1] 获取通信域、进程编号、总进程数
    # ============================================================
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    a, b = 0.0, math.pi
    N = 100_000_000
    h = (b - a) / N

    # ---- 块分解（与阻塞版相同）---------------------------------
    n_local = N // size
    start = rank * n_local + 1
    end = start + n_local
    if rank == size - 1:
        end = N

    t0 = time.time()

    # ---- 本地计算（各进程独立执行）-----------------------------
    local_sum = 0.0
    for i in range(start, end):
        x = a + i * h
        local_sum += f(x)

    # ============================================================
    # 非阻塞通信模式：Rank 0 并发接收，其他进程异步发送
    #
    # [MPI 通信原语 2] comm.Irecv(buf, source, tag)
    # 功能：非阻塞接收，立即返回 Request 对象，不等待数据到达
    # 数据流向：指定源进程 → 本地 buf（后台传输）
    # 优势：可同时向多个源发起接收请求，无需串行等待
    #
    # [MPI 通信原语 3] comm.Isend(buf, dest, tag)
    # 功能：非阻塞发送，立即返回 Request 对象，不等待接收方确认
    # 数据流向：本地 buf → 目标进程（后台传输）
    # 优势：发送方可继续执行后续代码（本场景中发送完即结束）
    #
    # [MPI 通信原语 4] req.Wait()
    # 功能：阻塞等待该 Request 对应的通信完成
    # 用于 Irecv 后确保数据已到达 buf 再读取
    # ============================================================
    if rank == 0:
        # Rank 0（根进程）：并发创建 Irecv 请求，接收所有 Worker 的 local_sum
        total_sum = local_sum
        bufs = []   # 存放各进程的接收缓冲区
        reqs = []   # 存放非阻塞接收请求句柄

        for src in range(1, size):
            # 为每个源进程分配独立的接收缓冲区（避免覆盖）
            b = np.zeros(1, dtype=np.float64)
            # Irecv：非阻塞接收，后台传输 src→buf
            req = comm.Irecv(b, source=src, tag=src)
            reqs.append(req)
            bufs.append(b)

        # 等待所有非阻塞接收完成（可按任意顺序 Wait）
        for req in reqs:
            req.Wait()

        # 汇总所有接收到的 local_sum
        for b in bufs:
            total_sum += b[0]

        elapsed = time.time() - t0
        result = h * ((f(a) + f(b)) / 2.0 + total_sum)
        print(f"=== MPI Non-blocking {size}P ===")
        print(f"  f(x) = sin(x), 区间 [{a}, {b}]")
        print(f"  区间数 N = {N:,}")
        print(f"  进程数 = {size}")
        print(f"  积分结果 = {result:.10f}")
        print(f"  理论值   = 2.0000000000")
        print(f"  误差     = {abs(result - 2.0):.10e}")
        print(f"  总耗时   = {elapsed:.4f}s")
    else:
        # Worker 进程：非阻塞发送本地计算结果给 Rank 0
        b = np.array([local_sum], dtype=np.float64)
        # Isend：非阻塞发送，立即返回（后台传输 b→rank 0）
        comm.Isend(b, dest=0, tag=rank)
        # 注意：此处未显式 Wait，因为进程即将退出，
        # MPI_Finalize 会确保所有 pending 通信完成
