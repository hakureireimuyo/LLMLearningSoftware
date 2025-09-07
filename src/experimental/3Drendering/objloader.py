class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        # 更通用的顶点格式
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.vertices = []  # 浮点数数组
        self.indices = []   # 整数索引数组

    def calculate_normals(self):
        """为没有法线的模型计算面法线"""
        # 重置所有法线为零
        for i in range(3, len(self.vertices), 8):
            self.vertices[i:i+3] = [0.0, 0.0, 0.0]
        
        # 计算每个面的法线并累加到顶点
        for i in range(len(self.indices) // 3):
            fi = i * 3
            i0 = self.indices[fi] * 8
            i1 = self.indices[fi+1] * 8
            i2 = self.indices[fi+2] * 8
            
            # 获取顶点位置
            v0 = self.vertices[i0:i0+3]
            v1 = self.vertices[i1:i1+3]
            v2 = self.vertices[i2:i2+3]
            
            # 计算面法线
            u = [v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]]
            v = [v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]]
            
            nx = u[1]*v[2] - u[2]*v[1]
            ny = u[2]*v[0] - u[0]*v[2]
            nz = u[0]*v[1] - u[1]*v[0]
            
            # 累加到顶点法线
            for idx in [i0, i1, i2]:
                self.vertices[idx+3] += nx
                self.vertices[idx+4] += ny
                self.vertices[idx+5] += nz
        
        # 标准化顶点法线
        for i in range(0, len(self.vertices), 8):
            nx, ny, nz = self.vertices[i+3], self.vertices[i+4], self.vertices[i+5]
            length = (nx*nx + ny*ny + nz*nz)**0.5
            if length > 0:
                self.vertices[i+3:i+6] = [nx/length, ny/length, nz/length]


class ObjFile:
    def __init__(self, filename, swapyz=False):
        self.objects = {}
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self._current_object = None
        
        # 添加原点顶点 (0,0,0) 作为占位符
        self.vertices.append((0.0, 0.0, 0.0))
        self.normals.append((0.0, 0.0, 1.0))
        self.texcoords.append((0.0, 0.0))
        
        for line in open(filename, "r", encoding='utf-8'):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue
            
            if values[0] == 'o':
                self.finish_object()
                self._current_object = values[1]
            
            elif values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = [v[0], v[2], v[1]]
                self.vertices.append(v)
            
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = [v[0], v[2], v[1]]
                self.normals.append(v)
            
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                
                for v in values[1:]:
                    w = v.split('/')
                    # 处理顶点索引
                    vi = int(w[0]) if w[0] else 0
                    # 处理法线索引
                    vni = int(w[2]) if len(w) >= 3 and w[2] else 0
                    # 处理纹理坐标索引
                    vti = int(w[1]) if len(w) >= 2 and w[1] else 0
                    
                    face.append(vi)
                    norms.append(vni)
                    texcoords.append(vti)
                
                # 支持三角形或四边形面
                if len(face) == 3:
                    self.faces.append((face, norms, texcoords))
                elif len(face) == 4:
                    # 四边形拆分成两个三角形
                    self.faces.append(([face[0], face[1], face[2]], 
                                       [norms[0], norms[1], norms[2]],
                                       [texcoords[0], texcoords[1], texcoords[2]]))
                    self.faces.append(([face[0], face[2], face[3]], 
                                       [norms[0], norms[2], norms[3]],
                                       [texcoords[0], texcoords[2], texcoords[3]]))
        
        self.finish_object()

    def finish_object(self):
        if not self._current_object or not self.faces:
            if self.faces:
                self._current_object = "default"
            else:
                return
        
        mesh = MeshData(name=self._current_object)
        vertex_map = {}
        vertex_count = 0
        
        # 处理每个面
        for face in self.faces:
            indices = []
            verts, norms, tcs = face
            
            # 处理面中的每个顶点
            for i in range(len(verts)):
                # 获取顶点属性
                vi = max(0, min(verts[i], len(self.vertices)-1))
                v = self.vertices[vi]
                
                n = (0.0, 0.0, 1.0)
                if norms[i] > 0 and norms[i] < len(self.normals):
                    n = self.normals[norms[i]]
                
                tc = (0.0, 0.0)
                if tcs[i] > 0 and tcs[i] < len(self.texcoords):
                    tc = self.texcoords[tcs[i]]
                
                # 创建顶点key用于判断是否已存在
                vertex_key = (vi, norms[i], tcs[i])
                
                # 检查是否已存在相同顶点
                if vertex_key in vertex_map:
                    indices.append(vertex_map[vertex_key])
                else:
                    # 添加新顶点
                    mesh.vertices.extend(v)
                    mesh.vertices.extend(n)
                    mesh.vertices.extend(tc)
                    vertex_map[vertex_key] = vertex_count
                    indices.append(vertex_count)
                    vertex_count += 1
            
            # 添加到索引
            mesh.indices.extend(indices)
        
        # 如果法线不完整，计算法线
        if not self.normals or len(self.normals) <= 1:
            mesh.calculate_normals()
        
        self.objects[self._current_object] = mesh
        self.faces = []
        self._current_object = None