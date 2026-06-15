"""
缓存工具模块
职责：Redis 连接管理、缓存读写、过期策略
"""
import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class CacheUtil:
    """Redis 缓存工具类（带内存缓存降级）"""

    def __init__(self):
        self._client = None
        self._memory_cache = {}  # 内存缓存作为降级方案

    def get_client(self):
        """获取 Redis 客户端（延迟初始化）"""
        if self._client is None:
            import redis
            try:
                password = os.getenv("REDIS_PASSWORD", None)
                if password and password.strip():
                    self._client = redis.Redis(
                        host=os.getenv("REDIS_HOST", "localhost"),
                        port=int(os.getenv("REDIS_PORT", 6379)),
                        db=int(os.getenv("REDIS_DB", 0)),
                        password=password,
                        decode_responses=True,
                        socket_connect_timeout=1,
                        socket_timeout=1,
                        retry_on_timeout=False
                    )
                else:
                    self._client = redis.Redis(
                        host=os.getenv("REDIS_HOST", "localhost"),
                        port=int(os.getenv("REDIS_PORT", 6379)),
                        db=int(os.getenv("REDIS_DB", 0)),
                        decode_responses=True,
                        socket_connect_timeout=1,
                        socket_timeout=1,
                        retry_on_timeout=False
                    )
                self._client.ping()
                logger.info("Redis 连接成功")
            except Exception as e:
                logger.warning(f"Redis 连接失败，将使用内存缓存: {e}")
                self._client = None
        return self._client

    def _memory_set(self, key: str, value: Any, ttl: int):
        """内存缓存写入"""
        import time
        self._memory_cache[key] = {
            'value': value,
            'expire_at': time.time() + ttl
        }

    def _memory_get(self, key: str) -> Optional[Any]:
        """内存缓存读取"""
        import time
        item = self._memory_cache.get(key)
        if item:
            if time.time() < item['expire_at']:
                return item['value']
            else:
                del self._memory_cache[key]
        return None

    def _memory_delete(self, *keys: str):
        """内存缓存删除"""
        for key in keys:
            if key in self._memory_cache:
                del self._memory_cache[key]

    def _memory_exists(self, key: str) -> bool:
        """内存缓存检查"""
        import time
        item = self._memory_cache.get(key)
        if item:
            if time.time() < item['expire_at']:
                return True
            else:
                del self._memory_cache[key]
        return False

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """写入缓存"""
        client = self.get_client()
        if client is None:
            # 降级到内存缓存
            try:
                self._memory_set(key, value, ttl)
                return True
            except Exception as e:
                logger.error(f"内存缓存写入失败 [{key}]: {e}")
                return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis缓存写入失败 [{key}]: {e}")
            # 降级到内存缓存
            try:
                self._memory_set(key, value, ttl)
                return True
            except Exception as e2:
                logger.error(f"内存缓存写入也失败 [{key}]: {e2}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """读取缓存"""
        client = self.get_client()
        if client is None:
            # 降级到内存缓存
            return self._memory_get(key)
        try:
            value = client.get(key)
            if value is None:
                # Redis没有，尝试从内存缓存获取
                return self._memory_get(key)
            # 尝试 JSON 解析
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis缓存读取失败 [{key}]: {e}")
            # 降级到内存缓存
            return self._memory_get(key)

    def delete(self, *keys: str) -> bool:
        """删除缓存"""
        client = self.get_client()
        if client is None:
            self._memory_delete(*keys)
            return True
        try:
            client.delete(*keys)
            self._memory_delete(*keys)
            return True
        except Exception as e:
            logger.error(f"缓存删除失败 [{keys}]: {e}")
            self._memory_delete(*keys)
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        client = self.get_client()
        if client is None:
            return self._memory_exists(key)
        try:
            return bool(client.exists(key))
        except Exception as e:
            logger.error(f"缓存检查失败 [{key}]: {e}")
            return self._memory_exists(key)

    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        return self.get(f"task:{task_id}")

    def set_task_status(self, task_id: str, status: str, ttl: int = 3600) -> bool:
        """设置任务状态"""
        return self.set(f"task:{task_id}", status, ttl)

    def get_result(self, task_id: str) -> Optional[dict]:
        """获取分析结果"""
        return self.get(f"result:{task_id}")

    def set_result(self, task_id: str, result: dict, ttl: int = 7200) -> bool:
        """缓存分析结果"""
        return self.set(f"result:{task_id}", result, ttl)

    def close(self):
        """关闭连接"""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass


# 全局单例
cache = CacheUtil()
