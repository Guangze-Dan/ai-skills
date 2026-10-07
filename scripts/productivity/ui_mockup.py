import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ===================== 配色 =====================
DEEP_BLUE = "#1B3A6B"
ACCENT_BLUE = "#5B8DEF"
ACCENT_CORAL = "#E8826B"
ACCENT_PURPLE = "#9B7FB8"
ACCENT_GREEN = "#4AAD7C"

BG_LIGHT = "#F0F2F7"
BG_CARD = "#FFFFFF"
CARD_GLASS = "#F5F7FC"

TEXT_PRIMARY = "#1A1D2E"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"
TEXT_ON_BLUE = "#FFFFFF"
TEXT_ON_BLUE_SUB = "#A8C5F0"

# ===================== 手机框（小米17Pro比例：更高）=====================
def draw_phone_frame(ax):
    """小米17Pro 比例：6.73寸 20:9，画布 411x920"""
    phone = FancyBboxPatch((0, 0), 411, 920, 
                          boxstyle="round,pad=20,rounding_size=20",
                          facecolor="#0F1012", edgecolor="#2a2a2a", linewidth=3)
    ax.add_patch(phone)
    screen = FancyBboxPatch((15, 15), 381, 890,
                           boxstyle="round,pad=5,rounding_size=5",
                           facecolor=BG_LIGHT, edgecolor="none")
    ax.add_patch(screen)
    return screen

# ===================== 毛玻璃卡片 =====================
def draw_glass_card(ax, x, y, w, h, radius=16):
    card = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=3,rounding_size={radius}",
                         facecolor=CARD_GLASS, edgecolor="#E0E4EC", linewidth=0.5)
    ax.add_patch(card)
    return card

# ===================== 课程卡片（超大间距版）=====================
def draw_course_card(ax, x, y, w, h, color, title, subtitle, location, period, slot):
    """
    y 是卡片底部 y 坐标
    卡片内部布局（从上到下，间距充足）：
      - 时段标签: y + h - 34
      - 课程名:   y + h - 68
      - 教师名:   y + h - 94
      - 地点:     y + 18
    """
    # 卡片背景（更圆角）
    card = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=3,rounding_size=18",
                         facecolor=BG_CARD, edgecolor="#E5E7EB", linewidth=0.5)
    ax.add_patch(card)
    
    # 左侧色条
    bar = FancyBboxPatch((x, y), 4, h,
                        boxstyle="round,pad=1,rounding_size=2",
                        facecolor=color, edgecolor="none")
    ax.add_patch(bar)
    
    # 时段标签（胶囊形）
    tag_y = y + h - 34
    tag = FancyBboxPatch((x+16, tag_y), 52, 22,
                        boxstyle="round,pad=2,rounding_size=8",
                        facecolor=color + "18", edgecolor="none")
    ax.add_patch(tag)
    ax.text(x+42, tag_y+11, period, fontsize=8, fontweight='bold', color=color, ha='center', va='center')
    
    # 节次（时段标签右边）
    ax.text(x+80, tag_y+11, slot, fontsize=9, color=TEXT_TERTIARY, va='center')
    
    # 课程名（大号，与标签间隔22px）
    ax.text(x+16, y + h - 64, title, fontsize=14, fontweight='semibold', color=TEXT_PRIMARY)
    
    # 教师名（在课程名下方，与地点错开）
    ax.text(x+16, y + 24, subtitle, fontsize=11, color=TEXT_SECONDARY)
    
    # 地点（紧贴卡片底部，与教师名间隔足够）
    ax.text(x+16, y + 6, location, fontsize=10, color=TEXT_TERTIARY)

# ===================== 1. 课表主页 =====================
def draw_schedule_screen():
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 10.5))
    ax.set_xlim(0, 411)
    ax.set_ylim(0, 920)
    ax.axis('off')
    
    draw_phone_frame(ax)
    
    # === 顶部蓝色区域（缩小，文字上下居中）===
    header = patches.Rectangle((15, 800), 381, 70, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(header)
    
    # 标题（垂直居中于蓝框）
    ax.text(45, 850, "我的课表", fontsize=22, fontweight='bold', color=TEXT_ON_BLUE, va='center')
    ax.text(45, 822, "2026年 秋季学期", fontsize=10, color=TEXT_ON_BLUE_SUB, va='center')
    
    # 周次切换（右侧，与标题同线居中）
    pill = FancyBboxPatch((280, 820), 105, 30,
                         boxstyle="round,pad=3,rounding_size=15",
                         facecolor="#FFFFFF20", edgecolor="none")
    ax.add_patch(pill)
    ax.text(332, 835, "第2周", fontsize=12, fontweight='semibold', color=TEXT_ON_BLUE, ha='center', va='center')
    
    # === 时间信息卡片（与蓝框保持间距）===
    time_y = 690
    time_h = 90
    time_bg = FancyBboxPatch((35, time_y), 341, time_h,
                            boxstyle="round,pad=3,rounding_size=24",
                            facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(time_bg)
    
    # 左侧：日期+星期（上下分开，间距充足）
    ax.text(55, time_y+62, "9月8日", fontsize=12, color=TEXT_ON_BLUE_SUB)
    ax.text(55, time_y+28, "周二", fontsize=26, fontweight='bold', color=TEXT_ON_BLUE)
    
    # 中间分隔线
    ax.plot([220, 220], [time_y+18, time_y+72], color="#FFFFFF25", linewidth=1)
    
    # 右侧：时间
    ax.text(245, time_y+52, "08:00", fontsize=34, fontweight='bold', color=TEXT_ON_BLUE, ha='left')
    ax.text(245, time_y+24, "上午", fontsize=13, color=TEXT_ON_BLUE_SUB)
    
    # === 本周统计（与时间卡片拉开间距）===
    ax.text(45, 646, "本周课程", fontsize=14, fontweight='semibold', color=TEXT_PRIMARY)
    count_bg = FancyBboxPatch((320, 636), 60, 22,
                             boxstyle="round,pad=2,rounding_size=11",
                             facecolor="#E8ECF4", edgecolor="none")
    ax.add_patch(count_bg)
    ax.text(350, 647, "共 4 节", fontsize=9, color=TEXT_SECONDARY, ha='center', va='center', fontweight='medium')
    
    # === 周二（今天）===
    y = 606
    dot = plt.Circle((48, y+5), 4, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(dot)
    ax.text(62, y+5, "周二", fontsize=15, fontweight='bold', color=DEEP_BLUE, va='center')
    
    # 今天标签（与周二间隔足够）
    today_tag = FancyBboxPatch((115, y-5), 44, 20,
                              boxstyle="round,pad=2,rounding_size=10",
                              facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(today_tag)
    ax.text(137, y+5, "今天", fontsize=9, color=TEXT_ON_BLUE, ha='center', va='center', fontweight='bold')
    
    # 空状态（与标题间隔足够）
    empty_y = y - 54
    empty_bg = FancyBboxPatch((40, empty_y), 331, 40,
                             boxstyle="round,pad=3,rounding_size=14",
                             facecolor=CARD_GLASS, edgecolor="#E5E7EB", linewidth=0.5)
    ax.add_patch(empty_bg)
    ax.text(205, empty_y+20, "无课", fontsize=13, color=TEXT_TERTIARY, ha='center', va='center', alpha=0.5)
    
    # === 周一 ===
    y = 516
    dot = plt.Circle((48, y+5), 3.5, facecolor="#D1D5DB", edgecolor="none")
    ax.add_patch(dot)
    ax.text(62, y+5, "周一", fontsize=14, fontweight='medium', color=TEXT_SECONDARY, va='center')
    count = FancyBboxPatch((352, y-3), 28, 18,
                          boxstyle="round,pad=2,rounding_size=9",
                          facecolor="#E5E7EB", edgecolor="none")
    ax.add_patch(count)
    ax.text(366, y+6, "2节", fontsize=8, color=TEXT_SECONDARY, ha='center', va='center', fontweight='medium')
    
    # 课程卡片1（高度110，内部间距更大）
    card_y = y - 118
    draw_course_card(ax, 40, card_y, 331, 108, ACCENT_BLUE,
                    "能源矿产理论和勘查前沿", "沈传波", "东教楼B0506", "上午", "1-4")
    
    # 课程卡片2（与卡片1间隔12）
    card_y2 = card_y - 120
    draw_course_card(ax, 40, card_y2, 331, 108, ACCENT_CORAL,
                    "科学方法论", "赵葵东", "教三楼109", "下午", "5-8")
    
    # === 周三 ===
    y = card_y2 - 40
    dot = plt.Circle((48, y+5), 3.5, facecolor="#D1D5DB", edgecolor="none")
    ax.add_patch(dot)
    ax.text(62, y+5, "周三", fontsize=14, fontweight='medium', color=TEXT_SECONDARY, va='center')
    count = FancyBboxPatch((352, y-3), 28, 18,
                          boxstyle="round,pad=2,rounding_size=9",
                          facecolor="#E5E7EB", edgecolor="none")
    ax.add_patch(count)
    ax.text(366, y+6, "2节", fontsize=8, color=TEXT_SECONDARY, ha='center', va='center', fontweight='medium')
    
    card_y3 = y - 118
    draw_course_card(ax, 40, card_y3, 331, 108, ACCENT_BLUE,
                    "能源矿产理论和勘查前沿", "沈传波", "东教楼B0506", "上午", "1-4")
    card_y4 = card_y3 - 120
    draw_course_card(ax, 40, card_y4, 331, 108, ACCENT_CORAL,
                    "科学方法论", "赵葵东", "教三楼109", "下午", "5-8")
    
    # === 周四 ===
    y = card_y4 - 40
    dot = plt.Circle((48, y+5), 3.5, facecolor="#D1D5DB", edgecolor="none")
    ax.add_patch(dot)
    ax.text(62, y+5, "周四", fontsize=14, fontweight='medium', color=TEXT_SECONDARY, va='center')
    count = FancyBboxPatch((352, y-3), 28, 18,
                          boxstyle="round,pad=2,rounding_size=9",
                          facecolor="#E5E7EB", edgecolor="none")
    ax.add_patch(count)
    ax.text(366, y+6, "2节", fontsize=8, color=TEXT_SECONDARY, ha='center', va='center', fontweight='medium')
    
    card_y5 = y - 118
    draw_course_card(ax, 40, card_y5, 331, 108, ACCENT_GREEN,
                    "软件工程", "徐迟", "化学楼1阶", "上午", "3-4")
    card_y6 = card_y5 - 120
    draw_course_card(ax, 40, card_y6, 331, 108, ACCENT_PURPLE,
                    "中国马克思主义与当代", "李海金", "教三楼109", "下午", "5-8")
    
    # === FAB 按钮（更大间距）===
    # 导入按钮（上）
    import_shadow = plt.Circle((365, 130), 22, facecolor="#00000010", edgecolor="none")
    ax.add_patch(import_shadow)
    import_btn = plt.Circle((365, 134), 21, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(import_btn)
    ax.text(365, 134, "↓", fontsize=18, color=TEXT_ON_BLUE, ha='center', va='center', fontweight='bold')
    
    # 添加按钮（下）
    add_shadow = plt.Circle((365, 62), 25, facecolor="#00000010", edgecolor="none")
    ax.add_patch(add_shadow)
    add_btn = plt.Circle((365, 68), 24, facecolor="white", edgecolor="#E5E7EB", linewidth=1)
    ax.add_patch(add_btn)
    ax.text(365, 68, "+", fontsize=28, color=DEEP_BLUE, ha='center', va='center', fontweight='light')
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig("C:/机械硬盘/Zcode/.zcode/workspace/default/screenshot_schedule.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("1/5 课表主页 - 完成")

# ===================== 2. 添加课程页 =====================
def draw_add_course_screen():
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 10.5))
    ax.set_xlim(0, 411)
    ax.set_ylim(0, 920)
    ax.axis('off')
    
    draw_phone_frame(ax)
    
    # === 顶部（缩小，文字居中）===
    header = patches.Rectangle((15, 800), 381, 70, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(header)
    ax.text(55, 835, "<", fontsize=24, color=TEXT_ON_BLUE, fontweight='light', va='center')
    ax.text(90, 835, "添加课程", fontsize=20, fontweight='bold', color=TEXT_ON_BLUE, va='center')
    
    # === 表单标题（远离顶部蓝框） ===
    ax.text(45, 770, "填写课程信息", fontsize=14, fontweight='semibold', color=ACCENT_BLUE)
    
    form_x = 40
    field_w = 331
    field_h = 50
    gap = 85  # 每组间距 = label(20) + field(50) + padding(15)
    
    y = 680
    
    # 课程名称
    draw_field(ax, form_x, y, field_w, field_h, "课程名称", "例如：软件工程")
    y -= gap
    
    # 教师
    draw_field(ax, form_x, y, field_w, field_h, "教师", "例如：徐迟")
    y -= gap
    
    # 地点
    draw_field(ax, form_x, y, field_w, field_h, "上课地点", "例如：化学楼1阶")
    y -= gap
    
    # 星期
    draw_dropdown(ax, form_x, y, field_w, field_h, "星期", "周一")
    y -= gap
    
    # 节次（并排，更宽）
    half_w = (field_w - 16) / 2
    draw_field(ax, form_x, y, half_w, field_h, "开始节次", "第1节")
    draw_field(ax, form_x+half_w+16, y, half_w, field_h, "结束节次", "第4节")
    y -= gap
    
    # 周次（并排）
    draw_field(ax, form_x, y, half_w, field_h, "开始周", "1")
    draw_field(ax, form_x+half_w+16, y, half_w, field_h, "结束周", "20")
    y -= gap
    
    # 周类型
    draw_dropdown(ax, form_x, y, field_w, field_h, "周类型", "全部周")
    y -= gap + 30
    
    # 保存按钮（更大）
    save_btn = FancyBboxPatch((form_x, y), field_w, 54,
                             boxstyle="round,pad=3,rounding_size=16",
                             facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(save_btn)
    ax.text(205, y+27, "添加课程", fontsize=16, fontweight='semibold', 
            color=TEXT_ON_BLUE, ha='center', va='center')
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig("C:/机械硬盘/Zcode/.zcode/workspace/default/screenshot_add_course.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("2/5 添加课程页 - 完成")

def draw_field(ax, x, y, w, h, label, placeholder):
    """绘制文本输入框，标签在上方与输入框完全分离"""
    # 标签（在输入框上方，留足间距）
    ax.text(x, y + h + 18, label, fontsize=11, color=TEXT_SECONDARY)
    # 输入框
    field = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=3,rounding_size=14",
                          facecolor="white", edgecolor="#E5E7EB", linewidth=1)
    ax.add_patch(field)
    ax.text(x+16, y+h/2, placeholder, fontsize=12, color="#C0C4CC", va='center')

def draw_dropdown(ax, x, y, w, h, label, value):
    """绘制下拉选择框"""
    ax.text(x, y + h + 18, label, fontsize=11, color=TEXT_SECONDARY)
    field = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=3,rounding_size=14",
                          facecolor="white", edgecolor="#E5E7EB", linewidth=1)
    ax.add_patch(field)
    ax.text(x+16, y+h/2, value, fontsize=12, color=TEXT_PRIMARY, va='center')
    # 下拉箭头
    tri = plt.Polygon([[x+w-24, y+h/2+5], [x+w-16, y+h/2-4], [x+w-8, y+h/2+5]], 
                      facecolor=TEXT_TERTIARY, edgecolor="none")
    ax.add_patch(tri)

# ===================== 3. 小组件预览 =====================
def draw_widget():
    fig, ax = plt.subplots(1, 1, figsize=(5, 2.8))
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 260)
    ax.axis('off')
    
    # 深蓝背景
    bg = FancyBboxPatch((10, 10), 480, 240,
                        boxstyle="round,pad=5,rounding_size=22",
                        facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(bg)
    
    # 顶部：时段 + 周次（间距充足）
    ax.text(45, 218, "上午", fontsize=17, fontweight='bold', color=TEXT_ON_BLUE)
    ax.text(460, 218, "第2周", fontsize=13, color=TEXT_ON_BLUE_SUB, ha='right')
    
    # 分隔线（与上下内容间隔）
    ax.plot([45, 460], [192, 192], color="#FFFFFF15", linewidth=0.8)
    
    # 即将上课标签
    ax.text(45, 170, "即将上课", fontsize=13, color=TEXT_ON_BLUE_SUB)
    
    # 课程名（大字）
    ax.text(45, 140, "能源矿产理论和勘查前沿", fontsize=19, fontweight='bold', color=TEXT_ON_BLUE)
    
    # 课程详情（节次和地点分开展示，间距更大）
    ax.text(45, 108, "第1-4节", fontsize=13, color=TEXT_ON_BLUE_SUB)
    ax.text(160, 108, "东教楼B0506", fontsize=13, color=TEXT_ON_BLUE_SUB)
    
    # 底部：课程数（右对齐）
    ax.text(460, 35, "今日 4 节课", fontsize=12, color=TEXT_ON_BLUE_SUB, alpha=0.5, ha='right')
    
    ax.text(250, 10, "桌面小组件预览", fontsize=9, color=TEXT_ON_BLUE_SUB, alpha=0.2, ha='center', va='bottom')
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig("C:/机械硬盘/Zcode/.zcode/workspace/default/screenshot_widget.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("3/5 小组件预览 - 完成")

# ===================== 4. 课程详情页 =====================
def draw_detail_screen():
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 10.5))
    ax.set_xlim(0, 411)
    ax.set_ylim(0, 920)
    ax.axis('off')
    
    draw_phone_frame(ax)
    
    # === 顶部（缩小，文字居中）===
    header = patches.Rectangle((15, 800), 381, 70, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(header)
    ax.text(55, 835, "<", fontsize=24, color=TEXT_ON_BLUE, fontweight='light', va='center')
    ax.text(90, 835, "课程详情", fontsize=20, fontweight='bold', color=TEXT_ON_BLUE, va='center')
    
    # 编辑/删除按钮（顶部右侧，居中）
    edit_bg = FancyBboxPatch((300, 822), 40, 24,
                            boxstyle="round,pad=2,rounding_size=10",
                            facecolor="#FFFFFF18", edgecolor="none")
    ax.add_patch(edit_bg)
    ax.text(320, 834, "编辑", fontsize=9, color=TEXT_ON_BLUE_SUB, ha='center', va='center')
    
    del_bg = FancyBboxPatch((345, 822), 40, 24,
                           boxstyle="round,pad=2,rounding_size=10",
                           facecolor="#FFFFFF18", edgecolor="none")
    ax.add_patch(del_bg)
    ax.text(365, 834, "删除", fontsize=9, color=TEXT_ON_BLUE_SUB, ha='center', va='center')
    
    # === 课程信息卡片（与蓝框保持间距）===
    card1_y = 705
    draw_glass_card(ax, 35, card1_y, 341, 85)
    
    # 标签
    ax.text(55, card1_y + 62, "课程信息", fontsize=11, fontweight='bold', color=ACCENT_BLUE)
    # 课程名
    ax.text(55, card1_y + 34, "能源矿产理论和勘查前沿", fontsize=16, fontweight='bold', color=TEXT_PRIMARY)
    # 教师 + 地点（同行分隔）
    ax.text(55, card1_y + 12, "沈传波", fontsize=12, color=TEXT_SECONDARY)
    ax.text(220, card1_y + 12, "东教楼B0506", fontsize=12, color=TEXT_SECONDARY)
    
    # === 时间信息卡片（与上方卡片保持间距）===
    card2_y = 600
    draw_glass_card(ax, 35, card2_y, 341, 95)
    
    ax.text(55, card2_y + 72, "上课时间", fontsize=11, fontweight='bold', color=ACCENT_BLUE)
    
    # 第一行：星期 + 节次
    ax.text(55, card2_y + 44, "周一", fontsize=14, color=TEXT_PRIMARY, fontweight='medium')
    ax.text(220, card2_y + 44, "第1-4节", fontsize=14, color=TEXT_PRIMARY, fontweight='medium')
    
    # 第二行：时段 + 周次
    ax.text(55, card2_y + 20, "上午 08:00-12:00", fontsize=13, color=TEXT_SECONDARY)
    ax.text(220, card2_y + 20, "第2-5周", fontsize=13, color=TEXT_SECONDARY)
    
    # === 操作按钮（更大间距）===
    edit_btn = FancyBboxPatch((35, 530), 160, 52,
                             boxstyle="round,pad=3,rounding_size=16",
                             facecolor="white", edgecolor=DEEP_BLUE, linewidth=1.2)
    ax.add_patch(edit_btn)
    ax.text(115, 556, "编辑", fontsize=14, color=DEEP_BLUE, ha='center', va='center', fontweight='semibold')
    
    del_btn = FancyBboxPatch((211, 530), 160, 52,
                            boxstyle="round,pad=3,rounding_size=16",
                            facecolor=ACCENT_CORAL, edgecolor="none")
    ax.add_patch(del_btn)
    ax.text(291, 556, "删除", fontsize=14, color=TEXT_ON_BLUE, ha='center', va='center', fontweight='semibold')
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig("C:/机械硬盘/Zcode/.zcode/workspace/default/screenshot_detail.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("4/5 课程详情页 - 完成")

# ===================== 5. 导入课程页 =====================
def draw_import_screen():
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 10.5))
    ax.set_xlim(0, 411)
    ax.set_ylim(0, 920)
    ax.axis('off')
    
    draw_phone_frame(ax)
    
    # === 顶部（缩小，文字居中）===
    header = patches.Rectangle((15, 800), 381, 70, facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(header)
    ax.text(55, 835, "<", fontsize=24, color=TEXT_ON_BLUE, fontweight='light', va='center')
    ax.text(90, 835, "导入课程", fontsize=20, fontweight='bold', color=TEXT_ON_BLUE, va='center')
    
    # === 说明卡片（更大）===
    info_y = 690
    info_bg = FancyBboxPatch((35, info_y), 341, 90,
                            boxstyle="round,pad=3,rounding_size=18",
                            facecolor=BG_CARD, edgecolor="#E5E7EB", linewidth=0.5)
    ax.add_patch(info_bg)
    
    ax.text(55, info_y+68, "如何导入", fontsize=13, fontweight='bold', color=DEEP_BLUE)
    ax.text(55, info_y+44, "1. 打开学校教务系统/课程表页面", fontsize=11, color=TEXT_SECONDARY)
    ax.text(55, info_y+24, "2. 全选并复制课程表内容，粘贴到下方", fontsize=11, color=TEXT_SECONDARY)
    
    # === 粘贴区域（更大）===
    paste_y = 460
    paste_bg = FancyBboxPatch((35, paste_y), 341, 220,
                             boxstyle="round,pad=3,rounding_size=18",
                             facecolor=BG_CARD, edgecolor="#E5E7EB", linewidth=0.5)
    ax.add_patch(paste_bg)
    
    ax.text(55, paste_y+196, "粘贴课表内容", fontsize=13, fontweight='semibold', color=TEXT_PRIMARY)
    
    # 输入框
    input_bg = FancyBboxPatch((55, paste_y+18), 301, 160,
                             boxstyle="round,pad=3,rounding_size=12",
                             facecolor="white", edgecolor="#E5E7EB", linewidth=1)
    ax.add_patch(input_bg)
    ax.text(67, paste_y+150, "在此粘贴你的课程表内容...", fontsize=12, color="#C0C4CC")
    
    # === 导入按钮（更大）===
    btn_y = 400
    import_btn = FancyBboxPatch((35, btn_y), 341, 52,
                               boxstyle="round,pad=3,rounding_size=16",
                               facecolor=DEEP_BLUE, edgecolor="none")
    ax.add_patch(import_btn)
    ax.text(205, btn_y+26, "解析并导入", fontsize=15, fontweight='semibold', color=TEXT_ON_BLUE, ha='center', va='center')
    
    # === 已有课程（与按钮间隔足够）===
    count_y = btn_y - 60
    count_bg = FancyBboxPatch((35, count_y), 341, 44,
                             boxstyle="round,pad=3,rounding_size=14",
                             facecolor=BG_CARD, edgecolor="#E5E7EB", linewidth=0.5)
    ax.add_patch(count_bg)
    ax.text(55, count_y+22, "当前已有课程", fontsize=12, color=TEXT_SECONDARY, va='center')
    ax.text(355, count_y+22, "0 门", fontsize=12, fontweight='bold', color=DEEP_BLUE, ha='right', va='center')
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig("C:/机械硬盘/Zcode/.zcode/workspace/default/screenshot_import.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("5/5 导入课程页 - 完成")

# ===================== 运行 =====================
if __name__ == "__main__":
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC']
    plt.rcParams['axes.unicode_minus'] = False
    
    print("🎨 正在生成小米17Pro适配UI预览图...")
    draw_schedule_screen()
    draw_add_course_screen()
    draw_widget()
    draw_detail_screen()
    draw_import_screen()
    print("")
    print("✅ 全部完成！")