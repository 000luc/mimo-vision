"""
mimo_vision.py — Mimo API 图片识别核心模块

共享给 CLI (analyze_img.py) 和 MCP Server (server.py) 使用。
"""

import base64
import json
import os
import mimetypes
import sys

try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    from urllib2 import Request, urlopen, URLError, HTTPError  # type: ignore

# ── 默认提示词 ──────────────────────────────────────────
DEFAULT_PROMPT = (
    "详细分析这张图片，完整输出所有可见信息："
    "1) 图片类型（截图、表格、票据、照片、图表等）；"
    "2) 所有文字内容；"
    "3) 数字和数据；"
    "4) 表格或结构化信息（用 Markdown 表格格式输出）；"
    "5) 布局和颜色等视觉特征。"
    "尽量详尽，不要遗漏任何信息。"
)

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
}


def load_config(config_dir: str = None) -> dict:
    """
    加载配置，优先级: 环境变量 > config.json > 默认值

    Args:
        config_dir: 配置文件所在目录，默认当前文件所在目录

    Returns:
        dict: 含 api_key, model, base_url
    """
    if config_dir is None:
        config_dir = os.path.dirname(os.path.abspath(__file__))

    config = {
        "api_key": os.environ.get("MIMO_API_KEY", ""),
        "model": "mimo-v2-omni",
        "base_url": "https://api.xiaomimimo.com/v1",
    }

    config_path = os.path.join(config_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            file_config = json.load(f)
        for key in ("api_key", "model", "base_url"):
            if key in file_config and not (key == "api_key" and config["api_key"]):
                config[key] = file_config[key]

    return config


def validate_config(config: dict):
    """检查配置是否完整"""
    if not config.get("api_key"):
        raise ValueError(
            "未配置 API Key。请在 config.json 中设置 api_key，"
            "或设置环境变量 MIMO_API_KEY。"
        )


def encode_image(image_path: str) -> tuple:
    """
    读取图片并返回 data URI 形式的 base64 字符串

    Args:
        image_path: 图片文件路径

    Returns:
        (data_uri, mime_type) 如 ("data:image/png;base64,xxxxx", "image/png")

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 格式不支持或文件过大
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"文件不存在: {image_path}")

    file_size = os.path.getsize(image_path)
    if file_size > 20 * 1024 * 1024:
        raise ValueError(
            f"文件过大 ({file_size / 1024 / 1024:.1f}MB)，"
            f"Mimo 最大支持约 20MB"
        )

    ext = os.path.splitext(image_path)[1].lower()
    mime_type = MIME_MAP.get(ext)
    if not mime_type:
        # 尝试通过 mimetypes 猜测
        mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(
            f"不支持的文件格式 '{ext}'，"
            f"支持: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    return f"data:{mime_type};base64,{img_b64}", mime_type


def _call_mimo_api(data_uri: str, prompt: str, config: dict) -> str:
    """
    调用 Mimo API 识图（核心方法，data_uri 已编码好）

    Args:
        data_uri: 图片 data URI，如 "data:image/png;base64,xxxxx"
        prompt: 提示词
        config: 配置字典

    Returns:
        str: API 返回的识别结果文本
    """
    payload = {
        "model": config["model"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                ],
            }
        ],
        "max_tokens": 2048,
    }

    url = f"{config['base_url'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

    req = Request(url, data=json.dumps(payload).encode(), headers=headers)

    try:
        resp = urlopen(req, timeout=120)
        result = json.loads(resp.read().decode())
        return result["choices"][0]["message"]["content"]
    except HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"API 错误 (HTTP {e.code}): {err_body}")
    except URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def analyze_image(image_path: str, prompt: str = None, config: dict = None) -> str:
    """
    调用 Mimo API 识别本地图片文件内容

    Args:
        image_path: 图片文件路径
        prompt: 提示词，不传则使用 DEFAULT_PROMPT
        config: 配置字典，不传则自动加载

    Returns:
        str: API 返回的识别结果文本
    """
    if config is None:
        config = load_config()
    validate_config(config)

    if prompt is None:
        prompt = DEFAULT_PROMPT

    data_uri, _ = encode_image(image_path)
    return _call_mimo_api(data_uri, prompt, config)


def analyze_image_data(
    image_data: str,
    image_format: str = "png",
    prompt: str = None,
    config: dict = None,
) -> str:
    """
    调用 Mimo API 识别图片内容（直接传 base64 数据，不依赖文件路径）

    Args:
        image_data: 图片的 base64 编码字符串
        image_format: 图片格式，默认 png，支持 png/jpg/jpeg/gif/bmp/webp
        prompt: 提示词，不传则使用 DEFAULT_PROMPT
        config: 配置字典，不传则自动加载

    Returns:
        str: API 返回的识别结果文本
    """
    if config is None:
        config = load_config()
    validate_config(config)

    if prompt is None:
        prompt = DEFAULT_PROMPT

    fmt = image_format.lower().lstrip(".")
    mime_type = MIME_MAP.get(f".{fmt}")
    if not mime_type:
        raise ValueError(
            f"不支持的图片格式 '{fmt}'，支持: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    data_uri = f"data:{mime_type};base64,{image_data}"
    return _call_mimo_api(data_uri, prompt, config)
