from global_instance import wd,sd
from global_tools import count_words

#自动统计单词数据
def auto_statistics(text,type):
    t_text=count_words(text)
    result=sd.query_multiple_words(t_text)
    wd.bulk_update_stats(result,type)