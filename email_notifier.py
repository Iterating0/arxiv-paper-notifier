"""
邮件通知模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from config import Config
from models import Paper


class EmailNotifier:
    """邮件通知器"""

    def __init__(self):
        """初始化邮件通知器"""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.SENDER_PASSWORD
        self.receiver_email = Config.RECEIVER_EMAIL

    def _create_email_content(self, papers: List[Paper], topic: str) -> str:
        """
        创建邮件内容

        Args:
            papers: 论文列表
            topic: 主题

        Returns:
            HTML格式的邮件内容
        """
        today = datetime.now().strftime('%Y年%m月%d日')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .stats {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .paper-item {{
                    border: 1px solid #e0e0e0;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 8px;
                    transition: box-shadow 0.3s;
                }}
                .paper-item:hover {{
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .paper-title {{
                    color: #2c3e50;
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 0;
                }}
                .paper-meta {{
                    color: #666;
                    font-size: 14px;
                    margin: 10px 0;
                }}
                .paper-link {{
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 8px 16px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .paper-link:hover {{
                    background: #2980b9;
                }}
                .paper-abstract {{
                    color: #555;
                    font-style: italic;
                    line-height: 1.5;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 arXiv论文日报</h1>
                <p>主题: {topic}</p>
                <p>日期: {today}</p>
            </div>

            <div class="stats">
                <h3>📊 今日统计</h3>
                <p>共获取 <strong>{len(papers)}</strong> 篇相关论文</p>
            </div>

            <div class="papers">
        """

        for i, paper in enumerate(papers, 1):
            authors_str = ', '.join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += f' 等 {len(paper.authors)} 位作者'

            html_content += f"""
                <div class="paper-item">
                    <h3 class="paper-title">{i}. {paper.title}</h3>
                    <div class="paper-meta">
                        <p><strong>👤 作者:</strong> {authors_str}</p>
                        <p><strong>📅 发布时间:</strong> {paper.published.strftime('%Y-%m-%d')}</p>
                        <p><strong>🏷️ 分类:</strong> {', '.join(paper.categories)}</p>
                    </div>
                    <a href="{paper.url}" class="paper-link">📄 查看论文</a>
                    <p class="paper-abstract">{paper.abstract}</p>
                </div>
            """

        html_content += f"""
            </div>

            <div class="footer">
                <p>本邮件由 arXiv论文爬虫自动发送</p>
                <p>如需取消订阅，请联系发送者</p>
            </div>
        </body>
        </html>
        """

        return html_content

    def send_email(self, papers: List[Paper], topic: str) -> bool:
        """
        发送邮件

        Args:
            papers: 论文列表
            topic: 主题

        Returns:
            是否发送成功
        """
        if not papers:
            print("没有论文需要发送")
            return False

        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = self.receiver_email
            message['Subject'] = f'📚 arXiv论文日报 - {topic} - {datetime.now().strftime("%Y-%m-%d")}'

            # 创建HTML内容
            html_content = self._create_email_content(papers, topic)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)

            # 连接SMTP服务器并发送
            print(f"正在连接SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"邮件已成功发送至: {self.receiver_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("错误: SMTP认证失败，请检查邮箱和密码")
            print("注意: 如果使用Gmail，需要使用应用专用密码而非普通密码")
            return False
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False
