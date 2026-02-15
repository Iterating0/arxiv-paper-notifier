"""
arXiv论文爬虫主程序
"""
import argparse
import sys
from config import Config
from scheduler import PaperScheduler


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='arXiv论文爬虫 - 自动爬取并发送论文到邮箱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 执行一次爬取
  python main.py -t "machine learning" --once

  # 每天早上9点自动爬取
  python main.py -t "deep learning" --daily 09:00

  # 每小时自动爬取
  python main.py -t "computer vision" --hourly

  # 每30分钟自动爬取
  python main.py -t "natural language processing" --interval 30
        """
    )

    parser.add_argument(
        '-t', '--topic',
        type=str,
        default=None,
        help='爬取主题（默认使用配置文件中的主题）'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='执行一次爬取任务'
    )

    parser.add_argument(
        '--daily',
        type=str,
        metavar='TIME',
        help='每日定时执行，格式为HH:MM（如09:00）'
    )

    parser.add_argument(
        '--hourly',
        action='store_true',
        help='每小时执行一次'
    )

    parser.add_argument(
        '--interval',
        type=int,
        metavar='MINUTES',
        help='每隔指定分钟数执行一次'
    )

    args = parser.parse_args()

    try:
        # 验证配置
        Config.validate()

        # 创建调度器
        scheduler = PaperScheduler(args.topic)

        # 根据参数执行不同的调度模式
        if args.once:
            print("执行一次性爬取任务...")
            scheduler.run_once()
        elif args.daily:
            scheduler.start_daily_schedule(args.daily)
        elif args.hourly:
            scheduler.start_hourly_schedule()
        elif args.interval:
            scheduler.start_interval_schedule(args.interval)
        else:
            # 默认：每天早上9点执行
            print("未指定调度模式，使用默认配置：每天09:00执行")
            parser.print_help()
            print("\n启动默认调度...")
            scheduler.start_daily_schedule("09:00")

    except ValueError as e:
        print(f"配置错误: {str(e)}")
        print("\n请先配置.env文件：")
        print("1. 复制.env.example为.env")
        print("2. 填写邮箱相关信息")
        print("3. 配置发送者邮箱和应用专用密码")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"程序出错: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
