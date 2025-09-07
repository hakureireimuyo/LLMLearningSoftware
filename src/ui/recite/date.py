import sqlite3

def convert_mysql_to_sqlite(sql_file_path, db_file_path):
    """
    将 MySQL SQL 文件转换为 SQLite 数据库
    :param sql_file_path: MySQL SQL 文件路径
    :param db_file_path: 输出的 SQLite 数据库路径
    """
    # 读取 SQL 文件内容
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 创建 SQLite 数据库连接
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        # 执行转换后的 SQL
        cursor.executescript(sql_content)
        conn.commit()
        print(f"成功创建 SQLite 数据库: {db_file_path}")
    except Exception as e:
        print(f"转换失败: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
if __name__ == "__main__":
    convert_mysql_to_sqlite('src\\core\\kivymd_component\\word_recitation\\database\\cet6lx.sql', 'src\\core\\kivymd_component\\word_recitation\\database\\words.db')