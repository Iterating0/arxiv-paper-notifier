"""
arXiv爬虫模块
"""
import time
import feedparser
from typing import List
from datetime import datetime, timedelta
from config import Config
from models import Paper


class ArxivCrawler:
    """arXiv论文爬虫"""

    def __init__(self, topic: str = None):
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
        # 添加时间过滤
        date_filter = datetime.now() - timedelta(days=days)
        date_str = date_filter.strftime('%Y%m%d')

        # 构建查询: all:主题 + AND + submittedDate:[日期 TO ]
        query = f'all:{self.topic} AND submittedDate:[{date_str}0000 TO {date_str}2359]'
        return query

    def fetch_papers(self, days: int = 1, max_results: int = None) -> List[Paper]:
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

        # 构建请求URL
        url = f'{self.api_url}?search_query={query}&start=0&max_results={max_results}'

        print(f"正在爬取主题: {self.topic} (最近{days}天的论文)...")
        print(f"查询URL: {url}")

        try:
            # 解析RSS feed
            feed = feedparser.parse(url)

            if feed.bozo:
                print(f"警告: 解析feed时出现问题: {feed.bozo_exception}")

            papers = []
            for entry in feed.entries:
                # 提取作者
                authors = []
                if 'authors' in entry:
                    authors = [author.name for author in entry.authors]
                elif 'author' in entry:
                    authors = [entry.author]

                # 提取arXiv ID
                arxiv_id = entry.id.split('/')[-1]

                # 提取分类
                tags = []
                if 'tags' in entry:
                    tags = [tag.term for tag in entry.tags]

                # 解析发布时间
                published = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')

                # 创建论文对象
                paper = Paper(
                    title=entry.title,
                    authors=authors,
                    abstract=entry.summary,
                    published=published,
                    url=entry.link,
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

    def crawl_with_limit(self, max_papers: int = None) -> List[Paper]:
        """
        带限制的爬取

        Args:
            max_papers: 最大论文数

        Returns:
            论文列表
        """
        max_papers = max_papers or Config.MAX_PAPERS_PER_DAY
        return self.fetch_papers(days=Config.CRAWL_INTERVAL_DAYS, max_results=max_papers)
