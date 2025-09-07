import sys
import os

# 添加项目根目录到模块查找路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.branchdialogue import SessionTree,SessionNode,GlobalSessionIDAllocator

gsda = GlobalSessionIDAllocator()
gsda.set_start(1)

tree = SessionTree(gsda)

for index in range(2,6):
    for num in range(0,3):
        tree.create_child_branch(f"{index}_{num}")
    tree.switch_to_node(index)
    
print(tree.to_tree_string())