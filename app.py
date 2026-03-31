from __future__ import annotations

from pathlib import Path
import tempfile

import streamlit as st

from word_replacer import apply_rules_to_docx, parse_rules


st.set_page_config(page_title="Word 文档批量替换器", page_icon="📝", layout="centered")

st.title("📝 Word 文档文字替换工具（本地运行）")
st.write(
    "上传 `.docx` 文件，填写规则后即可自动替换并下载修改后的文档。"
)

with st.expander("查看内置规则格式说明（建议先读）", expanded=True):
    st.markdown(
        """
### 规则语法（每行一条）
- `literal:旧文本=>新文本`：普通文本替换
- `regex:正则表达式=>新文本`：正则替换

### 示例
```text
# 把“甲方”替换为“采购方”
literal:甲方=>采购方

# 日期格式 2026/03/31 -> 2026-03-31
regex:(\d{4})/(\d{2})/(\d{2})=>$1-$2-$3
```

> 说明：
> 1. 支持注释行（以 `#` 开头）和空行。
> 2. 替换范围：正文段落 + 表格中的段落。
> 3. 仅支持 `.docx`（不支持旧版 `.doc`）。
"""
    )

uploaded_file = st.file_uploader("上传 Word 文档（.docx）", type=["docx"])
default_rules = """# 常规替换
literal:甲方=>采购方
literal:乙方=>供应商
"""
rules_text = st.text_area("替换规则", value=default_rules, height=220)

output_name = st.text_input("输出文件名", value="modified.docx")

if st.button("开始替换", type="primary"):
    if not uploaded_file:
        st.error("请先上传一个 .docx 文件。")
    else:
        try:
            rules = parse_rules(rules_text)
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = Path(tmpdir) / "input.docx"
                output_path = Path(tmpdir) / output_name
                input_path.write_bytes(uploaded_file.getvalue())

                changed_count = apply_rules_to_docx(
                    str(input_path), str(output_path), rules
                )
                output_bytes = output_path.read_bytes()

            st.success(f"处理完成！共修改 {changed_count} 个段落。")
            st.download_button(
                label="下载修改后的文档",
                data=output_bytes,
                file_name=output_name,
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"处理失败：{exc}")
