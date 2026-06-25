"""
Mimo Vision MCP Server

为 Claude Code 提供图片识别能力，暴露 analyze_image 工具，
底层调用 Mimo API（mimo-v2-omni 多模态模型）。

启动方式:
    python server.py

注册到 Claude Code:
    claude mcp add mimo-vision -- python d:/BaiduSyncdisk/claude/mimo-vision/server.py
"""

import os
import sys

from mcp.server.fastmcp import FastMCP

# 将项目目录加入 Python 路径，确保导入 mimo_vision
_project_dir = os.path.dirname(os.path.abspath(__file__))
if _project_dir not in sys.path:
    sys.path.insert(0, _project_dir)

from mimo_vision import load_config, analyze_image, validate_config

mcp = FastMCP(
    "Mimo Vision",
    instructions=(
        "图片识别工具。当用户需要分析图片内容时，调用此工具。"
        "支持 png/jpg/jpeg/gif/bmp/webp 格式。"
        "工具会返回图片的文字描述、数字、表格等结构化信息。"
    ),
)


@mcp.tool()
def analyze_image_tool(image_path: str, prompt: str = "") -> str:
    """识别本地图片中的内容（文字、数字、表格、图表等）

    Args:
        image_path: 图片文件的完整路径 (如 C:\\Users\\xxx\\图片.png)
        prompt: 分析提示词，留空则自动使用默认提示词进行全面分析
    """
    config = load_config()

    try:
        validate_config(config)
    except ValueError as e:
        return f"配置错误: {e}"

    try:
        result = analyze_image(
            image_path,
            prompt if prompt else None,
            config,
        )
        return result
    except FileNotFoundError as e:
        return f"文件不存在: {e}"
    except ValueError as e:
        return f"文件错误: {e}"
    except RuntimeError as e:
        return f"API 调用失败: {e}"
    except Exception as e:
        return f"未知错误: {type(e).__name__}: {e}"


def main():
    print("Mimo Vision MCP Server 启动中...", file=sys.stderr)
    config = load_config()
    try:
        validate_config(config)
        print(f"  模型: {config['model']}", file=sys.stderr)
        print(f"  API:  已配置", file=sys.stderr)
        print("  MCP Server 已就绪 (stdio)", file=sys.stderr)
    except ValueError as e:
        print(f"  ⚠ {e}", file=sys.stderr)
        print("  请先配置 config.json 中的 api_key", file=sys.stderr)

    mcp.run()


if __name__ == "__main__":
    main()
