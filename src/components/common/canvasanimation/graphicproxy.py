"""
canvas图形指令的代理对象
将颜色指令,图形指令,旋转指令进行统一管理
实现内部数据户同步
"""

class GraphicProxy:
    """图形代理类，统一管理颜色和形状指令"""
    def __init__(self, color=None, shape=None,rotate=None):
        self.color = color
        self.shape = shape
        self.rotate = rotate

        self._pos = getattr(shape, 'pos', (0, 0)) if shape else (0, 0)
        self._size = getattr(shape, 'size', (0, 0)) if shape else (0, 0)
        self._rgba = getattr(color, 'rgba', (1, 1, 1, 1)) if color else (1, 1, 1, 1)
        self._angle = getattr(rotate, 'angle', 0) if shape else 0
        self._origin = getattr(rotate, 'origin', (0, 0)) if shape else (0, 0)

        # 旋转中心保持在中点?
        self._keep_rotate_origin_in_center = True
        if self._keep_rotate_origin_in_center:
            self.update_rotate_origin_to_center()
        # 保存初始值
        self.initial_pos = self._pos
        self.initial_size = self._size
        self.initial_rgba = self._rgba
        self.initial_angle = self._angle
        self.initial_origin = self._origin
        
        # 类型信息
        self.color_type = type(color).__name__ if color else "None"
        self.shape_type = type(shape).__name__ if shape else "None"
        self.rotate_type = type(rotate).__name__ if rotate else "None"
    
    def __str__(self):
        """用户友好的字符串表示"""
        return (
            f"GraphicProxy(\n"
            f"  Color: {self.rgba} ({self.color_type})\n"
            f"  Shape: {self.shape_type}\n"
            f"  Rotate: {self.rotate_type}\n"
            f"  Position: {self.pos}\n"
            f"  Size: {self.size}\n"
            f"  Angle: {self.angle}\n"
            f"  Origin: {self.origin}\n"
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
        if self.rotate:
            if hasattr(self.rotate, 'origin'):
                self.rotate.origin = self.initial_origin
                self._origin = self.initial_origin
            if hasattr(self.rotate, 'angle'):
                self.rotate.angle = self.initial_angle
                self._angle = self.initial_angle
    
    
    def update_layout(self, size, pos):
        """更新布局（子类可重写）"""
        # 默认实现 - 更新位置和尺寸
        # if self.shape:
        #     if hasattr(self.shape, 'pos'):
        #         self.pos = pos
        #     if hasattr(self.shape, 'size'):
        #         self.size = size
        # 暂时没想好
    def update_rotate_origin_to_center(self):
        """更新旋转原点"""
        if self.rotate and hasattr(self.rotate, 'origin'):
            self.rotate.origin = (self._pos[0]+self.size[0] / 2, self._pos[1]+self.size[1] / 2)
            self._origin = self.rotate.origin
            self.initial_origin = self._origin

        
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value
        self.shape.pos = value
        if self._keep_rotate_origin_in_center:
            self.update_rotate_origin_to_center()
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        #if self.shape and hasattr(self.shape, 'size'):
        self.shape.size = value
        if self._keep_rotate_origin_in_center:
            self.update_rotate_origin_to_center()
    
    @property
    def rgba(self):
        return self._rgba
    
    @rgba.setter
    def rgba(self, value):
        self._rgba = value
        # if self.color and hasattr(self.color, 'rgba'):
        self.color.rgba = value

    @property
    def x(self):
        """X坐标"""
        return self.pos[0]
    
    @x.setter
    def x(self, value):
        """仅更新X坐标"""
        self.pos = (value, self.pos[1])  # 保留原有Y值
    
    @property
    def y(self):
        """Y坐标"""
        return self.pos[1]
    
    @y.setter
    def y(self, value):
        """仅更新Y坐标"""
        self.pos = (self.pos[0], value)  # 保留原有X值
    
    @property
    def w(self):
        """宽度"""
        return self.size[0]
    
    @w.setter
    def w(self, value):
        """仅更新宽度"""
        self.size = (value, self.size[1])  # 保留原有高度
    
    @property
    def h(self):
        """高度"""
        return self.size[1]
    
    @h.setter
    def h(self, value):
        """仅更新高度"""
        self.size = (self.size[0], value)  # 保留原有宽度

    @property
    def angle(self):
        """旋转角度"""
        return self._angle
    
    @angle.setter
    def angle(self, value):
        """设置旋转角度"""
        self._angle = value
        if self.rotate:
            self.rotate.angle = value
    
    @property
    def origin(self):
        """旋转原点"""
        return self._origin
    
    @origin.setter
    def origin(self, value):
        """设置旋转原点"""
        if self._keep_rotate_origin_in_center:
            # 保持旋转中心不变
            return
        self._origin = value
        if self.rotate:
            self.rotate.origin = value

    def remove(self):
        """移除图形指令"""
        # 实际移除操作应由画布处理
        # 这里只解除引用
        self.color = None
        self.shape = None
        self.rotate = None
        self._pos = (0, 0)
        self._size = (0, 0)
        self._rgba = (1, 1, 1, 1)
        self._angle = 0
        self._origin = (0, 0)