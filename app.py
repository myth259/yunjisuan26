"""Flask 后端 API — 云计算课程设计"""
import os
from flask import Flask, jsonify
import redis

app = Flask(__name__)

# 从环境变量读取 Redis 配置（由 K8s ConfigMap / Secret 注入）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# 初始化 Redis 客户端
redis_client = None
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD if REDIS_PASSWORD else None,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    redis_client.ping()
    print(f"[OK] 已连接 Redis: {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"[WARN] Redis 连接失败（可能尚未部署）: {e}")


@app.route("/api/ping")
def ping():
    """健康检查接口 — 用于 ELB 探活和验收"""
    return jsonify({"status": "ok"})


@app.route("/api/info")
def info():
    """返回 Redis 连接信息（用于调试）"""
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    return jsonify({
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
        "redis_status": redis_status,
    })


@app.route("/api/counter")
def counter():
    """Redis 计数器示例 — 每次访问 +1，验证 Redis 读写正常"""
    if redis_client:
        count = redis_client.incr("visit_count")
        return jsonify({"visit_count": count})
    return jsonify({"error": "Redis not available"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
