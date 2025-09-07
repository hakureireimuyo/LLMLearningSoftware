
class GraphicProxy:
    """图形代理类，统一管理颜色和形状指令"""
    def __init__(self, color, shape):
        self.color = color
        self.shape = shape
        self._pos = getattr(shape, 'pos', (0, 0)) if shape else (0, 0)
        self._size = getattr(shape, 'size', (0, 0)) if shape else (0, 0)
        self._rgba = getattr(color, 'rgba', (1, 1, 1, 1)) if color else (1, 1, 1, 1)
        
        # 保存初始值
        self.initial_pos = self._pos
        self.initial_size = self._size
        self.initial_rgba = self._rgba
        
        # 类型信息
        self.color_type = type(color).__name__ if color else "None"
        self.shape_type = type(shape).__name__ if shape else "None"
    
    def __str__(self):
        """用户友好的字符串表示"""
        return (
            f"GraphicProxy(\n"
            f"  Color: {self.rgba} ({self.color_type})\n"
            f"  Shape: {self.shape_type}\n"
            f"  Position: {self.pos}\n"
            f"  Size: {self.size}\n"
            f"  Initial: [rgba={self.initial_rgba}, pos={self.initial_pos}, size={self.initial_size}]\n"
            f")"
        )
    
    def __repr__(self):
        """开发人员友好的字符串表示"""
        color_id = id(self.color) if self.color else 0
        shape_id = id(self.shape) if self.shape else 0
        return (
            f"<GraphicProxy at {hex(id(self))}>\n"
            f"  Color: {self.rgba} ({self.color_type}@{hex(color_id)})\n"
            f"  Shape: {self.shape_type}@{hex(shape_id)}\n"
            f"  Position: {self.pos}, Size: {self.size}"
        )
    
    def reset(self):
        """重置到初始状态"""
        if self.color and hasattr(self.color, 'rgba'):
            self.color.rgba = self.initial_rgba
            self._rgba = self.initial_rgba
        if self.shape:
            if hasattr(self.shape, 'pos'):
                self.shape.pos = self.initial_pos
                self._pos = self.initial_pos
            if hasattr(self.shape, 'size'):
                self.shape.size = self.initial_size
                self._size = self.initial_size
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value
        if self.shape and hasattr(self.shape, 'pos'):
            self.shape.pos = value
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        if self.shape and hasattr(self.shape, 'size'):
            self.shape.size = value
    
    @property
    def rgba(self):
        return self._rgba
    
    @rgba.setter
    def rgba(self, value):
        self._rgba = value
        if self.color and hasattr(self.color, 'rgba'):
            self.color.rgba = value
    
    def update_layout(self, size, pos):
        """更新布局（子类可重写）"""
        # 默认实现 - 更新位置和尺寸
        if self.shape:
            if hasattr(self.shape, 'pos'):
                self.pos = pos
            if hasattr(self.shape, 'size'):
                self.size = size
    
    def get_debug_info(self):
        """获取调试信息"""
        return {
            "type": "GraphicProxy",
            "id": hex(id(self)),
            "color": {
                "type": self.color_type,
                "rgba": self.rgba,
                "id": hex(id(self.color)) if self.color else None
            },
            "shape": {
                "type": self.shape_type,
                "pos": self.pos,
                "size": self.size,
                "id": hex(id(self.shape)) if self.shape else None
            },
            "initial": {
                "rgba": self.initial_rgba,
                "pos": self.initial_pos,
                "size": self.initial_size
            }
        }
    
    def remove(self):
        """移除图形指令"""
        # 实际移除操作应由画布处理
        # 这里只解除引用
        self.color = None
        self.shape = None
        self._pos = (0, 0)
        self._size = (0, 0)
        self._rgba = (1, 1, 1, 1)