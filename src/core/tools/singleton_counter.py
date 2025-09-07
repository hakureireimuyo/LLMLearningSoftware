import threading
# ================= 单例计数器 =================
class SingletonCounter:
    _instance = None
    _counters = {}  # 按模型类型分别计数
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def get_next_number(self, model_name: str) -> int:
        with self._lock:
            current = self._counters.get(model_name, 1)
            self._counters[model_name] = current + 1
            return current
