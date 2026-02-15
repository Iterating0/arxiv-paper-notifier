"""
arXiv爬虫模块
"""
import time
import feedparser
import sqlite3
from typing import List, Optional, Set
from datetime import datetime, timedelta
from urllib.parse import quote
from config import Config
from models import Paper


class ArxivCrawler:
    """arXiv论文爬虫"""

    def __init__(self, topic: Optional[str] = None):
        """
        初始化爬虫

        Args:
            topic: 爬取主题
        """
        self.topic = topic or Config.DEFAULT_TOPIC
        self.api_url = Config.ARXIV_API_URL
        self.request_delay = Config.REQUEST_DELAY
        self.max_results = Config.MAX_RESULTS
        self.sent_paper_ids: Set[str] = set()  # 已发送的论文ID集合

        # 初始化数据库
        self._init_database()
        self._load_sent_papers()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(Config.DB_FILE)
        cursor = conn.cursor()

        # 创建已发送论文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_papers (
                arxiv_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _load_sent_papers(self):
        """加载已发送的论文ID"""
        try:
            conn = sqlite3.connect(Config.DB_FILE)
            cursor = conn.cursor()
            cursor.execute('SELECT arxiv_id FROM sent_papers')
            self.sent_paper_ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            print(f"已加载 {len(self.sent_paper_ids)} 条历史记录")
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")

    def _save_sent_paper(self, paper: Paper):
        """保存已发送的论文到数据库"""
        try:
            conn = sqlite3.connect(Config.DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO sent_papers (arxiv_id, title)
                VALUES (?, ?)
            ''', (paper.arxiv_id, paper.title))
            conn.commit()
            conn.close()
            self.sent_paper_ids.add(paper.arxiv_id)
        except Exception as e:
            print(f"保存论文记录失败: {str(e)}")


    def is_paper_sent(self, arxiv_id: str) -> bool:
        """检查论文是否已发送"""
        return arxiv_id in self.sent_paper_ids

    def _build_query(self, days: int = 1) -> str:
        """
        构建查询字符串

        Args:
            days: 查询最近几天的论文

        Returns:
            查询字符串
        """
        # 构建查询: all:主题（先不添加时间过滤，提高查询成功率）
        query = f'all:{self.topic}'
        return query

    def fetch_papers(self, days: int = 365, max_results: int = 10, check_duplicate: bool = True) -> List[Paper]:
        """
        爬取论文

        Args:
            days: 查询最近几天的论文
            max_results: 最大返回结果数
            check_duplicate: 是否检查重复

        Returns:
            论文列表
        """
        max_results = max_results or self.max_results
        query = self._build_query(days)

        # 构建请求URL（需要对查询字符串进行URL编码）
        encoded_query = quote(query, safe='')
        url = f'{self.api_url}?search_query={encoded_query}&start=0&max_results={max_results}'

        print(f"正在爬取主题: {self.topic} (最近{days}天的论文)...")
        print(f"查询URL: {url}")

        try:
            # 解析RSS feed
            feed = feedparser.parse(url)

            if feed.bozo:
                print(f"警告: 解析feed时出现问题: {feed.bozo_exception}")

            papers = []
            new_papers = []
            duplicate_count = 0

            for entry in feed.entries:
                # 提取作者（确保都是字符串类型）
                authors = []
                if 'authors' in entry:
                    authors = [str(author.name) for author in entry.authors]
                elif 'author' in entry:
                    authors = [str(entry.author)]

                # 提取arXiv ID（确保id是字符串类型）
                entry_id = str(entry.id)
                arxiv_id = entry_id.split('/')[-1]

                # 提取分类（确保都是字符串类型）
                tags = []
                if 'tags' in entry:
                    tags = [str(tag.term) for tag in entry.tags]

                # 解析发布时间（确保published是字符串类型）
                published_str = str(entry.published)
                published = datetime.strptime(published_str, '%Y-%m-%dT%H:%M:%SZ')

                # 创建论文对象（确保所有字符串字段都是str类型）
                paper = Paper(
                    title=str(entry.title),
                    authors=authors,
                    abstract=str(entry.summary),
                    published=published,
                    url=str(entry.link),
                    arxiv_id=arxiv_id,
                    categories=tags
                )

                # 检查重复
                if check_duplicate and self.is_paper_sent(arxiv_id):
                    duplicate_count += 1
                    continue

                new_papers.append(paper)
                papers.append(paper)

            print(f"成功获取 {len(papers)} 篇论文 (新增 {len(new_papers)} 篇, 跳过 {duplicate_count} 篇重复)")

            # 控制爬取频率
            time.sleep(self.request_delay)

            return papers

        except Exception as e:
            print(f"爬取失败: {str(e)}")
            return []

    def mark_papers_sent(self, papers: List[Paper]):
        """
        标记论文为已发送

        Args:
            papers: 论文列表
        """
        for paper in papers:
            self._save_sent_paper(paper)
        print(f"已标记 {len(papers)} 篇论文为已发送")
        #test

    def crawl_with_limit(self, max_papers: int = 10) -> List[Paper]:
        """
        带限制的爬取

        Args:
            max_papers: 最大论文数

        Returns:
            论文列表
        """
        max_papers = max_papers or Config.MAX_PAPERS_PER_DAY
        return self.fetch_papers(days=Config.CRAWL_INTERVAL_DAYS, max_results=max_papers)

    def crawl_until_enough(self, target_count: int = 0, max_rounds: int = 0) -> List[Paper]:
        """
        循环爬取直到达到目标数量或最大轮数

        Args:
            target_count: 目标新论文数量（默认为MAX_PAPERS_PER_DAY）
            max_rounds: 最大爬取轮数（默认为MAX_CRAWL_ROUNDS）

        Returns:
            新论文列表
        """
        target_count = target_count or Config.MAX_PAPERS_PER_DAY
        max_rounds = max_rounds or Config.MAX_CRAWL_ROUNDS

        all_new_papers = []
        seen_ids = set()  # 本次爬取中已看到的论文ID，避免重复
        round_num = 0  # 初始化轮数

        for round_num in range(1, max_rounds + 1):
            print(f"\n--- 第 {round_num} 轮爬取 ---")

            # 爬取论文
            papers = self.fetch_papers(
                days=Config.CRAWL_INTERVAL_DAYS,
                max_results=Config.CRAWL_RESULTS
            )

            if not papers:
                print("本轮未获取到论文")
                continue

            # 过滤出本次爬取中的新论文（不在seen_ids中，也不在数据库中）
            round_new_papers = []
            for paper in papers:
                if paper.arxiv_id not in seen_ids and not self.is_paper_sent(paper.arxiv_id):
                    round_new_papers.append(paper)
                    seen_ids.add(paper.arxiv_id)

            print(f"本轮获取 {len(papers)} 篇论文，新增 {len(round_new_papers)} 篇")

            # 将本轮新论文添加到总列表
            all_new_papers.extend(round_new_papers)

            # 检查是否达到目标
            if len(all_new_papers) >= target_count:
                print(f"\n已达到目标数量 {target_count} 篇新论文")
                break

        print(f"\n=== 爬取完成 ===")
        print(f"共进行 {round_num} 轮爬取")
        print(f"总共找到 {len(all_new_papers)} 篇新论文")

        return all_new_papers
