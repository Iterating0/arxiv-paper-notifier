"""
配置管理模块
"""
import os
from dotenv import load_dotenv

_ = load_dotenv()


class Config:
    """配置类"""

    # 邮箱配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', '')

    # 爬虫配置
    DEFAULT_TOPIC = os.getenv('DEFAULT_TOPIC', 'machine learning')
    MAX_PAPERS_PER_DAY = int(os.getenv('MAX_PAPERS_PER_DAY', '10'))  # 每日最多发送的新论文数
    CRAWL_RESULTS = int(os.getenv('CRAWL_RESULTS', '50'))  # 每次爬取的论文总数（用于筛选新论文）
    CRAWL_INTERVAL_DAYS = int(os.getenv('CRAWL_INTERVAL_DAYS', '1'))  # 查询最近几天的论文
    MAX_CRAWL_ROUNDS = int(os.getenv('MAX_CRAWL_ROUNDS', '15'))  # 最大爬取轮数

    # arXiv API配置
    ARXIV_API_URL = 'http://export.arxiv.org/api/query'
    REQUEST_DELAY = 3  # 请求间隔（秒），遵守arXiv API限制
    MAX_RESULTS = 20  # 每次请求最多返回结果数

 # 数据库配置
    DB_FILE = 'papers.db'  # SQLite数据库文件路径
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.SENDER_EMAIL:
            raise ValueError("请配置SENDER_EMAIL环境变量")
        if not cls.SENDER_PASSWORD:
            raise ValueError("请配置SENDER_PASSWORD环境变量")
        if not cls.RECEIVER_EMAIL:
            raise ValueError("请配置RECEIVER_EMAIL环境变量")
