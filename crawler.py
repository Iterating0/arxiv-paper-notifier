"""
arXiv爬虫模块
"""
import time
import feedparser
from typing import List, Optional
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

    def fetch_papers(self, days: int = 365, max_results: int = 10) -> List[Paper]:
        """
        爬取论文

        Args:
            days: 查询最近几天的论文
            max_results: 最大返回结果数

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
                papers.append(paper)

            print(f"成功获取 {len(papers)} 篇论文")

            # 控制爬取频率
            time.sleep(self.request_delay)

            return papers

        except Exception as e:
            print(f"爬取失败: {str(e)}")
            return []

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
