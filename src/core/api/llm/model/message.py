import threading
from typing import List, Dict, Union, Optional, Callable, Deque,  get_args, get_origin
import inspect
from collections import deque
import logging
from dataclasses import dataclass
from queue import Queue
import time
from .allocator import MessageIDAllocator

# 配置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("SyncMessageManager")
logger.addHandler(logging.NullHandler())  # 添加空处理器，不输出到任何地方

@dataclass
class CompressionResult:
    """压缩操作的结果数据结构。
    
    Attributes:
        message_ids: 被压缩的原始消息ID列表
        compressed_msg: 压缩后的消息字典，压缩失败时为None
        start_index: 原始消息在队列中的起始位置索引
    """
    message_ids: List[str]   # 被压缩的原始消息ID
    compressed_msg: Union[Dict,None]      # 压缩后的消息
    start_index: int         # 在队列中的起始位置

class Message:
    """支持多线程压缩的对话上下文管理器。
    
    记录上下文,并且增加了对上下文的管理
    实现消息队列管理、动态压缩和token超限处理功能，支持多线程操作。

    Attributes:
        raw_id_allocator: 原始消息ID分配器
        compressed_id_allocator: 压缩消息ID分配器
        system_pompmts: 受保护的系统消息列表
        message_queue: 按时间排序的对话消息队列
        current_context_tokens: 当前上下文token计数
        max_context_tokens: 允许的最大token阈值
        compression_ratio: 触发压缩时的消息处理比例
        compression_callback: 外部提供的压缩回调函数
        lock: 线程同步锁
        compression_queue: 压缩任务队列
        compression_results: 待应用的压缩结果缓存
        compression_thread: 后台压缩工作线程
        last_operation: 记录上次操作类型及参数
    """
    
    def __init__(
        self,
        session: str,
        max_context_tokens: int = 1024*64,
        compression_ratio: float = 0.3,
        raw_id_start: int = 1,
        compressed_id_start: int = 1,
        system_prompt: str = "",
        compression_callback: Optional[Callable[[List[Dict]], str]] = None
    ):
        """初始化消息管理器实例。
        
        Args:
            session: 当前会话的唯一标识符
            max_context_tokens: 上下文token上限，默认4096
            compression_ratio: 压缩比例系数(0.1-0.9)，默认0.3
            raw_id_start: 原始消息ID起始值，默认1
            compressed_id_start: 压缩消息ID起始值，默认1
            system_prompt: 初始系统提示词
            compression_callback: 消息压缩处理回调函数
        """

        # 创建ID分配器
        self.raw_id_allocator = MessageIDAllocator(
            session, "raw", raw_id_start
        )
        self.compressed_id_allocator = MessageIDAllocator(
            session, "compressed", compressed_id_start
        )
        self.session = session
        # 系统消息（受保护）
        self.system_pompmts = [{"id":self.raw_id_allocator(),"role":"system","content":system_prompt}] if system_prompt !="" else []
        
        # 对话消息队列（按时间顺序）
        self.message_queue: Deque[Dict] = deque()
        
        # Token管理
        self.current_context_tokens = 0
        self.max_context_tokens = max_context_tokens
        self.compression_ratio = max(0.1, min(compression_ratio, 0.9))
        self.compression_callback = compression_callback
        
        # 线程安全组件
        self.lock = threading.Lock()
        self.compression_queue = Queue()
        self._shutdown = False
        
        # 压缩结果缓存
        self.compression_results: List[CompressionResult] = []
        
        # 启动压缩线程
        self.compression_thread = threading.Thread(
            target=self._compression_worker, 
            daemon=True
        )
        self.compression_thread.start()
        
        # 状态跟踪
        self.last_operation: Optional[Dict] = None

    def set_compression_callback(self, callback):
        """设置压缩回调函数，验证参数类型为 str 或 list[str]"""
        # 1. 检查是否可调用
        if not callable(callback):
            raise TypeError("回调函数必须可调用")
        
        # 2. 获取函数签名
        try:
            sig = inspect.signature(callback)
        except ValueError:
            # 内置函数等无法获取签名的特殊处理
            self.compression_callback = callback
            return
        
        # 3. 验证参数数量
        params = list(sig.parameters.values())
        if len(params) == 0:
            raise TypeError("回调函数需要至少一个参数")
        
        # 4. 获取第一个参数的类型注解
        first_param = params[0]
        param_type = first_param.annotation
        
        # 5. 没有类型注解时直接接受
        if param_type is inspect.Parameter.empty:
            self.compression_callback = callback
            return
        
        # 6. 检查类型兼容性
        def is_compatible(t) -> bool:
            """检查类型是否兼容 str 或 list[str]"""
            # 直接匹配 str
            if t is str:
                return True
            
            # 匹配 List[str] 或 list[str]
            origin = get_origin(t) or t
            if origin in (List, list):
                type_args = get_args(t)
                # 检查是否有类型参数且第一个是 str
                if type_args and type_args[0] is str:
                    return True
            
            # 匹配 Union 类型
            if get_origin(t) is Union:
                return any(is_compatible(union_type) for union_type in get_args(t))
            
            return False
        
        # 7. 验证类型
        if not is_compatible(param_type):
            expected_types = "Union[str, List[str], list[str]]"
            raise TypeError(
                f"回调函数参数类型不兼容。期望: {expected_types}, 实际: {param_type}"
            )
        
        self.compression_callback = callback
        
    def load_context(self,raw:dict,com:dict,pompmts:list[str],messages:list[str]):
        """恢复上下文

        Args:
            raw (_type_): 原始数据分配器配置
            com (_type_): 压缩数据分配器配置
            pompmts (_type_): 系统提示词
            messages (_type_): 上下文消息

        Returns:
            _type_: _description_
        """        
        if self.session is None:
            return ValueError("Message缺失 session")
        
        self.raw_id_allocator.load_data(**raw)
        self.compressed_id_allocator.load_data(**com)
        for pompmt in pompmts:
            self.add_system_pompmt(pompmt,flush=False)
        for message in messages:
            self.add_message(message,flush=False)

    def _compression_worker(self):
        """后台压缩线程工作函数。
        
        循环处理压缩队列中的任务，结果存入压缩缓存。
        """

        while not self._shutdown:
            try:
                # 获取压缩任务（设置超时以便检查关闭标志）
                task = self.compression_queue.get(timeout=0.5)
                # 检查是否收到关闭信号
                if self._shutdown:
                    self.compression_queue.task_done()
                    break
                    
                try:
                    if self.compression_callback is None:
                        continue
                    # 执行同步压缩操作
                    compressed_content = self.compression_callback(task["messages"])
                    
                    # 创建压缩消息结构
                    compressed_msg = {
                        "id":self.compressed_id_allocator(),
                        "role": "user",
                        "content": compressed_content,
                        "is_compressed": True,
                        "source_ids": [msg["id"] for msg in task["messages"]]
                    }

                    # 将结果存储在缓存中
                    with self.lock:
                        self.compression_results.append(CompressionResult(
                            message_ids=task["message_ids"],
                            compressed_msg=compressed_msg,

                            start_index=task["start_index"]
                        ))
                    
                    logger.info(f"压缩任务完成: {len(task['messages'])}条消息 -> 缓存结果")
                    
                except Exception as e:
                    logger.error(f"压缩失败: {e}")
                    # 即使失败也添加结果，但标记为失败
                    with self.lock:
                        self.compression_results.append(CompressionResult(
                            message_ids=task["message_ids"],
                            compressed_msg=None,  # None 表示压缩失败
                            start_index=task["start_index"]
                        ))
                    
                finally:
                    self.compression_queue.task_done()
                    
            except:
                # 队列超时，继续检查关闭标志
                pass
    
    def _apply_compression_results(self):
        """应用所有待处理的压缩结果到消息队列。
        
        删除被压缩的原始消息，插入压缩后的新消息。
        """
        if not self.compression_results:
            return
        
        with self.lock:
            # 处理所有待应用的压缩结果
            for result in self.compression_results:
                # 移除原始消息
                for msg_id in result.message_ids:
                    for i, msg in enumerate(self.message_queue):
                        if msg["id"] == msg_id:
                            del self.message_queue[i]
                            break
                
                # 插入压缩消息到起始位置（如果压缩成功）
                if result.compressed_msg:
                    self.message_queue.insert(result.start_index, result.compressed_msg)
                    logger.info(f"压缩消息插入位置: {result.start_index}")
            
            # 清空结果缓存
            self.compression_results.clear()
    
    def close(self):
        """安全关闭管理器并清理资源。
        
        停止压缩线程并等待退出。
        """
        # 设置关闭标志
        self._shutdown = True
        
        # 等待压缩线程退出
        if self.compression_thread.is_alive():
            self.compression_thread.join(timeout=1.0)
        
        logger.info("管理器已关闭")
    
    def add_message(
        self, 
        role: str, 
        content: str,
        is_compressed: bool = False,
        source_ids: Optional[List[str]] = None,
    ) -> int:
        """添加新消息到对话队列。
        
        Args:
            role: 消息角色（user/system/assistant）
            content: 消息文本内容
            is_compressed: 是否为压缩消息，默认False
            source_ids: 压缩消息的原始消息ID列表
            
        Returns:
            分配的消息ID字符串
        """
        # 不需要空消息
        if content is None or content =="":
            return -1
        # 根据消息类型选择分配器
        if is_compressed:
            allocator = self.compressed_id_allocator
        else:
            allocator = self.raw_id_allocator
        
        # 获取唯一ID
        message_id = allocator()
        
        # 创建消息结构
        message = {
            "id": message_id,
            "role": role,
            "content": content,
            "is_compressed": is_compressed,
            "source_ids": source_ids or []
        }
        
        # 添加到队列
        with self.lock:
            self.message_queue.append(message)

        logger.info(f"添加消息: {message_id} (压缩: {is_compressed})")
        return message_id
    
    def get_context(self) -> List[Dict]:
        """生成当前对话上下文的格式化列表。
        
        Returns:
            包含系统消息和对话消息的字典列表
        """
        # 应用所有待处理的压缩结果
        self._apply_compression_results()
        
        with self.lock:
            context = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.system_pompmts
            ]
            
            for msg in self.message_queue:
                context.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return context
    
    def process_token_excess(self, prompt_tokens: int) -> Optional[List[Dict]]:
        """
        更新token计数并处理超限情况（同步版）
        
        Args:
            prompt_tokens: 提示token数（上下文总token）
            
        Returns:
            被移除或压缩的原始消息列表（如果有处理）
        """
        self.current_context_tokens = prompt_tokens
        logger.info(f"更新Token计数: {prompt_tokens}/{self.max_context_tokens}")
        
        if prompt_tokens > self.max_context_tokens:
            excess_ratio = (prompt_tokens - self.max_context_tokens) / self.max_context_tokens
            return self.handle_token_excess(excess_ratio)
        
        return None
    
    def handle_token_excess(self, excess_ratio: float) -> Optional[List[Dict]]:
        """处理token超限情况（同步版）"""
        with self.lock:
            # 计算需要处理的消息数量
            total_messages = len(self.message_queue)
            messages_to_process = max(1, int(total_messages * self.compression_ratio))
            logger.info(f"Token超限处理: 比例={excess_ratio:.2f}, 处理消息数={messages_to_process}")
            
            # 收集要处理的消息
            messages_to_handle = []
            message_ids_to_handle = []
            messages_content = []
            
            # 获取前N条消息
            for i in range(messages_to_process):
                if i < len(self.message_queue):
                    msg = self.message_queue[i]
                    messages_to_handle.append(msg)
                    message_ids_to_handle.append(msg["id"])
                    messages_content.append(msg)
            
            start_index = 0  # 消息起始位置
            
            # 如果没有压缩回调，直接移除消息
            if not self.compression_callback:
                for _ in range(messages_to_process):
                    if self.message_queue:
                        self.message_queue.popleft()
                
                self.last_operation = {"type": "remove", "count": len(messages_to_handle)}
                return messages_to_handle
        
        # 创建压缩任务
        task = {
            "message_ids": message_ids_to_handle,
            "messages": messages_content,
            "start_index": start_index
        }
        
        # 提交压缩任务
        self.compression_queue.put(task)
        logger.info(f"压缩任务已提交: {len(message_ids_to_handle)}条消息")
        
        self.last_operation = {
            "type": "compress_started", 
            "count": len(messages_to_handle)
        }
        
        return messages_to_handle
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """根据ID从队列中检索消息。
        
        Args:
            message_id: 要检索的消息ID
            
        Returns:
            匹配的消息字典，未找到时返回None
        """
        with self.lock:
            for msg in self.message_queue:
                if msg.get("id") == message_id:
                    return msg
        return None
    
    def clear_context(self, keep_system: bool = True):
        """重置对话上下文状态。
        
        Args:
            keep_system: 是否保留系统消息，默认True
        """

        with self.lock:
            self.message_queue.clear()
            self.current_context_tokens = 0
            self.last_operation = None
            self.compression_results.clear()
            
            self.raw_id_allocator.reset()
            self.compressed_id_allocator.reset()

            if not keep_system:
                self.system_pompmts.clear()
    
    def wait_for_compression(self, timeout: float = 30.0) -> bool:
        """等待当前压缩任务完成（同步版）"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.compression_queue.empty():
                return True
            time.sleep(0.1)
        return False
    
    def get_original_messages(self, compressed_id: str) -> Optional[List[Dict]]:
        """通过压缩消息ID反查原始消息。
        
        Args:
            compressed_id: 压缩消息ID
            
        Returns:
            原始消息字典列表，查询失败时返回None
        """
        compressed_msg = self.get_message(compressed_id)
        if not compressed_msg or not compressed_msg.get("is_compressed"):
            return None
        
        source_ids = compressed_msg.get("source_ids", [])
        return [msg for id in source_ids if (msg := self.get_message(id)) is not None]
    
    def get_queue_size(self) -> int:
        """获取当前对话队列长度。
        
        Returns:
            消息队列中的消息数量
        """
        with self.lock:
            return len(self.message_queue)
    
    def add_system_pompmt(self, content: str) -> int:
        """添加系统消息到受保护区域。
        
        Args:
            content: 系统消息内容
        Returns:
            分配的系统消息ID
        """
        with self.lock:
            message_id = self.raw_id_allocator()
            pormpt = {
                "id": message_id,
                "role": "system",
                "content": content
            }
            self.system_pompmts.append(pormpt)

            return message_id
    
    def remove_message(self, message_id: str) -> Optional[Dict]:
        """从队列中删除指定消息。
        
        Args:
            message_id: 要删除的消息ID
            
        Returns:
            被删除的消息字典，未找到时返回None
        """

        with self.lock:
            for i, msg in enumerate(self.message_queue):
                if msg.get("id") == message_id:
                    del self.message_queue[i]
                    return msg
        return None
    
    def get_allocator_states(self) -> Dict[str, Dict]:
        """获取ID分配器的当前状态。
        
        Returns:
            包含原始ID和压缩ID分配器状态的字典
        """
        with self.lock:
            return {
                "raw": self.raw_id_allocator.get_current_state(),
                "compressed": self.compressed_id_allocator.get_current_state()
            }
        
    def get_full_context(self):
        """获取完整的原始消息队列（包含元数据）。
        
        Returns:
            当前消息队列的完整副本
        """
        return self.message_queue
    
    def get_all_data(self):
        """返回所有数据"""
        return self.system_pompmts,self.message_queue
    
    def __str__(self) -> str:
        """返回对象的字符串表示，展示关键状态信息"""
        # 安全获取队列大小（避免锁冲突）
        try:
            queue_size = self.get_queue_size()
            compression_tasks = self.compression_queue.qsize()
        except:
            queue_size = "未知"
            compression_tasks = "未知"
        
        # 获取分配器状态
        allocator_states = self.get_allocator_states()
        
        # 构建系统消息摘要
        system_summary = f"{len(self.system_pompmts)}条系统提示词"
        if self.system_pompmts and self.system_pompmts[0]['content']:
            first_system = self.system_pompmts[0]['content']
            if len(first_system) > 20:
                first_system = first_system[:17] + "..."
            system_summary += f" (首条: '{first_system}')"
        
        # 构建状态字符串
        return (
            f"Message(会话: {self.session})\n"
            f"├── 系统消息: {system_summary}\n"
            f"├── 消息队列: {queue_size}条消息\n"
            f"├── Token使用: {self.current_context_tokens}/{self.max_context_tokens}\n"
            f"├── 原始消息ID: {allocator_states['raw']['current_id']}\n"
            f"├── 压缩消息ID: {allocator_states['compressed']['current_id']}\n"
            f"├── 压缩任务: {compression_tasks}个待处理\n"
            f"└── 压缩结果: {len(self.compression_results)}个待应用"
        )