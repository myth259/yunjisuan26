# 云计算课程设计 (SCAI004712)

**成员：** 张耀升 (2023112490) 王文桐（2023112494）

---

## 目录结构

```
├── backend/                    # Flask 后端
│   ├── app.py                  # API 服务 (/api/ping, /api/counter, /api/info)
│   ├── Dockerfile              # 多阶段构建 (builder + runtime)
│   └── requirements.txt        # flask, redis, requests
├── frontend/                   # Nginx 前端
│   ├── Dockerfile              # nginx:1.25-alpine
│   ├── nginx.conf              # K8s 反向代理配置
│   ├── nginx-local.conf        # 本地 docker-compose 代理配置
│   └── static/
│       └── index.html          # 前端页面 (学号/姓名)
├── k8s/                        # Kubernetes 资源定义
│   ├── backend-deployment.yaml # Flask 后端 Deployment
│   ├── redis-deployment.yaml   # Redis Deployment + PVC
│   ├── frontend-deployment.yaml# Nginx 前端 Deployment
│   ├── services.yaml           # LoadBalancer + ClusterIP
│   ├── configmap.yaml          # backend-config + nginx-config
│   ├── secret.yaml             # Redis 密码 Secret
│   ├── pvc.yaml                # csi-disk 10Gi PVC
│   └── hpa.yaml                # 后端 HPA (min=1, max=4, CPU 60%)
├── mpi/                        # MPI 并行计算 (方向 B)
│   ├── Dockerfile              # MPI 环境镜像 (OpenMPI 4.2.1 + mpi4py)
│   ├── trap_serial.py          # 串行梯形积分基准
│   ├── trap_mpi.py             # 阻塞版 MPI 梯形积分 (comm.reduce)
│   ├── trap_mpi_nb.py          # 非阻塞版 MPI 梯形积分 (Isend/Irecv)
│   ├── pi_mpi.py               # π 值蒙特卡洛估算 (MPI 验证)
│   ├── mpijob.yaml             # MPIJob CR (kubeflow.org/v1)
│   ├── b2-pod.yaml             # B-2 性能基准测试 Pod
│   └── b2_benchmark.sh         # B-2 基准测试脚本
└── docker-compose.yml          # 本地三服务编排
```

## 环境信息

- **云平台：** 华为云 CCE (cn-north-4)
- **容器引擎：** Docker → SWR 镜像仓库
- **K8s 版本：** v1.35+ (Yangtse CNI)
- **MPI 环境：** OpenMPI 4.2.1 + mpi4py + MPI Operator (kubeflow.org/v2beta1)
