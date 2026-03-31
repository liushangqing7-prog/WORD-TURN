from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

APP_NAME = "Word Turn"


@dataclass(frozen=True)
class ColorSystem:
    background: str = "#F5F7FB"
    panel: str = "#FFFFFF"
    primary: str = "#2F5DFF"
    primary_hover: str = "#244BE0"
    success: str = "#2E9B5F"
    warning: str = "#D89C1E"
    danger: str = "#CF3F5A"
    text_primary: str = "#1A1F36"
    text_secondary: str = "#505A77"
    border: str = "#DCE2F0"


@dataclass
class CheckResult:
    item: str
    ok: bool
    detail: str
    repair: Callable[[], tuple[bool, str]] | None = None


REQUIRED_PACKAGES = ["streamlit", "python-docx"]


def _check_python_version() -> CheckResult:
    ok = sys.version_info >= (3, 10)
    detail = f"当前 Python 版本: {sys.version.split()[0]}"
    return CheckResult("Python 版本", ok, detail)


def _repair_package(package: str) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "pip", "install", package]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return True, f"已安装 {package}"
    return False, (proc.stderr or proc.stdout or "安装失败").strip()


def _check_package(package: str, import_name: str | None = None) -> CheckResult:
    module_name = import_name or package.replace("-", "_")
    try:
        __import__(module_name)
        return CheckResult(f"依赖包 {package}", True, "已安装")
    except Exception:
        return CheckResult(
            f"依赖包 {package}",
            False,
            "未安装",
            repair=lambda p=package: _repair_package(p),
        )


def _check_temp_rw() -> CheckResult:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "word_turn_probe.txt"
            path.write_text("probe", encoding="utf-8")
            if path.read_text(encoding="utf-8") != "probe":
                raise OSError("内容校验失败")
        return CheckResult("临时目录读写", True, "临时目录可读写")
    except Exception as exc:
        return CheckResult("临时目录读写", False, f"读写失败: {exc}")


def _check_project_files() -> CheckResult:
    missing = [name for name in ["app.py", "word_replacer.py", "requirements.txt"] if not Path(name).exists()]
    if missing:
        return CheckResult("核心文件", False, f"缺失文件: {', '.join(missing)}")
    return CheckResult("核心文件", True, "核心文件完整")


def _repair_output_dir() -> tuple[bool, str]:
    try:
        Path("output").mkdir(exist_ok=True)
        return True, "已创建 output 目录"
    except Exception as exc:
        return False, f"创建 output 目录失败: {exc}"


def _check_output_dir() -> CheckResult:
    output = Path("output")
    if output.exists() and output.is_dir():
        return CheckResult("输出目录", True, "output 目录已就绪")
    return CheckResult("输出目录", False, "缺少 output 目录", repair=_repair_output_dir)


def run_self_check() -> tuple[list[CheckResult], float]:
    checks = [
        _check_python_version(),
        _check_package("streamlit"),
        _check_package("python-docx", import_name="docx"),
        _check_temp_rw(),
        _check_project_files(),
        _check_output_dir(),
    ]

    # 数学方法：加权健康指数（满分 100）
    weights = [20, 18, 18, 16, 16, 12]
    score = sum(weight for result, weight in zip(checks, weights) if result.ok)
    return checks, float(score)


def start_streamlit() -> subprocess.Popen[str]:
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    return subprocess.Popen(cmd)


class LauncherApp:
    def __init__(self) -> None:
        self.colors = ColorSystem()
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} 启动器")
        self.root.geometry("820x600")
        self.root.configure(bg=self.colors.background)

        self._proc: subprocess.Popen[str] | None = None

        self._build_styles()
        self._build_ui()
        self._initial_check()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors.background)
        style.configure("Card.TFrame", background=self.colors.panel, borderwidth=1, relief="solid")
        style.configure("Title.TLabel", background=self.colors.background, foreground=self.colors.text_primary, font=("Segoe UI", 20, "bold"))
        style.configure("Sub.TLabel", background=self.colors.background, foreground=self.colors.text_secondary, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=self.colors.panel, foreground=self.colors.text_primary, font=("Segoe UI", 11, "bold"))
        style.configure("CardBody.TLabel", background=self.colors.panel, foreground=self.colors.text_secondary, font=("Segoe UI", 10))
        style.configure("Accent.TButton", foreground="white", background=self.colors.primary, font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Accent.TButton", background=[("active", self.colors.primary_hover)])

    def _build_ui(self) -> None:
        wrapper = ttk.Frame(self.root, padding=20)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(wrapper, text="Windows 本地启动 · 自检修复 · 优雅简洁 UI", style="Sub.TLabel").pack(anchor="w", pady=(0, 14))

        card = ttk.Frame(wrapper, style="Card.TFrame", padding=14)
        card.pack(fill="x")
        ttk.Label(card, text="系统状态", style="CardTitle.TLabel").pack(anchor="w")

        self.score_var = tk.StringVar(value="健康指数: 检测中...")
        ttk.Label(card, textvariable=self.score_var, style="CardBody.TLabel").pack(anchor="w", pady=(8, 8))

        self.status_text = tk.Text(card, height=14, bd=0, relief="flat", bg=self.colors.panel, fg=self.colors.text_secondary, font=("Consolas", 10))
        self.status_text.pack(fill="both", expand=True)
        self.status_text.configure(state="disabled")

        controls = ttk.Frame(wrapper)
        controls.pack(fill="x", pady=(14, 0))
        ttk.Button(controls, text="运行自检", style="Accent.TButton", command=self.run_checks).pack(side="left")
        ttk.Button(controls, text="一键修复", style="Accent.TButton", command=self.auto_repair).pack(side="left", padx=8)
        ttk.Button(controls, text="启动 Word Turn", style="Accent.TButton", command=self.launch_app).pack(side="left")

    def _append_status(self, text: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.insert("end", text + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _set_status_lines(self, lines: list[str]) -> None:
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", "\n".join(lines) + "\n")
        self.status_text.configure(state="disabled")

    def _initial_check(self) -> None:
        self.run_checks()

    def run_checks(self) -> None:
        checks, score = run_self_check()
        lines: list[str] = []
        for item in checks:
            icon = "✅" if item.ok else "❌"
            lines.append(f"{icon} {item.item}: {item.detail}")
        self._set_status_lines(lines)
        self.score_var.set(f"健康指数: {score:.0f}/100")

    def auto_repair(self) -> None:
        checks, _ = run_self_check()
        repairs = [item for item in checks if (not item.ok and item.repair)]
        if not repairs:
            messagebox.showinfo(APP_NAME, "未发现可自动修复的问题。")
            return

        self._append_status("开始自动修复...")
        for item in repairs:
            ok, detail = item.repair() if item.repair else (False, "无修复方法")
            icon = "✅" if ok else "❌"
            self._append_status(f"{icon} 修复 {item.item}: {detail}")

        self.run_checks()

    def launch_app(self) -> None:
        def _run() -> None:
            try:
                self._proc = start_streamlit()
                self._append_status("✅ 已启动 Streamlit，请在浏览器查看输出地址。")
            except Exception as exc:
                self._append_status(f"❌ 启动失败: {exc}")

        threading.Thread(target=_run, daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = LauncherApp()
    app.run()


if __name__ == "__main__":
    main()
