"""
数据模型模块
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Paper:
    """论文数据模型"""
    title: str
    authors: List[str]
    abstract: str
    published: datetime
    url: str
    arxiv_id: str
    categories: List[str]

    def __str__(self):
        """格式化输出"""
        authors_str = ', '.join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f' 等 {len(self.authors)} 位作者'

        return (
            f"标题: {self.title}\n"
            f"作者: {authors_str}\n"
            f"发布时间: {self.published.strftime('%Y-%m-%d')}\n"
            f"分类: {', '.join(self.categories)}\n"
            f"链接: {self.url}\n"
            f"摘要: {self.abstract[:200]}...\n"
        )

    def to_html(self):
        """转换为HTML格式"""
        authors_str = ', '.join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f' 等 {len(self.authors)} 位作者'

        return f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h3 style="margin-top: 0; color: #2c3e50;">{self.title}</h3>
            <p><strong>作者:</strong> {authors_str}</p>
            <p><strong>发布时间:</strong> {self.published.strftime('%Y-%m-%d')}</p>
            <p><strong>分类:</strong> {', '.join(self.categories)}</p>
            <p><a href="{self.url}" style="color: #3498db;">查看论文</a></p>
            <p style="color: #666;"><em>{self.abstract[:300]}...</em></p>
        </div>
        """
