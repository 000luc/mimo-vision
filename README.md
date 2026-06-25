# Mimo Vision

基于小米 MiMo（馍馍）多模态大模型的本地图片识别工具。支持 **CLI 命令行** 和 **MCP Server** 两种使用方式，可作为 Claude Code / Cursor / 其他 AI 编程工具的识图补充。

当你的 AI 编程助手（通过 DeepSeek、Kimi 等非 Claude 模型接入）没有识图能力时，Mimo Vision 提供一条额外的视觉通道。

## 功能

- 识别本地图片中的文字、表格、数字、图表等内容
- 支持 PNG / JPG / JPEG / GIF / BMP / WebP 格式
- CLI 模式：在终端直接调用，适合手动分析
- MCP Server 模式：注册为 AI 编程工具的 MCP 工具，自动调用
- 默认智能提示词自动分析图片，也支持自定义提示词

## 前置要求

- Python 3.8+
- 小米 MiMo API Key（[申请地址](https://platform.xiaomimimo.com)）
- `mcp` 包（仅 MCP Server 模式需要）

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/mimo-vision.git
cd mimo-vision

# （可选）安装 MCP 依赖
pip install mcp
```

### 2. 配置 API Key

复制配置模板并填入你的 API Key：

```bash
cp config.example.json config.json
```

编辑 `config.json`：

```json
{
  "api_key": "sk-your-mimo-api-key",
  "model": "mimo-v2-omni",
  "base_url": "https://api.xiaomimimo.com/v1"
}
```

> 也可以设置环境变量 `MIMO_API_KEY` 来替代配置文件中的 `api_key`，环境变量优先级更高。

### 3. CLI 模式测试

```bash
python analyze_img.py 测试图片.png
```

如果看到详细的分析结果，说明配置成功。

## CLI 用法

```bash
# 使用默认提示词全面分析
python analyze_img.py 报表截图.png

# 自定义提示词提取特定信息
python analyze_img.py 发票.jpg -p "提取发票号码、金额和日期"

# 路径包含空格时加引号
python analyze_img.py "C:\My Documents\图片.png" -p "描述这张图表"

# Windows 用户也可用 py 启动器
py analyze_img.py 图片.png
```

默认提示词会自动分析：图片类型、文字内容、数字数据、表格结构、布局颜色等。

## MCP Server 模式

MCP Server 模式让 AI 编程工具（如 Claude Code）能自动调用图片识别能力，无需手动操作。

### 配置方式

在项目的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "mimo-vision": {
      "command": "python",
      "args": ["path/to/mimo-vision/server.py"]
    }
  }
}
```

> Windows 用户如果 `python` 命令不可用，可改为 `"py"`。

### 在 Claude Code 中使用

配置后重启 Claude Code，MCP 工具会自动注册。当需要分析图片时，直接告诉 Claude Code：

> "帮我看一下这张图：C:\图片.png"
>
> "分析这个截图里的数据"

Claude Code 会自动调用 `analyze_image` 工具，将图片发送给 Mimo 模型分析并返回结果。

### 可用工具

| 工具名 | 参数 | 说明 |
| --- | --- | --- |
| analyze_image_tool | image_path, prompt | 识别本地图片内容 |

## 项目结构

```text
mimo-vision/
├── mimo_vision.py        # 核心库：封装 Mimo API 调用逻辑
├── analyze_img.py        # CLI 入口
├── server.py             # MCP Server 入口
├── config.example.json   # 配置模板（提交到 GitHub）
├── config.json           # 实际配置（含 API Key，已 gitignore）
├── .mcp.example.json     # MCP 配置示例
├── .gitignore
└── README.md
```

## 安全注意事项

- **`config.json`** 包含 API Key，已加入 `.gitignore`，**不要提交到 GitHub**
- 提交前检查是否误将 `config.json` 加入版本控制
- 如使用 Git 管理，建议先 `git add` 时确认文件列表

## 技术说明

- Mimo API 兼容 OpenAI 消息格式
- 本地图片通过 Base64 编码后以 `data:` URI 形式发送
- 推荐模型 `mimo-v2-omni`（支持图像理解），也可用 `mimo-v2.5`

## License

MIT
