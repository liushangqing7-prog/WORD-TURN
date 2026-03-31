# Word Turn：本地 Word 文档规则替换工具

这是一个**本地运行、开源、可二次开发**的 `.docx` 文档文字替换工具，项目名称统一为 **Word Turn**。

你可以上传 Word 文档，然后按内置格式填写替换规则，程序会自动识别并修改文档内容，最后直接下载修改后的文件。

## 功能特点

- ✅ 本地运行，不依赖云端
- ✅ 可视化界面（Streamlit）
- ✅ 支持规则化替换（普通文本 / 正则）
- ✅ 支持正文和表格中的文字替换
- ✅ 开源，便于用户自行修改与扩展
- ✅ 新增 Windows 启动器（`word_turn_launcher.py` + `start_word_turn.bat`）
- ✅ 内置自检与自动修复流程（依赖、目录、读写环境）
- ✅ 采用加权健康指数（数学方法）展示系统状态

## 替换规则格式（内置规范）

每行一条规则：

```text
literal:旧文本=>新文本
regex:正则表达式=>新文本
```

说明：

- `literal`：纯文本替换
- `regex`：正则替换
- 允许空行
- 允许注释行（`#` 开头）

示例：

```text
# 常规替换
literal:甲方=>采购方
literal:乙方=>供应商

# 日期格式 2026/03/31 -> 2026-03-31
regex:(\d{4})/(\d{2})/(\d{2})=>$1-$2-$3
```

> 正则替换支持 `$1`、`$2` 这种分组写法。

## 运行方式

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 启动程序（跨平台）

```bash
streamlit run app.py
```

### 3) 启动程序（Windows 推荐）

双击 `start_word_turn.bat`，或在命令行执行：

```bat
start_word_turn.bat
```

该启动器会打开 `Word Turn` 桌面启动面板，提供：

- 运行自检
- 一键修复
- 启动 Web 主程序

## 启动器自检项

- Python 版本（要求 3.10+）
- 依赖包（`streamlit`, `python-docx`）
- 临时目录读写能力
- 核心项目文件完整性
- `output` 输出目录存在性

系统健康指数使用加权求和方式：

- 总分 100
- 各项通过后按权重累加
- 用于快速判断运行环境稳定性

## 项目结构

```text
.
├── app.py                   # Streamlit 页面
├── word_replacer.py         # 核心替换逻辑与规则解析
├── word_turn_launcher.py    # Windows 启动器（自检 + 修复 + 启动）
├── start_word_turn.bat      # Windows 一键启动脚本
├── tests/test_replacer.py
├── requirements.txt
├── LICENSE
└── README.md
```

## 开发与扩展建议

你可以在 `word_replacer.py` 中继续扩展：

- 增加页眉/页脚替换
- 增加替换前预览 diff
- 增加“只替换第 N 次出现”
- 增加“区分大小写/全词匹配”开关

## 开源协议

本项目采用 MIT License，可自由使用与修改。
