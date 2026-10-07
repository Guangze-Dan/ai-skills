# scripts — 自动化脚本存档

从各工作区收集的历史自动化脚本，按主题分类。多为 Windows PowerShell，路径可能需要按当前机器调整（脚本头部有说明）。

## android-mtp/ — 小米手机 MTP/USB 驱动与 APK 推送
修复 Windows 识别不出小米手机 MTP/ADB 的问题，并绕过 MTP 把 APK 推上手机。

| 脚本 | 用途 |
|---|---|
| `copy_apk.ps1` | 通过 Shell.Application (MTP) 把编译好的 APK 复制进手机下载目录 |
| `fix_mtp_driver.ps1` | 用 Windows 内置 `wpdmtp.inf` 给 WPD 设备装 MTP 驱动（pnputil，需管理员） |
| `reenumerate.ps1` | 强制重新枚举 VID_2717（小米）USB 设备 |
| `update_driver.ps1` | 给 ADB 接口装 Google USB 驱动（android_winusb.inf） |

典型顺序：`reenumerate.ps1` → `fix_mtp_driver.ps1` / `update_driver.ps1` → `copy_apk.ps1`。
（若装了 ADB，`adb install` 更省事；这组脚本是 MTP 场景的兜底。）

## android-ui/ — Android 屏幕 UI 解析
| 脚本 | 用途 |
|---|---|
| `parse_ui.ps1` | 解析 `uiautomator dump` 出的 XML：按 resource-id/text 提取控件与 bounds 坐标 |
| `dump481.ps1` | 从 UI dump 文本中截取指定控件 id 的子树（原始排查脚本，参数硬编码 id=481，可按需改） |

## productivity/ — 效率工具
| 脚本 | 用途 |
|---|---|
| `ui_mockup.py` | matplotlib 绘制 App UI 仿真图（深蓝配色手账/课表类界面），改坐标与文案即可复用 |
| `read_schedule.py` | 读取课表 docx（python-docx），打印段落与表格结构 |
| `start_zcode.bat` | 启动 ZCode，多路径回退（D 盘优先，找不到再找常见安装位置） |

## legacy/ — 一次性历史脚本
| 脚本 | 用途 |
|---|---|
| `check_files.py` | 遍历目录统计文件数（原用于裂缝检测项目） |
| `explore_tree.py` | 生成目录树文本（原用于 D:\Zcode 盘点） |
| `c_drive_cleanup.bat` | C 盘合并收尾清理（2026-10 已执行完毕，仅存档） |
