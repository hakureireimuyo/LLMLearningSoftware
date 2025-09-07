from src.components.common.callback import CallbackManager
# 创建回调管理器实例
callback_manager = CallbackManager()
def test():
    # 定义回调函数
    def on_response(data):
        print("Received response:", data)

    callback_manager.register("on_response", on_response)
    callback_manager.trigger("on_response", "Hello, World!")
    # 取消注册回调函数
    callback_manager.unregister("on_response", on_response)

    #异常测试
    def on_error(error):
        print("Error occurred:", error)

    callback_manager.register("on_error", on_error)
    callback_manager.trigger("on_error", Exception("Something went wrong"))

    #未注册回调调用测试
    callback_manager.trigger("on_response", "Hello, World!")
    callback_manager.trigger("on_error", Exception("Something went wrong"))

    #异常输入测试
    callback_manager.trigger("on_response", 123)

