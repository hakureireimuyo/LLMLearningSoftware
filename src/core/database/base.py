"""
作为数据库表操作类的父类,提供基础的操作方法 
"""
import sqlite3
from typing import Optional,Union,List
import re
from typing import Protocol, runtime_checkable

class BaseTableOperator():

    def __init__(self, conn: sqlite3.Connection, table_name: str):
        """初始化数据库操作对象，绑定连接与目标表。

        此构造方法创建数据库操作实例，建立与SQLite数据库的持久化关联，
        并指定后续CRUD操作的目标数据表。需确保传入的连接已正确打开，
        且表名在数据库中真实存在（或后续通过`create_table`创建）[7,8](@ref)。

        Args:
        conn (sqlite3.Connection): 已激活的SQLite数据库连接对象。
            此连接应通过`sqlite3.connect()`创建，并保持有效状态直至实例销毁[7](@ref)。
        table_name (str): 目标数据表名称。需符合SQLite命名规范：
            - 仅包含字母、数字、下划线
            - 不以数字开头
            - 避免SQL关键字（如`select`, `delete`等）

        Attributes:
        conn (sqlite3.Connection): 存储数据库连接对象，用于执行所有SQL操作。
        table_name (str): 存储目标表名，用于动态构建SQL语句。

        Raises:
        TypeError: 当`conn`非Connection对象或`table_name`非字符串时抛出。
        ValueError: 当`table_name`包含非法字符或为空字符串时抛出。

        Example:
        >>> import sqlite3
        >>> db_conn = sqlite3.connect("example.db")
        >>> user_db = Database(db_conn, "users")  # 操作users表
        >>> order_db = Database(db_conn, "orders") # 操作orders表

        Note:
        1. 多个实例可共享同一连接对象[8](@ref)
        2. 表名大小写敏感（推荐统一小写）
        3. 连接生命周期应由调用方管理关闭[7](@ref)
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("conn必须是sqlite3.Connection实例")
        if not isinstance(table_name, str) or not self._validate_table_name(table_name):
            raise ValueError(f"非法表名: {table_name}")

        self._conn:sqlite3.Connection = conn
        self._table_name:str = table_name

        if not self._tables_exist():
            self._create_table()
    
    def _create_table(self):
        """初始化数据库表结构，执行原子性建表操作
        
        执行流程：
        1. 启用事务保证原子操作：要么全表创建成功，要么完全回滚
        2. 强制开启外键约束：确保数据关联完整性
        3. 调用子类实现的表定义方法创建物理表
        
        安全机制：
        - 事务保护：with语句自动管理提交/回滚
        - 外键约束：PRAGMA指令强制关联完整性
        - 注入防护：表定义由抽象方法提供（非外部输入）
        
        Example:
            当表结构为：
                CREATE TABLE users(...)
                CREATE TABLE orders(...)
            执行过程：
                1. BEGIN TRANSACTION
                2. PRAGMA foreign_keys=ON
                3. CREATE TABLE users(...)
                4. CREATE TABLE orders(...)
                5. COMMIT

        Note:
            1. 依赖子类正确实现get_table_definition()
            2. 方法隐含事务边界：with conn: 开启隐式事务
            3. 建表操作具有幂等性（依赖IF NOT EXISTS）
        """
        with self._conn:  # 开启事务上下文管理器（成功执行后自动提交）
            cursor = self._conn.cursor()
            
            # 关键安全设置：强制启用外键约束（SQLite默认关闭）
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # 核心操作：执行子类提供的表定义SQL
            # 重要：抽象方法调用驱动实际建表操作
            cursor.execute(self.get_table_definition())  

    def _tables_exist(self) -> bool:
        """验证数据库所需表是否已存在（幂等性检查）。
        
        通过查询 SQLite 系统表 `sqlite_master` 检测目标表是否存在：
        1. **原子性检查**：单次事务内验证所有表存在性
        2. **注入防护**：参数化查询避免 SQL 注入风险
        3. **类型安全**：强制表名类型约束

        Returns:
            bool: 表存在时返回 True，表缺失返回 False
            
        Raises:
            sqlite3.OperationalError: 数据库连接失效或查询语法错误
            TypeError: 表名列表包含非字符串元素

        Example:
            >>> db = Database("app.db")
            >>> db._tables_exist()
            True  # 当 self_table_name表存在时

        Design:
            1. 获取需检测的表名列表（子类实现 `required_table_names`）
            2. 使用参数化查询验证每个表是否存在
            3. 采用短路逻辑优化性能（发现缺失表立即返回）
        """
        # 原子操作：单连接内完成所有检测
        with self._conn:
            cursor = self._conn.cursor()
            # 参数化查询防止注入 [1,5](@ref)
            cursor.execute(
                "SELECT count(name) FROM sqlite_master "
                "WHERE type='table' AND name=?",
                (self._table_name,)
            )
            result = cursor.fetchone()
            return result[0] > 0 if result else False

    def _validate_table_name(self, name: str) -> bool:
        """验证表名格式合法性，防止SQL注入攻击。
        
        使用正则表达式对表名进行白名单校验，确保表名：
        1. 仅包含小写字母、数字和下划线
        2. 以字母或下划线开头
        3. 长度在1-64字符之间（兼容SQLite标识符长度限制）
        
        Args:
            name (str): 待验证的表名字符串
        
        Returns:
            bool: 验证结果
                True  - 符合安全规范
                False - 含非法字符或格式错误
        
        Raises:
            TypeError: 当输入参数非字符串类型时抛出
            
        Example:
            >>> self._validate_table_name("valid_table_123") 
            True
            >>> self._validate_table_name("1invalid_table")  # 数字开头
            False
            >>> self._validate_table_name("table;DROP TABLE users")  # 含SQL注入字符
            False
        
        Note:
            1. 此校验是防止表名注入的核心防线[1](@ref)
            2. 正则设计基于SQLite标识符规范：
            - 首字符必须为字母或下划线[4](@ref)
            - 后续字符可包含数字[7](@ref)
            3. 长度限制避免超长标识符导致的解析错误[8](@ref)
        """
        return re.match(r"^[a-z_][a-z0-9_]{0,63}$", name) is not None
    
    @property
    def is_connection_active(self):
        try:
            self._conn.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False
    
    def get_table_definition(self) -> str:
        """提供数据表的定义语句，子类必须实现此方法以支持数据库操作。
        
        此方法用于动态生成数据表的 SQL 定义语句（如 CREATE TABLE），
        确保子类能够根据实际业务需求定制表结构。抽象方法的设计强制子类必须实现，
        否则在实例化或调用时将引发 `TypeError` 异常。

        Returns:
            str: 完整的 SQL 表定义语句（例如：`"CREATE TABLE users (id INT, name VARCHAR(255))"`）。
        
        Raises:
            NotImplementedError: 子类未实现此方法时，在抽象类中调用会触发该异常。
            TypeError: 子类未实现此方法时尝试实例化对象会触发此异常。

        Example:
            class UserTable(AbstractDatabase):
                def get_table_definition(self) -> str:
                    return '''
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE
                    )
                    '''
        """
        raise NotImplementedError("子类必须实现数据表的定义")

    def insert(self, data: dict) -> int:
        """通用数据库插入方法，使用参数化查询防止SQL注入
        
        自动处理自增主键字段（移除传入的id键），动态构建INSERT语句，
        执行后返回数据库生成的主键rowid。若操作失败则返回-1。

        Args:
            data (dict): 待插入的字段名与值组成的字典。
                示例：{"name": "Alice", "email": "alice@example.com", "age": 30}
                注意：若字典包含'id'键会被自动移除（避免干扰自增主键）

        Returns:
            int: 新插入行的主键值（rowid），插入失败时返回-1

        Raises:
            sqlite3.OperationalError: SQL语法错误或表不存在
            sqlite3.IntegrityError: 违反唯一约束等完整性错误

        Example:
            >>> db = Database("users")
            >>> rowid = db.insert({"name": "Bob", "age": 25})
            # 生成SQL: INSERT INTO users (name, age) VALUES (?, ?)
            # 参数: ('Bob', 25)
            # 返回: 42 (新插入行的rowid)
        """
        # 移除可能存在的'id'键（确保主键由数据库自增生成）
        if 'id' in data:
            del data['id']  # 避免手动指定主键导致冲突
        
        # 动态构建插入语句的列名和占位符
        columns = ', '.join(data.keys())  # 例: "name, email, age"
        placeholders = ', '.join(['?'] * len(data))  # 例: "?, ?, ?"
        
        # 组合完整SQL语句（关键：分离用户输入与SQL结构）
        sql = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
        
        # 执行参数化查询（元组化字典值作为参数）
        cursor = self._execute(sql, tuple(data.values()))
        
        # 获取最后插入行的ID（数据库自增主键）
        id = cursor.lastrowid
        
        # 返回rowid（失败时返回-1）
        return id if id is not None else -1

    def update(self, where_clause: str, where_params: tuple, update_data: dict) -> int:
        """通用数据库更新方法，使用参数化查询防止SQL注入
        
        通过动态生成SET子句和条件语句，将用户输入数据与SQL语句分离。
        返回数据库操作影响的行数。

        Args:
            where_clause (str): WHERE条件语句（不含WHERE关键字），
                可包含占位符（如：`id=?`）。示例："status=? AND created_at < ?"
            where_params (tuple): WHERE条件对应的参数值元组，
                顺序需与`where_clause`中的占位符匹配。示例：(1, '2023-01-01')
            update_data (dict): 待更新的字段名与值组成的字典。
                示例：{"status": 2, "updated_at": "2023-08-14 10:00:00"}

        Returns:
            int: 数据库操作影响的行数（例如更新的记录数）

        Example:
            >>> db.update(
            ...     where_clause="id=?",
            ...     where_params=(1001,),
            ...     update_data={"status": 3}
            ... )
            # 生成SQL: UPDATE table_name SET status=? WHERE id=?
            # 参数: (3, 1001)
        """
        # 动态生成SET子句（例如：field1=?, field2=?）
        set_clause = ', '.join([f"{k}=?" for k in update_data.keys()])
        
        # 组合完整SQL语句（关键：分离用户输入与SQL结构）
        sql = f"UPDATE {self._table_name} SET {set_clause} WHERE {where_clause}"
        
        # 合并参数：先更新字段值，后条件参数（确保顺序匹配占位符）
        params = tuple(update_data.values()) + where_params
        
        # 执行参数化查询并返回影响行数
        return self._execute(sql, params).rowcount


    def delete(self, where_clause: str, where_params: tuple) -> int:
        """执行安全的参数化删除操作，返回受影响行数。
        
        根据指定的条件删除表中的记录，使用参数化查询避免SQL注入。
        注意：WHERE 条件需显式提供占位符（如 `id=?`）并与参数顺序严格匹配。

        Args:
            where_clause (str): WHERE 条件语句（不含 WHERE 关键字），
                需包含占位符（如 `status=? AND created_at < ?`）。
            where_params (tuple): WHERE 条件对应的参数值元组，
                顺序需与 `where_clause` 占位符一致（如 (1, '2023-01-01')）。

        Returns:
            int: 删除操作影响的行数（0 表示无匹配记录）。

        Raises:
            sqlite3.OperationalError: 表不存在或SQL语法错误
            sqlite3.IntegrityError: 违反外键约束等完整性错误

        Example:
            >>> db.delete("status=? AND expire_date < ?", (0, '2025-01-01'))
            # SQL: DELETE FROM table_name WHERE status=? AND expire_date<?
            # 参数: (0, '2025-01-01')
            # 返回: 5 (删除5条记录)
        """
        sql = f"DELETE FROM {self._table_name} WHERE {where_clause}"
        return self._execute(sql, where_params).rowcount

    def select(
        self,
        columns: str = "*",
        where_clause: Optional[str] = None,
        where_params: tuple = (),
        order_by: Optional[str] = None
    ) -> list:
        """执行安全的参数化查询，返回结果字典列表。
        
        支持动态列选择、条件过滤和排序，所有用户输入均通过参数化传递。

        Args:
            columns (str): 查询的列名（逗号分隔，默认所有列）。示例："id, name, age"。
            where_clause (str | None): WHERE 条件语句（不含 WHERE 关键字），
                需包含占位符（如 `category=?`）。若为 None 则无条件查询。
            where_params (tuple): WHERE 条件参数值（如 ('books',)）。
            order_by (str | None): ORDER BY 子句（不含关键字），
                示例："created_at DESC, id ASC"。

        Returns:
            list[dict]: 查询结果列表，每行转为字典（键为列名，值为数据）。

        Raises:
            sqlite3.OperationalError: 表/列不存在或SQL语法错误

        Example:
            >>> db.select(
            ...     columns="name, email",
            ...     where_clause="age>? AND status=?",
            ...     where_params=(18, 1),
            ...     order_by="register_date DESC"
            ... )
            # SQL: SELECT name, email FROM table_name 
            #      WHERE age>? AND status=? ORDER BY register_date DESC
            # 参数: (18, 1)
            # 返回: [{'name':'Alice','email':'alice@test.com'}, ...]
        """
        # 基础SELECT语句
        sql = f"SELECT {columns} FROM {self._table_name}"
        
        # 动态添加WHERE条件
        if where_clause:
            sql += f" WHERE {where_clause}"
        
        # 动态添加排序
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        # 执行参数化查询并转换结果为字典列表
        cursor = self._execute(sql, where_params)
        return [dict(row) for row in cursor.fetchall()]
    
    def batch_insert(self, data_list: list[dict], batch_size: int = 500) -> int:
        """批量插入数据方法，通过事务管理和分批处理优化性能
        
        自动过滤字典中的'id'键（避免干扰自增主键），动态构建参数化SQL语句。
        采用分批提交策略避免内存溢出，确保大规模数据插入的稳定性。

        Args:
            data_list (list[dict]): 待插入的字典列表，每个字典代表一行数据。
                示例: [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            batch_size (int): 每批次插入的行数（默认500），根据数据库性能调整[5,6](@ref)

        Returns:
            int: 实际插入的总行数

        Raises:
            sqlite3.OperationalError: 表不存在或SQL语法错误
            sqlite3.IntegrityError: 违反唯一约束等数据完整性错误

        Example:
            >>> db.batch_insert([
            ...     {"name": "Leo", "status": 1},
            ...     {"name": "Mia", "status": 2}
            ... ])
            # 生成SQL: INSERT INTO table_name (name, status) VALUES (?, ?)
            # 参数批次: [('Leo', 1), ('Mia', 2)]
            # 返回: 2
        """
        if not data_list:
            return 0

        # 1. 预处理数据：移除所有字典中的'id'键并提取列名
        clean_data = []
        columns = set()
        for row in data_list:
            row_copy = row.copy()
            row_copy.pop('id', None)  # 移除可能存在的id键[6](@ref)
            clean_data.append(row_copy)
            columns.update(row_copy.keys())
        
        # 2. 动态构建SQL（参数化防注入）
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?'] * len(columns))
        sql = f"INSERT INTO {self._table_name} ({columns_str}) VALUES ({placeholders})"
        
        # 3. 分批处理数据
        total_rows = 0
        try:
            # 使用上下文管理器自动处理事务
            with self._conn:
                for i in range(0, len(clean_data), batch_size):
                    batch = clean_data[i:i + batch_size]
                    # 将字典列表转换为参数元组列表（保持列顺序一致）
                    params = [tuple(row[col] for col in columns) for row in batch]
                    
                    # 执行批量插入
                    cursor = self._execute(sql, params, many=True)
                    total_rows += cursor.rowcount
        except Exception as e:
            raise sqlite3.DatabaseError(f"批量插入失败: {e}")
        
        return total_rows

    def _execute(self, sql: str, params: Union[tuple, List[tuple]],many: bool = False) -> sqlite3.Cursor:
        """内部方法：执行参数化SQL语句并返回游标对象。
        
        此方法封装数据库连接执行逻辑，确保所有SQL操作均通过参数化传递，
        从根本上防止SQL注入漏洞。

        Args:
            sql (str): 含占位符的SQL语句（如 `SELECT * FROM table WHERE id=?`）。
            params (tuple): 与SQL占位符对应的参数值（如 (1001,)）。

        Returns:
            sqlite3.Cursor: 数据库游标对象，可用于获取结果或元数据。

        Raises:
            sqlite3.DatabaseError: 数据库底层操作失败
        """
        if many:
            return self._conn.executemany(sql, params)  # 使用 executemany
        else:
            return self._conn.execute(sql, params)  # 单次执行