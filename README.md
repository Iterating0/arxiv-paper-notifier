# arXiv论文爬虫

自动爬取arXiv论文并发送到邮箱的Python工具。

## 功能特性

- 根据主题自动爬取arXiv最新论文
- 合理控制爬取频率，遵守arXiv API限制
- 支持每日/每小时/自定义间隔定时推送
- 精美的HTML邮件模板
- 简单易用的命令行接口

## 安装

1. 克隆或下载项目

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板：
```bash
cp .env.example .env
```

2. 编辑`.env`文件，填入邮箱配置：
```env
# 邮箱配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECEIVER_EMAIL=receiver@example.com

# 爬虫配置
DEFAULT_TOPIC=machine learning
MAX_PAPERS_PER_DAY=10
CRAWL_INTERVAL_DAYS=1
```

### 重要提示

如果使用Gmail作为发送邮箱，需要使用"应用专用密码"而非普通密码：
1. 访问 https://myaccount.google.com/security
2. 启用两步验证
3. 生成应用专用密码
4. 将生成的密码填入`SENDER_PASSWORD`

## 使用方法

### 执行一次爬取
```bash
python main.py -t "machine learning" --once
```

### 每天定时爬取（例如每天早上9点）
```bash
python main.py -t "deep learning" --daily 09:00
```

### 每小时爬取
```bash
python main.py -t "computer vision" --hourly
```

### 自定义间隔（例如每30分钟）
```bash
python main.py -t "natural language processing" --interval 30
```

### 使用配置文件中的主题
```bash
python main.py --once
```

## 命令行参数

- `-t, --topic`: 指定爬取主题
- `--once`: 执行一次爬取任务
- `--daily TIME`: 每日定时执行，格式为HH:MM
- `--hourly`: 每小时执行一次
- `--interval MINUTES`: 每隔指定分钟数执行一次

## 项目结构

```
arxiv-crawler/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── crawler.py           # arXiv爬虫
├── email_notifier.py    # 邮件通知
├── scheduler.py         # 定时任务调度
├── models.py            # 数据模型
├── requirements.txt     # 依赖列表
├── .env.example         # 配置文件模板
└── README.md           # 项目说明
```

## 注意事项

1. **爬取频率控制**: 程序已内置请求间隔（默认3秒），遵守arXiv API使用规范
2. **邮件发送**: 确保邮箱SMTP服务已开启，且使用正确的应用专用密码
3. **主题搜索**: 使用英文关键词搜索效果更好
4. **定时任务**: 保持程序运行才能执行定时任务，建议使用nohup或screen在后台运行

## 后台运行（Linux/Mac）

使用nohup在后台运行：
```bash
nohup python main.py -t "machine learning" --daily 09:00 > crawler.log 2>&1 &
```

使用screen：
```bash
screen -S arxiv-crawler
python main.py -t "machine learning" --daily 09:00
# 按 Ctrl+A+D 退出screen
```

## 许可证

MIT License
