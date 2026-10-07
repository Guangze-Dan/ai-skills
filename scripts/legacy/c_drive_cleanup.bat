@echo off
chcp 936 >nul
echo ============================================================
echo  C盘残留收尾：把活动会话数据做最后快照到D盘，然后删除C盘目录
echo  请先确认 ZCode 已经完全关闭！按任意键继续，或直接关窗口取消。
echo ============================================================
pause

echo [1/3] 快照 .zcode 会话数据 ...
robocopy "C:\机械硬盘\Zcode\.zcode" "D:\Zcode\_C盘合并存档\.zcode_最终快照" /E /NFL /NDL /NJH /NJS /NP

echo [2/3] 快照 试验方案 残留 ...
robocopy "C:\机械硬盘\Zcode\试验方案" "D:\Zcode\_C盘合并存档\试验方案_最终快照" /E /NFL /NDL /NJH /NJS /NP

echo [3/3] 删除 C 盘目录 ...
rd /s /q "C:\机械硬盘\Zcode"
rd /s /q "C:\机械硬盘"

if exist "C:\机械硬盘" (echo 删除未完成，请检查是否有程序占用) else (echo 已完成：C:\机械硬盘 已删除)
echo 结束后可删除本批处理文件。
pause
