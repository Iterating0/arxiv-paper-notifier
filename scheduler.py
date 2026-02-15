"""
定时任务调度模块
"""
import time
import schedule
from datetime import datetime
from typing import Optional
from crawler import ArxivCrawler
from email_notifier import EmailNotifier
from config import Config


class PaperScheduler:
    """论文爬取调度器"""

    def __init__(self, topic: Optional[str] = None):
        """
        初始化调度器

        Args:
            topic: 爬取主题
        """
        self.topic = topic or Config.DEFAULT_TOPIC
        self.crawler = ArxivCrawler(self.topic)
        self.notifier = EmailNotifier()
        self.is_running = False

    def crawl_and_notify(self):
        """爬取并发送通知"""
        try:
            print(f"\n{'='*50}")
            print(f"开始执行任务: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"主题: {self.topic}")
            print(f"{'='*50}\n")

            # 爬取论文
            papers = self.crawler.crawl_with_limit()

            if not papers:
                print("未找到新论文")
                return

            # 发送邮件
            success = self.notifier.send_email(papers, self.topic)

            if success:
                print("\n任务执行成功！")
            else:
                print("\n任务执行失败！")

        except Exception as e:
            print(f"任务执行出错: {str(e)}")

    def start_daily_schedule(self, time_str: str = "09:00"):
        """
        启动每日定时任务

        Args:
            time_str: 执行时间，格式为"HH:MM"
        """
        print(f"调度器已启动，将在每天 {time_str} 执行爬取任务")
        print(f"爬取主题: {self.topic}")
        print("按 Ctrl+C 停止调度器\n")

        # 设置定时任务
        schedule.every().day.at(time_str).do(self.crawl_and_notify)

        self.is_running = True

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次

        except KeyboardInterrupt:
            print("\n调度器已停止")

    def start_hourly_schedule(self):
        """启动每小时定时任务"""
        print(f"调度器已启动，将每小时执行一次爬取任务")
        print(f"爬取主题: {self.topic}")
        print("按 Ctrl+C 停止调度器\n")

        # 设置定时任务
        schedule.every().hour.do(self.crawl_and_notify)

        self.is_running = True

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            print("\n调度器已停止")

    def start_interval_schedule(self, minutes: int = 30):
        """
        启动间隔定时任务

        Args:
            minutes: 间隔分钟数
        """
        print(f"调度器已启动，将每 {minutes} 分钟执行一次爬取任务")
        print(f"爬取主题: {self.topic}")
        print("按 Ctrl+C 停止调度器\n")

        # 设置定时任务
        schedule.every(minutes).minutes.do(self.crawl_and_notify)

        self.is_running = True

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            print("\n调度器已停止")

    def run_once(self):
        """执行一次爬取任务"""
        self.crawl_and_notify()
