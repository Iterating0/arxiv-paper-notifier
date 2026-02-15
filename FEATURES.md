# 新增功能说明

## 1. 爬取频率限制
- 将请求间隔从3秒调整为0.25秒，实现4篇/秒的爬取速度
- 严格遵守arXiv API的使用规范

## 2. 运行状态记录
- 使用SQLite数据库记录已发送的论文
- 自动创建`papers.db`数据库文件
- 记录内容包括：arXiv ID、论文标题、主题、发送时间

## 3. 去重机制
- 基于arXiv ID自动去重
- 启动时加载历史记录到内存
- 只发送新论文，避免重复通知

## 4. 数据库管理工具
提供`db_manager.py`工具用于管理数据库：
- 查看所有已发送论文
- 统计已发送论文数量
- 清除旧记录（可指定天数）
- 重置数据库

## 使用示例

### 查看数据库统计
```python
from db_manager import DatabaseManager
db = DatabaseManager()
print(f"已发送: {db.get_sent_count()} 篇论文")
```

### 清除旧记录
```python
from db_manager import DatabaseManager
db = DatabaseManager()
db.clear_old_records(days=30)  # 清除30天前的记录
```

### 重置数据库
```python
from db_manager import DatabaseManager
db = DatabaseManager()
db.reset_database()  # 清空所有记录
```
