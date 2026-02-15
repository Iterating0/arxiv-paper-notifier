"""
数据库管理工具
"""
import sqlite3
from datetime import datetime
from typing import List, Any
from config import Config


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        """初始化数据库"""
        self.db_file = Config.DB_FILE
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # 创建已发送论文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_papers (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                topic TEXT,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def get_all_sent_papers(self) -> List[tuple[Any, ...]]:
        """获取所有已发送的论文"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT arxiv_id, title, topic, sent_time
            FROM sent_papers
            ORDER BY sent_time DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return results

    def get_sent_count(self) -> int:
        """获取已发送论文总数"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sent_papers')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def clear_old_records(self, days: int = 30):
        """清除旧记录"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM sent_papers
            WHERE sent_time < datetime('now', '-{} days')
        '''.format(days))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        print(f"已清除 {deleted} 条旧记录")

    def reset_database(self):
        """重置数据库（清空所有记录）"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS sent_papers')
        conn.commit()
        conn.close()
        print("数据库已重置")
        self._init_database()


if __name__ == '__main__':
    db = DatabaseManager()

    print("=== 数据库统计 ===")
    print(f"已发送论文总数: {db.get_sent_count()}")

    print("\n=== 最近发送的论文 ===")
    papers = db.get_all_sent_papers()[:10]
    for paper in papers:
        print(f"{paper[0]} - {paper[1][:50]}...")

    print("\n提示: 可以使用以下命令管理数据库")
    print("  - 清除30天前的记录: db_manager.clear_old_records(30)")
    print("  - 重置数据库: db_manager.reset_database()")
