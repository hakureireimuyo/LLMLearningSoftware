import time
import ctypes
import logging
from win_ime import WindowsImeHandler  # 假设类保存在这个文件中

# 配置日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ImeTest')

def simulate_ime_input():
    """模拟输入法行为并测试ImeHandler的功能"""
    logger.info("=== Windows 输入法处理器测试开始 ===")
    
    # 创建输入法处理器实例
    ime_handler = WindowsImeHandler()
    
    # 测试1: 激活输入法上下文
    logger.info("\n测试1: 激活输入法上下文...")
    if ime_handler.activate():
        logger.info("激活成功! 当前IMC句柄: %s", ime_handler.h_imc)
    else:
        logger.error("激活失败! 请确保:")
        logger.error("1. 系统中有可用的输入法")
        logger.error("2. 测试时焦点在文本输入窗口")
        logger.error("3. 输入法已开启(非英文模式)")
        return
    
    # 测试2: 获取候选词列表
    logger.info("\n测试2: 获取候选词列表...")
    logger.info("请在文本输入窗口输入中文(如拼音)，然后按回车继续")
    input("> 准备就绪后按Enter继续...")
    
    try:
        # 获取实时候选词数据
        candidates, selection, page_start, page_size = ime_handler._get_candidate_list_real_time()
        
        if candidates:
            logger.info("获取到 %d 个候选词:", len(candidates))
            for i, cand in enumerate(candidates):
                prefix = "==>" if i == selection else f"{i+1}."
                logger.info(f"{prefix} {cand}")
            logger.info("当前选择: %d, 页面起始: %d, 页面大小: %d", 
                        selection, page_start, page_size)
        else:
            logger.warning("未获取到候选词! 可能原因:")
            logger.warning("- 未在输入状态")
            logger.warning("- 输入法未开启中文模式")
            logger.warning("- 系统不支持候选词查询")
    except Exception as e:
        logger.error("获取候选词时出错: %s", e)
    
    # 测试3: 获取候选词切片
    logger.info("\n测试3: 获取候选词切片...")
    if candidates:
        logger.info("完整候选词列表: %s", candidates)
        
        # 测试各种切片情况
        test_cases = [
            (0, 3),    # 前3个
            (2, 2),    # 中间2个
            (5, 10),   # 超出范围
            (-1, 3),   # 负索引
        ]
        
        for start, count in test_cases:
            slice_result = ime_handler.get_candidates_slice(start, count)
            logger.info("切片(start=%d, count=%d): %s", start, count, slice_result)
    
    # 测试4: 释放上下文
    logger.info("\n测试4: 释放输入法上下文...")
    ime_handler.deactivate()
    logger.info("释放完成! 当前状态: %s", "活跃" if ime_handler.is_active() else "未激活")
    
    # 测试5: 重新激活测试
    logger.info("\n测试5: 重新激活测试...")
    logger.info("请切换窗口焦点后再切回测试窗口，按回车继续")
    input("> 准备就绪后按Enter继续...")
    
    if ime_handler.activate():
        logger.info("重新激活成功!")
    else:
        logger.warning("重新激活失败!")
    
    logger.info("\n=== 测试完成 ===")

def main():
    # 显示测试说明
    print("="*60)
    print("Windows 输入法处理器测试说明")
    print("="*60)
    print("1. 请确保系统中有中文输入法(如微软拼音)")
    print("2. 测试期间请保持焦点在文本输入窗口(如记事本)")
    print("3. 当提示输入时，请在文本窗口输入中文拼音")
    print("4. 观察程序输出的候选词信息")
    print("="*60)
    print("6s后开始测试...")
    time.sleep(6)
    # 执行测试
    simulate_ime_input()

if __name__ == "__main__":
    main()