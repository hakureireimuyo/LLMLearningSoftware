import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import DB,DAO
from src.core.evn import database
from src.core.database import UserOperator

# ------ 使用示例 ------ 
def test_db_operations():
    print(database)
    db = DB(database_path=database)
    dao:DAO[UserOperator] = db.get_dao('user')
    
    with dao.transaction():
        user = dao.user
        # 1. 用户表
        user_id =user.insert({
            'username': 'test_user',
            'avatar_path': '/path/avatar.png'
        })
        print(user_id)
    db.close()


if __name__ == "__main__":
    test_db_operations()