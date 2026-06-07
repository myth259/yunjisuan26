#!/bin/bash
# B-2 性能基准测试：串行 + MPI 1P/2P/4P 各跑 3 次
echo "=============================================="
echo "  B-2 Performance Benchmark — Trapezoidal"
echo "  N = 100,000,000 intervals"
echo "=============================================="
echo ""

# ----- 串行基准 (3 次) -----
echo ">>> [1] Serial Baseline (3 runs) <<<"
for i in 1 2 3; do
    echo "--- Serial Run #$i ---"
    python /scripts/trap_serial.py
    echo ""
done

# ----- MPI 1 进程 (3 次) -----
echo ">>> [2] MPI 1 Process (3 runs) <<<"
for i in 1 2 3; do
    echo "--- MPI 1P Run #$i ---"
    OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
        OMPI_MCA_rmaps_base_oversubscribe=1 mpirun -np 1 python /scripts/trap_mpi.py
    echo ""
done

# ----- MPI 2 进程 (3 次) -----
echo ">>> [3] MPI 2 Processes (3 runs) <<<"
for i in 1 2 3; do
    echo "--- MPI 2P Run #$i ---"
    OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
        OMPI_MCA_rmaps_base_oversubscribe=1 mpirun -np 2 python /scripts/trap_mpi.py
    echo ""
done

# ----- MPI 4 进程 (3 次) -----
echo ">>> [4] MPI 4 Processes (3 runs) <<<"
for i in 1 2 3; do
    echo "--- MPI 4P Run #$i ---"
    OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
        OMPI_MCA_rmaps_base_oversubscribe=1 mpirun -np 4 python /scripts/trap_mpi.py
    echo ""
done

echo "=============================================="
echo "  Benchmark Complete!"
echo "=============================================="

# 输出汇总表格
echo ""
echo "+------------------+----------+----------+----------+-----------+"
echo "| Config           |  Run 1   |  Run 2   |  Run 3   |  Average  |"
echo "+------------------+----------+----------+----------+-----------+"
echo "| Serial (1P)      |  <---    extract from above    --->       |"
echo "| MPI 1P           |  <---    extract from above    --->       |"
echo "| MPI 2P           |  <---    extract from above    --->       |"
echo "| MPI 4P           |  <---    extract from above    --->       |"
echo "+------------------+----------+----------+----------+-----------+"
