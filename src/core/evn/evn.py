import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('资源路径')

# 全局缓存
_RESOURCE_ROOT = None

def _find_resource_root(start_path: Path) -> Path:
    """
    向上递归查找包含resource目录的项目根目录
    :param start_path: 起始搜索路径
    :return: 资源根目录 Path 对象
    """
    current_path = start_path.resolve()
    max_depth = 10  # 防止无限递归
    
    for _ in range(max_depth):
        # 检查当前路径是否包含resource目录
        resource_dir = current_path / "resource"
        if resource_dir.exists() and resource_dir.is_dir():
            logger.debug(f"找到资源根目录: {current_path}")
            return current_path
        
        # 到达文件系统根目录时终止
        if current_path == current_path.parent:
            break
        
        current_path = current_path.parent
    
    # 未找到时回退到起始路径的父目录
    logger.warning("未找到资源根目录，使用回退路径")
    return start_path.parent

def get_resource_root() -> Path:
    """
    获取资源根目录（自动适配开发与打包环境）
    """
    global _RESOURCE_ROOT
    if _RESOURCE_ROOT:
        return _RESOURCE_ROOT

    # 在打包环境中使用可执行文件所在目录
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent.resolve()
        logger.info(f"生产环境资源根目录: {base_path}")
    else:
        # 开发环境：从当前文件向上查找resource目录
        current_file_path = Path(__file__).resolve()
        base_path = _find_resource_root(current_file_path)
        logger.info(f"开发环境资源根目录: {base_path}")
    
    _RESOURCE_ROOT = base_path
    return base_path

def external_resource_path(relative_path: str) -> str:
    """
    获取外部资源绝对路径（用户可访问的资源）
    :param relative_path: 相对于resource/external目录的路径
    :return: 完整资源路径字符串
    """
    # 获取资源根目录
    base_dir = get_resource_root()
    
    # 构建完整路径：resource/external + 相对路径
    full_path = base_dir / "resource" / "external" / relative_path
    normalized_path = full_path.resolve()
    
    # 确保目录存在（仅在生产环境）
    if getattr(sys, 'frozen', False) and not normalized_path.parent.exists():
        normalized_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建外部资源目录: {normalized_path.parent}")
    
    return str(normalized_path)

def internal_resource_path(relative_path: str) -> str:
    """
    获取内部资源绝对路径（打包在内部的资源，仅运行时可见）
    :param relative_path: 相对于resource/internal目录的路径
    :return: 完整资源路径字符串
    """
    # 打包环境优先使用 sys._MEIPASS
    _meipass = getattr(sys, '_MEIPASS', None)
    if _meipass:
        base_dir = Path(_meipass) / "resource" / "internal"
    else:
        # 开发环境中，使用项目中的resource/internal目录
        base_dir = get_resource_root() / "resource" / "internal"
    
    full_path = base_dir / relative_path
    normalized_path = full_path.resolve()
    
    # 验证路径是否存在（在生产环境中总是存在）
    if not normalized_path.exists():
        logger.warning(f"内部资源路径不存在: {normalized_path}")
    
    return str(normalized_path)

def prepare_internal_resource(src_path: str, target_rel_path: str):
    """
    准备内部资源（在开发环境中复制文件到内部资源目录）
    :param src_path: 原始文件路径（绝对路径）
    :param target_rel_path: 目标文件在内部资源中的相对路径
    """
    # 仅在开发环境中需要准备
    if getattr(sys, 'frozen', False):
        return
    
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"源文件不存在: {src_path}")
    
    # 获取目标路径
    target = Path(internal_resource_path(target_rel_path))
    
    # 确保目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果源文件在开发环境内部资源目录，不需要复制
    if target.exists() and target.samefile(src):
        return
    
    # 复制文件（仅在需要时）
    logger.info(f"复制内部资源: {src} -> {target}")
    if src.is_dir():
        # 复制目录
        import shutil
        shutil.copytree(src, target, dirs_exist_ok=True)
    else:
        # 复制文件
        import shutil
        shutil.copy2(src, target)
    
    return target

"""
这里用于对定义了程序基本可更改的属性进行获取和管理的代码
该模块将会从固定位置固定的yaml文件(没有就生成)获取配置信息
当前的配置信息主要
系统其他配置不可更改
"""

database:str = internal_resource_path("data/app.db")
stardict:str = internal_resource_path("data/stardict.db")
words:str = internal_resource_path("data/words.db")