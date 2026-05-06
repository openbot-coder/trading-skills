#!/usr/bin/env python3
"""
获取股票行情（使用 westockdata）

使用方式:
    python get_quote.py hk00700        # 腾讯控股
    python get_quote.py hk00700 usAAPL  # 多只股票
"""

import argparse
import subprocess
import sys
import json


def run_westock_command(command: str):
    """运行 westockdata 命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"命令执行失败: {result.stderr}")
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print("命令执行超时")
        return None
    except Exception as e:
        print(f"执行命令失败: {e}")
        return None


def get_quote(symbol: str):
    """获取单只股票行情"""
    # 尝试使用 westockdata 的命令
    # 这里根据 westockdata 的实际用法调整
    command = f'npx -y westock-data-clawhub@1.0.4 quote {symbol}'
    output = run_westock_command(command)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="获取股票行情",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python get_quote.py hk00700        # 腾讯控股
    python get_quote.py usAAPL         # 苹果
    python get_quote.py hk00700 usAAPL  # 多只股票

注意: 需要先安装 westock-data-clawhub (npm install -g westock-data-clawhub)
或使用 npx 运行
"""
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="股票代码 (例如: hk00700, usAAPL)",
    )
    args = parser.parse_args()

    for symbol in args.symbols:
        print(f"\n{'='*60}")
        print(f"查询: {symbol}")
        print(f"{'='*60}")
        output = get_quote(symbol)
        if output:
            print(output)


if __name__ == "__main__":
    main()
