"""
analyze_img.py — Mimo 图片识别 CLI 工具

用法:
    py analyze_img.py <图片路径> [-p <提示词>]
    py analyze_img.py <图片路径>                     # 使用默认提示词
    py analyze_img.py C:\图片.png -p "提取表格里的数字"

示例:
    py analyze_img.py 截图.png
    py analyze_img.py 发票.jpg -p "提取发票号码、金额和日期"
"""

import argparse
import os
import sys

from mimo_vision import (
    load_config,
    analyze_image,
    DEFAULT_PROMPT,
)


def main():
    parser = argparse.ArgumentParser(
        description="调用 Mimo API 识别图片内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("image_path", help="图片文件路径")
    parser.add_argument(
        "-p", "--prompt",
        help=f"自定义提示词（默认: 通用详细分析）",
    )
    args = parser.parse_args()

    config = load_config()

    # 显示基本信息
    abs_path = os.path.abspath(args.image_path)
    if os.path.exists(abs_path):
        file_size = os.path.getsize(abs_path)
        print(f"模型: {config['model']}")
        print(f"图片: {abs_path} ({file_size / 1024:.1f} KB)")
        print(f"提示: {'自定义' if args.prompt else '默认'}")
        print("-" * 40)
    sys.stdout.flush()

    try:
        result = analyze_image(args.image_path, args.prompt, config)
        print(result)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
