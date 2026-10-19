"""环境自检：依赖、第三方软件、字体、以及已知的坑。

默认是"只看不启"——不会启动 Origin / Visio（它们启动慢，且会话锁屏时会挂住）。
要真正试探连接，加 --connect。

    python check_env.py
    python check_env.py --connect
"""
from __future__ import annotations

import argparse
import platform
import shutil
import sys
from pathlib import Path

OK = "[ OK ]"
BAD = "[FAIL]"
WARN = "[WARN]"
INFO = "[ -- ]"

problems: list[str] = []
warnings: list[str] = []


def head(title: str) -> None:
    print(f"\n=== {title} ===")


def check_python() -> None:
    head("Python")
    v = sys.version_info
    bits = platform.architecture()[0]
    print(f"{INFO} {sys.version.split()[0]}  ({bits})  {sys.executable}")
    if v < (3, 10):
        problems.append("需要 CPython 3.10+")
        print(f"{BAD} 版本过低，需要 3.10 / 3.11 / 3.12")
        return
    if v >= (3, 13):
        print(f"{WARN} 3.13+ 未实测过，originpro / OriginExt 可能没有对应轮子")
        warnings.append("Python 版本高于实测范围（3.10-3.12）")
    if bits != "64bit":
        problems.append("需要 64 位 Python")
        print(f"{BAD} 必须 64 位")
    else:
        print(f"{OK} 版本与位数符合要求")


def pkg_version(module, pip_name: str) -> str:
    """先取模块自带 __version__，取不到就查 pip 元数据。"""
    v = getattr(module, "__version__", "")
    if v:
        return str(v)
    try:
        from importlib.metadata import version
        return version(pip_name)
    except Exception:
        return ""


def check_packages() -> None:
    head("Python 依赖")
    required = {
        "win32com": ("pywin32", "COM 桥，驱动 Visio"),
        "originpro": ("originpro", "Origin 官方封装"),
        "OriginExt": ("OriginExt", "originpro 底层扩展"),
        "ezdxf": ("ezdxf", "代码生成 dxf，替代 CAD"),
        "PIL": ("Pillow", "导出校验"),
        "numpy": ("numpy", "计算"),
    }
    optional = {"matplotlib": ("matplotlib", "纯数据图兜底路线")}

    for mod, (pip_name, desc) in required.items():
        try:
            m = __import__(mod)
            print(f"{OK} {mod:<12} {pkg_version(m, pip_name):<10} {desc}")
        except Exception as e:
            print(f"{BAD} {mod:<12} {'':<10} {desc}  -> {type(e).__name__}")
            problems.append(f"缺少依赖 {mod}（pip install -r requirements.txt）")

    for mod, (pip_name, desc) in optional.items():
        try:
            m = __import__(mod)
            print(f"{OK} {mod:<12} {pkg_version(m, pip_name):<10} {desc}")
        except Exception:
            print(f"{INFO} {mod:<12} {'':<10} {desc}（可选，未装）")


def check_software() -> None:
    head("第三方软件")
    import winreg

    def progid_registered(progid: str) -> bool:
        for root in (winreg.HKEY_CLASSES_ROOT,):
            try:
                with winreg.OpenKey(root, progid):
                    return True
            except OSError:
                pass
        return False

    for progid, desc in (
        ("Origin.ApplicationSI", "Origin / OriginPro（走 Origin 出图必需）"),
        ("Visio.Application", "Microsoft Visio 桌面版（走 Visio 示意图必需）"),
        ("AutoCAD.Application", "AutoCAD（**不需要**，ezdxf 已替代）"),
    ):
        got = progid_registered(progid)
        print(f"{OK if got else INFO} {progid:<22} {desc}")
        if not got and not desc.startswith("AutoCAD"):
            warnings.append(f"未检测到 {progid}；用到相关功能时才会需要")


def check_fonts() -> None:
    head("字体（规范要求）")
    fonts_dir = Path(r"C:\Windows\Fonts")
    for fname, desc in (("times.ttf", "Times New Roman（西文）"),
                        ("simsun.ttc", "宋体 SimSun（中文）")):
        p = fonts_dir / fname
        if p.exists():
            print(f"{OK} {fname:<12} {desc}")
        else:
            print(f"{WARN} {fname:<12} {desc} -> 未找到，成图字体会被替换")
            warnings.append(f"字体缺失：{desc}")


def check_environment() -> None:
    head("运行时环境")
    # 残留 Origin 进程会让后续自动化报"无效指针"
    try:
        import subprocess
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Name Origin64 -ErrorAction SilentlyContinue).Count"],
            capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out.isdigit() else 0
        if n:
            print(f"{WARN} 有 {n} 个 Origin64 进程残留 —— 建议先清掉，否则可能互相干扰")
            print(f"       Get-Process -Name Origin64 | Stop-Process -Force")
            warnings.append("有残留 Origin 进程")
        else:
            print(f"{OK} 无残留 Origin 进程")
    except Exception as e:
        print(f"{INFO} 进程检查跳过（{type(e).__name__}）")

    # 锁屏时 GUI 程序起不了窗口，自动化会挂在连接之后
    try:
        import subprocess
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "if (Get-Process -Name LogonUI -ErrorAction SilentlyContinue) {'locked'} else {'unlocked'}"],
            capture_output=True, text=True, timeout=30).stdout.strip()
        if "locked" in out:
            print(f"{BAD} 当前会话处于锁屏状态 —— Origin/Visio 自动化会挂死，请先解锁")
            problems.append("会话锁屏，自动化不可用")
        else:
            print(f"{OK} 会话已解锁")
    except Exception as e:
        print(f"{INFO} 锁屏检查跳过（{type(e).__name__}）")


def try_connect() -> None:
    head("试探连接（--connect）")
    print(f"{WARN} 会启动 Origin / Visio，可能耗时数十秒；会话锁屏时会挂住")
    try:
        import win32com.client as w
        v = w.DispatchEx("Visio.Application")
        print(f"{OK} Visio 版本 {v.Version}")
        v.Quit()
    except Exception as e:
        print(f"{BAD} Visio 连接失败：{type(e).__name__} {str(e)[:120]}")
        problems.append("Visio COM 连接失败")

    try:
        import originpro as op
        op.set_show(False)
        op.lt_exec("type -a $(@V)")
        print(f"{OK} Origin 连接成功")
        op.exit()
    except Exception as e:
        print(f"{BAD} Origin 连接失败：{type(e).__name__} {str(e)[:120]}")
        problems.append("Origin 连接失败（见 INSTALL.md 第四节的已知阻塞）")


def main() -> int:
    ap = argparse.ArgumentParser(description="academic-figure-style 环境自检")
    ap.add_argument("--connect", action="store_true",
                    help="实际启动并连接 Origin / Visio（慢，锁屏时会挂）")
    a = ap.parse_args()

    print("academic-figure-style 环境自检")
    check_python()
    check_packages()
    check_software()
    check_fonts()
    check_environment()
    if a.connect:
        try_connect()

    head("结论")
    if problems:
        print(f"{BAD} {len(problems)} 个问题：")
        for p in problems:
            print(f"       - {p}")
    else:
        print(f"{OK} 必需项全部通过")
    if warnings:
        print(f"{WARN} {len(warnings)} 条提醒：")
        for p in warnings:
            print(f"       - {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
