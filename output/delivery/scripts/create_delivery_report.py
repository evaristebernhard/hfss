#!/usr/bin/env python3
"""Create a compact Chinese delivery report for the current HFSS work."""

from __future__ import annotations

import math
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "hfss" / "results"
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUT / "hfss_current_status_report_20260922.pdf"
V4_S4P = RESULTS / "v4_local_identification" / "center.s4p"
V5_HBEST = RESULTS / "v5_post_joint_screen" / "r2p4_h16p25_pair_on" / "audit.json"
V5_EPAS = RESULTS / "v5_e_step_screen" / "e_b8p0_l3p0" / "audit.json"


def register_font() -> str:
    for candidate in (
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ):
        if Path(candidate).exists():
            pdfmetrics.registerFont(TTFont("ReportCN", candidate))
            return "ReportCN"
    raise RuntimeError("未找到可显示中文的字体")


def read_s4p(path: Path):
    tokens = []
    for raw in path.read_text(encoding="ascii", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("!") and not line.startswith("#"):
            tokens.extend(line.split())
    if len(tokens) % 33:
        raise ValueError(f"S4P 字段数异常: {path}")
    freqs, matrices = [], []
    for k in range(0, len(tokens), 33):
        freqs.append(float(tokens[k]))
        values = [float(x) for x in tokens[k + 1:k + 33]]
        matrix = []
        for i in range(0, 32, 2):
            mag, deg = values[i], values[i + 1]
            angle = math.radians(deg)
            matrix.append(mag * complex(math.cos(angle), math.sin(angle)))
        matrices.append(matrix)
    return freqs, matrices


def db(value: complex) -> float:
    return 20 * math.log10(max(abs(value), 1e-12))


def make_sparam_drawing(font: str) -> Drawing:
    freqs, matrices = read_s4p(V4_S4P)
    traces = {"S11": 0, "S21": 4, "S31": 8, "S41": 12}
    line_colors = [
        colors.HexColor("#0F766E"),
        colors.HexColor("#2563EB"),
        colors.HexColor("#D97706"),
        colors.HexColor("#DC2626"),
    ]
    drawing = Drawing(175 * mm, 82 * mm)
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = 42, 30, 425, 185
    plot.data = [
        [(freqs[k], db(matrices[k][index])) for k in range(len(freqs))]
        for index in traces.values()
    ]
    plot.xValueAxis.valueMin, plot.xValueAxis.valueMax = min(freqs), max(freqs)
    plot.xValueAxis.valueStep = 0.5
    plot.yValueAxis.valueMin, plot.yValueAxis.valueMax = -60, 0
    plot.yValueAxis.valueStep = 10
    for axis in (plot.xValueAxis, plot.yValueAxis):
        axis.labels.fontName = font
        axis.labels.fontSize = 7
    for i, color in enumerate(line_colors):
        plot.lines[i].strokeColor = color
        plot.lines[i].strokeWidth = 1.3
    drawing.add(plot)
    legend = Legend()
    legend.x, legend.y = 70, 226
    legend.dx, legend.dy = 9, 7
    legend.fontName, legend.fontSize = font, 8
    legend.colorNamePairs = list(zip(line_colors, traces.keys()))
    drawing.add(legend)
    drawing.add(String(42, 233, "v4 中心点原始端口 S 参数", fontName=font, fontSize=9, fillColor=colors.HexColor("#334155")))
    drawing.add(String(220, 16, "频率 (GHz)", fontName=font, fontSize=8, fillColor=colors.HexColor("#334155")))
    drawing.add(String(10, 115, "幅度 (dB)", fontName=font, fontSize=8, fillColor=colors.HexColor("#334155")))
    return drawing


def make_table(rows, widths, font: str, small=False, header=True) -> Table:
    style_name = "TableSmall" if small else "Table"
    converted = [
        [cell if isinstance(cell, Paragraph) else Paragraph(str(cell), styles[style_name]) for cell in row]
        for row in rows
    ]
    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0)
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
    for r in range(1 if header else 0, len(converted)):
        if r % 2 == (1 if header else 0):
            commands.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F8FAFC")))
    table.setStyle(TableStyle(commands))
    return table


def footer(canvas, doc, font: str):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont(font, 7.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, 9 * mm, "HFSS 当前模型与仿真结果交付报告")
    canvas.drawRightString(192 * mm, 9 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


font_cn = register_font()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName=font_cn, fontSize=25, leading=32, alignment=TA_CENTER, textColor=colors.HexColor("#0F3D3E"), spaceAfter=10))
styles.add(ParagraphStyle(name="CoverSub", fontName=font_cn, fontSize=12, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=8))
styles.add(ParagraphStyle(name="H1CN", fontName=font_cn, fontSize=16, leading=22, textColor=colors.HexColor("#0F766E"), spaceBefore=6, spaceAfter=8))
styles.add(ParagraphStyle(name="H2CN", fontName=font_cn, fontSize=11.5, leading=16, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCN", fontName=font_cn, fontSize=9.5, leading=15, textColor=colors.HexColor("#1E293B"), spaceAfter=6))
styles.add(ParagraphStyle(name="SmallCN", fontName=font_cn, fontSize=8, leading=12, textColor=colors.HexColor("#475569"), spaceAfter=4))
styles.add(ParagraphStyle(name="Table", fontName=font_cn, fontSize=8.3, leading=11, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="TableSmall", fontName=font_cn, fontSize=7.2, leading=9.5, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="Callout", fontName=font_cn, fontSize=10, leading=15, textColor=colors.HexColor("#7C2D12"), backColor=colors.HexColor("#FFF7ED"), borderColor=colors.HexColor("#FDBA74"), borderWidth=0.6, borderPadding=7, spaceBefore=5, spaceAfter=8))

v4_analysis = json.loads((RESULTS / "v4_local_identification" / "local_control_analysis.json").read_text())
r11_analysis = json.loads((RESULTS / "v3_4_jacobian_r11" / "jacobian_analysis.json").read_text())
v2_summary = json.loads((RESULTS / "v2_stage_a" / "summary.json").read_text())
power_audit = json.loads((RESULTS / "v4_local_identification" / "efficiency_power_audit.json").read_text())
v5_hbest = json.loads(V5_HBEST.read_text())
v5_epas = json.loads(V5_EPAS.read_text())
v2_h = [item["H_rl_min_dB"] for item in v2_summary]
v2_e = [item["E_rl_min_dB"] for item in v2_summary]

doc = SimpleDocTemplate(
    str(PDF_PATH), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
    topMargin=16 * mm, bottomMargin=19 * mm,
    title="HFSS 当前模型与仿真结果交付报告", author="OpenAI Codex",
)
story = []

story += [
    Spacer(1, 28 * mm),
    Paragraph("HFSS 当前模型与仿真结果<br/>交付报告", styles["CoverTitle"]),
    Paragraph("X 波段四路高功率 Magic-T 合成器<br/>当前阶段：v4 单胞全架构 + 局部方向识别", styles["CoverSub"]),
    Spacer(1, 12 * mm),
]
story.append(make_table([
    ["项目", "9.0-11.5 GHz 四路波导功率合成器"],
    ["当前主模型", "single_magictee_v4_full.aedt"],
    ["HFSS 环境", "Ansys Electronics Desktop 2025.2 Student（当前可打开）"],
    ["报告日期", "2026-09-22"],
    ["交付判断", "架构与诊断资料齐全；尚未达到最终指标"],
], [34 * mm, 125 * mm], font_cn, header=False))
story += [
    Spacer(1, 15 * mm),
    Paragraph("本报告用于对外展示当前工作状态。PDF 中的曲线来自已保存的 S4P 文件；原始 S4P、AEDT 工程、参数扫描和分析 JSON 均放在同名压缩包中。", styles["SmallCN"]),
    PageBreak(),
]

story += [
    Paragraph("1. 当前结论", styles["H1CN"]),
    Paragraph("当前交付版本是一个可在 AEDT 中打开和继续修改的 v4 单 Magic-T 三维全架构模型，不是已经完成的四路整机，也不是硬件定型版本。模型包含 H 臂局部匹配柱对、H 面缩窄喉部、双脊渐变段和三个处于收回状态的调谐螺钉。", styles["BodyCN"]),
    Paragraph(
        "关键判断：当前 v4 局部方向识别未通过方向门槛。启发式增广奇异值分析得到最小奇异值增益约 "
        f"{v4_analysis['heuristic_sigma_min_gain_over_r11']:.2f} 倍，低于预设的 5 倍；最小/最大奇异值比约 "
        f"{v4_analysis['heuristic_sigma_min_over_sigma_max']:.5f}，也低于优选的 0.01。因此下一步应重新识别完整 v4 Jacobian，再进行受约束被动综合，不宜直接宣称已经满足 22 dB 回波损耗目标。",
        styles["Callout"],
    ),
    Paragraph("目标与当前状态", styles["H2CN"]),
    make_table([
        ["指标", "设计目标", "当前判断"],
        ["频带", "9.0-11.5 GHz", "已按该频带进行 101 点数据处理"],
        ["回波损耗", ">= 22 dB", "当前单胞结果约 1-6 dB 量级，未达到"],
        ["隔离度", ">= 22 dB", "部分禁止耦合低于 -30 dB，但不能替代整机隔离"],
        ["合成效率", ">90%（当前展示门槛）", "v4 单胞 H 臂端口效率 47.2%-59.5%，未通过；四路树仍待验证"],
        ["功率", ">30 kW 峰值；>1 kW CW", "已完成端口功率线性换算；峰值电场、损耗、热仍未验证"],
    ], [34 * mm, 42 * mm, 83 * mm], font_cn),
    Paragraph("结果解释边界", styles["H2CN"]),
    Paragraph("现有 S4P 主要用于单胞结构诊断、方向识别和参数敏感性判断。它们不能直接代表四路树装配后的系统性能，也不能作为高功率安全裕量或硬件资格结论。", styles["BodyCN"]),
    PageBreak(),
]

story += [
    Paragraph("2. 当前 v4 模型与参数", styles["H1CN"]),
    Paragraph("当前 AEDT 工程文件已从 /tmp/hfss-v4-center/single_magictee_v4_full.aedt 复制到交付包的 model/ 目录；同时保留 aedtresults 缓存，便于在同一环境中打开工程。", styles["BodyCN"]),
    make_table([
        ["区域", "当前种子"],
        ["基本波导", "WR90：a = 22.86 mm，b = 10.16 mm"],
        ["局部柱对 J0", "半径 1.50 mm；高度 0.70 mm；轴向位置 y = 2.00 mm"],
        ["H 面喉部 J1", "缩窄 broad dimension = 20.40 mm；长度 = 5.50 mm"],
        ["终端双脊 J2", "脊宽 = 4.572 mm；间隙 = 5.80 mm；长度 = 7.50 mm"],
        ["平滑渐变 J3", "g1 = 7.672 mm，L1 = 9.872 mm；g2 = 5.800 mm，L2 = 8.857 mm"],
        ["三螺钉 J4", "相对轴向位置 0 / 8.4 / 17.6 mm；当前穿入量 0 / 0 / 0 mm"],
        ["E 臂", "保留 v2 parity-corrected 方向；完整树级联仍待综合"],
    ], [38 * mm, 121 * mm], font_cn),
    Paragraph("模型展示建议", styles["H2CN"]),
    Paragraph("打开 AEDT 后，在左侧选择 SingleMagicT_v4_Full，使用 Modeler -> Fit All 使结构完整居中。建议先展示整体拓扑，再展开 H 臂局部区域，最后说明三个螺钉目前均为收回状态。", styles["BodyCN"]),
    PageBreak(),
]

story += [
    Paragraph("3. 仿真结果汇总", styles["H1CN"]),
    Paragraph("所有结果均来自压缩包 simulation/ 目录中的原始文件。下面的曲线是 v4 局部识别中心点 center.s4p 的原始端口网络幅度，未进行混合模变换。", styles["BodyCN"]),
    make_sparam_drawing(font_cn),
    Spacer(1, 3 * mm),
    make_table([
        ["分析项", "结果", "判定"],
        ["v4 局部识别案例", "主方向识别 5 个 S4P；另保留 radius +/- 2 个补充案例", "已完成"],
        ["v4 最小奇异值增益", f"{v4_analysis['heuristic_sigma_min_gain_over_r11']:.2f} 倍", "低于 5 倍门槛"],
        ["v4 sigma_min/sigma_max", f"{v4_analysis['heuristic_sigma_min_over_sigma_max']:.5f}", "低于 0.01 优选值"],
        ["v4 中心点 c+ 回波损耗", f"{v4_analysis['center_metrics']['c_plus_worst_return_loss_dB']:.2f} dB @ {v4_analysis['center_metrics']['c_plus_worst_return_loss_freq_GHz']:.2f} GHz", "远低于 22 dB"],
        ["v4 中心点禁止耦合", f"{v4_analysis['center_metrics']['worst_forbidden_coupling_dB']:.2f} dB", "局部耦合较低，但非整机隔离"],
    ], [43 * mm, 68 * mm, 48 * mm], font_cn, small=True),
    Spacer(1, 4 * mm),
    Paragraph("图 1. v4 中心点原始端口 S 参数幅度。曲线用于结构诊断，不能直接等同于最终四路合成效率。", styles["SmallCN"]),
    Paragraph("4. 效率与功率端口审计", styles["H1CN"]),
    Paragraph("审计采用 v4 中心点 S4P，对 P1/P2 施加等幅同相入射，P3 作为 H 臂目标输出，P4 作为 E 臂泄漏端口。归一化总入射功率为 2 W，因此结果可线性缩放到 30 kW 或 1 kW。", styles["BodyCN"]),
    make_table([
        ["项目", "9.0-11.5 GHz 结果", "判定"],
        ["H 臂同相合成效率", f"{power_audit['metrics']['sum_eta_H']['min'] * 100:.2f}%-{power_audit['metrics']['sum_eta_H']['max'] * 100:.2f}%；平均 {power_audit['metrics']['sum_eta_H']['mean'] * 100:.2f}%", "未达到 >90%"],
        ["E 臂泄漏", f"最大 {power_audit['metrics']['sum_eta_E_leak']['max'] * 100:.4f}%", "隔离方向较好"],
        ["输入反射功率占比", f"{power_audit['metrics']['sum_eta_reflection']['min'] * 100:.2f}%-{power_audit['metrics']['sum_eta_reflection']['max'] * 100:.2f}%", "匹配不足"],
        ["30 kW 输入时 H 臂输出", f"{power_audit['power_scaling']['30000W']['H_output_min_W'] / 1000:.2f}-{power_audit['power_scaling']['30000W']['H_output_max_W'] / 1000:.2f} kW", "不是 30 kW 有效输出"],
        ["1 kW 输入时 H 臂输出", f"{power_audit['power_scaling']['1000W']['H_output_min_W']:.1f}-{power_audit['power_scaling']['1000W']['H_output_max_W']:.1f} W", "线性端口换算"],
    ], [43 * mm, 68 * mm, 48 * mm], font_cn, small=True),
    Paragraph("这一步验证了端口功率守恒和线性功率分配，但没有验证 30 kW 下的峰值电场、导体损耗、真空击穿或 1 kW CW 热稳定性；原始审计 JSON/CSV 已一并放入 simulation/v4_local_identification/。", styles["Callout"]),
    PageBreak(),
]

story += [
    Paragraph("5. 本轮研究推进结果", styles["H1CN"]),
    Paragraph("针对原 v4 的 H 面效率过低问题，本轮新增了经典结区贯穿匹配柱、上下对称结区柱对和 E 臂短阶梯三类全波筛选。最有效的 H 面候选为：贯穿柱半径 2.4 mm、从底壁起高度 16.25 mm，并保留原局部柱对。它把 H 面效率范围从基线 47.2%-59.5%提高到 59.3%-88.4%，但仍未形成 >90% 的全带宽结果。", styles["BodyCN"]),
    make_table([
        ["结构候选", "H 面效率", "E 面效率", "结论"],
        ["v4 基线中心点", "47.2%-59.5%", "71.2%-86.8%", "基线"],
        ["贯穿柱 r=2.4, h=15.0 mm", "54.2%-85.0%", "48.0%-57.2%", "改善 H，但为单峰"],
        ["贯穿柱 r=2.4, h=16.25 mm + 局部柱对", f"{v5_hbest['metrics']['sum_eta_H']['min']*100:.1f}%-{v5_hbest['metrics']['sum_eta_H']['max']*100:.1f}%", f"{v5_hbest['metrics']['diff_eta_E']['min']*100:.1f}%-{v5_hbest['metrics']['diff_eta_E']['max']*100:.1f}%", "当前最佳 H 候选"],
        ["E 臂短阶梯 b=8.0, L=3.0 mm", f"{v5_epas['metrics']['sum_eta_H']['min']*100:.1f}%-{v5_epas['metrics']['sum_eta_H']['max']*100:.1f}%", f"35.1%-38.0%", "排除简单阶梯"],
    ], [58 * mm, 37 * mm, 37 * mm, 33 * mm], font_cn, small=True),
    Paragraph("最佳 H 候选在 30 kW 线性端口换算下约输出 17.80-26.52 kW；这只是 S 参数功率分配，不是峰值功率资格。E 臂短阶梯筛选表明，当前缺的不是普通窄截面变换，而是局部差模耦合的隔板、窗口或多级结区匹配结构。", styles["Callout"]),
    Paragraph("6. 历史基线与敏感性扫描", styles["H1CN"]),
    Paragraph("v3.4 的一阶 Jacobian 扫描用于说明旧坐标系统的实际秩亏问题；v2 Stage-A 扫描用于说明单纯调整终端脊间隙/长度不能解决当前宽带匹配问题。", styles["BodyCN"]),
    make_table([
        ["项目", "数值"],
        ["v3.4 Jacobian 案例", "中心点 + 8 个单参数扰动，共 9 个 S4P"],
        ["step-normalized sigma_min", f"{r11_analysis['step_normalized_svd']['singular_values'][-1]:.6f}"],
        ["step-normalized sigma_max", f"{r11_analysis['step_normalized_svd']['singular_values'][0]:.6f}"],
        ["条件数", f"{r11_analysis['step_normalized_svd']['condition_number']:.1f}"],
        ["有效秩（5% / 1%）", f"{r11_analysis['raw_svd']['effective_rank_5pct']} / {r11_analysis['raw_svd']['effective_rank_1pct']}"],
    ], [65 * mm, 94 * mm], font_cn),
    Paragraph("v2 Stage-A 12 点扫描区间", styles["H2CN"]),
    make_table([
        ["扫描量", "范围内最小值", "范围内最大值"],
        ["H 模式回波损耗", f"{min(v2_h):.2f} dB", f"{max(v2_h):.2f} dB"],
        ["E 模式回波损耗", f"{min(v2_e):.2f} dB", f"{max(v2_e):.2f} dB"],
        ["参数组合", "g2 = 4.6 / 5.0 / 5.4 / 5.8 mm；终端长度 = 4.5 / 6.0 / 7.5 mm", "共 12 组"],
    ], [55 * mm, 55 * mm, 49 * mm], font_cn, small=True),
    Paragraph("现阶段的技术含义", styles["H2CN"]),
    Paragraph("已有结果支持“先修正局部控制方向，再进行被动综合”的路线。当前最重要的下一步不是扩大螺钉扫描，而是基于 v4 五个全波案例重新计算统一定义的 v4 Jacobian；只有当新增局部柱方向确实改善弱方向后，才进入受约束的几何优化和残余螺钉调谐。", styles["BodyCN"]),
    PageBreak(),
]

story += [
    Paragraph("7. 压缩包内容与下一步", styles["H1CN"]),
    Paragraph("压缩包按“报告 - 模型 - 原始仿真 - 设计资料 - 脚本”分层，接收方可先看 PDF，再用 AEDT 打开 model/ 下的工程，最后回溯 simulation/ 下的原始 S4P。", styles["BodyCN"]),
    make_table([
        ["目录", "内容"],
        ["report/", "本 PDF 报告"],
        ["model/", "当前 v4 AEDT 工程及 aedtresults 缓存"],
        ["simulation/v4_local_identification/", "v4 中心点、post height/y 四个扰动案例、S4P、manifest、分析 JSON"],
        ["simulation/v5_post_joint_screen/", "贯穿匹配柱高度/半径与局部柱对联合筛选；包含原始 S4P 与效率功率审计"],
        ["simulation/v5_through_post_screen/ 与 v5_through_post_extend/", "贯穿匹配柱高度方向筛选"],
        ["simulation/v5_e_step_screen/", "E 臂短阶梯筛选；用于排除简单窄截面变换"],
        ["simulation/v3_4_jacobian_r11/", "v3.4 Jacobian 9 案例及分析 JSON"],
        ["simulation/v2_stage_a/", "v2 12 点参数扫描及 summary.json"],
        ["simulation/parameter_checks/", "早期单参数 S4P 检查"],
        ["design/ 与 docs/", "v4 种子、架构说明和工程设计背景"],
        ["scripts/", "v4 构建器、分析脚本和本报告生成脚本"],
    ], [58 * mm, 101 * mm], font_cn, small=True),
    Paragraph("建议的后续工作顺序", styles["H2CN"]),
    Paragraph("1）重新计算完整 v4 Jacobian；2）若方向门槛通过，进行小信赖域被动综合；3）被动回波损耗达到约 18 dB 后再启用三个螺钉；4）把单胞复制为三 Magic-T 二叉树；5）最后进行有限导体、峰值电场、30 kW 峰值和 1 kW CW 热分析。", styles["BodyCN"]),
    Paragraph("交付声明：本包完整保存了截至 2026-09-22 的当前模型与仿真证据，但结果仍处于研究设计阶段，不能作为已通过指标或硬件安全认证的依据。", styles["Callout"]),
]

doc.build(
    story,
    onFirstPage=lambda canvas, doc: footer(canvas, doc, font_cn),
    onLaterPages=lambda canvas, doc: footer(canvas, doc, font_cn),
)
print(PDF_PATH)
