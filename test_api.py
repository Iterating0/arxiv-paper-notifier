"""
测试arXiv API
"""
import feedparser
from urllib.parse import quote
from config import Config

def test_api():
    """测试API连接"""

    # 测试不同的查询方式
    tests = [
        ("不带时间限制", "all:physics"),
        ("带时间限制（最近3天）", "all:physics AND submittedDate:[202602120000 TO 202602152359]"),
        ("更具体的主题", "all:quantum mechanics"),
    ]

    for test_name, query in tests:
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")

        encoded_query = quote(query, safe='')
        url = f'{Config.ARXIV_API_URL}?search_query={encoded_query}&start=0&max_results=3'

        print(f"查询: {query}")
        print(f"URL: {url}\n")

        try:
            # 解析RSS feed
            feed = feedparser.parse(url)

            print(f"API状态: {'成功' if not feed.bozo else '失败'}")
            print(f"找到论文数量: {len(feed.entries)}\n")

            # 显示论文
            if len(feed.entries) > 0:
                for i, entry in enumerate(feed.entries[:3], 1):
                    print(f"--- 论文 {i} ---")
                    print(f"标题: {entry.title[:100]}...")
                    print(f"作者: {entry.get('author', 'N/A')}")
                    print(f"发布时间: {entry.get('published', 'N/A')}")
                    print()
            else:
                print("未找到论文")

        except Exception as e:
            print(f"API测试失败: {str(e)}")

if __name__ == '__main__':
    test_api()
