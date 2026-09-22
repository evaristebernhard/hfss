# HFSS 当前模型与仿真结果交付包

日期：2026-09-22

## 建议查看顺序

1. 先阅读 `report/hfss_current_status_report_20260922.pdf`。
2. 在 Ansys Electronics Desktop 中打开 `model/single_magictee_v4_full.aedt`。
3. 原始 S4P、参数扫描、分析 JSON 位于 `simulation/`。

## 当前主模型

这是 v4 单 Magic-T 三维全架构模型，包含局部柱对、H 面喉部、双脊渐变段和三个收回状态的调谐螺钉。它是研究设计阶段模型，不是已完成的四路整机，也不是硬件资格认证结果。

## 仿真结论

- v4 局部方向识别已完成，随后新增 v5 结区匹配柱、局部柱对联合筛选和 E 臂短阶梯筛选；启发式方向门槛仍未通过。
- v4 中心点端口功率审计显示同相 H 臂合成效率为 47.16%-59.55%，未达到 >90% 门槛；30 kW/1 kW 数值已按 S4P 线性换算。
- 本轮最佳 H 面候选为贯穿匹配柱半径 2.4 mm、从底壁起高度 16.25 mm，并保留局部柱对：H 面效率 59.34%-88.40%，平均 77.26%；30 kW 线性端口换算约 17.80-26.52 kW。
- E 臂短阶梯筛选未能恢复差模效率，下一步需要真实隔板/窗口或复合结区匹配结构。
- v3.4 Jacobian 扫描和 v2 Stage-A 扫描均保留，便于回溯设计判断。
- 当前结果尚未覆盖四路树级联、有限导体损耗、30 kW 峰值电场或 1 kW CW 热分析。

## 打开工程

Windows 上可以直接双击 `model/single_magictee_v4_full.aedt`。如果工程关联未配置，可在 WSL 项目目录运行：

```bash
scripts/wsl_pyaedt_launcher.sh \
  scripts/open_hfss_project_gui.py \
  /path/to/model/single_magictee_v4_full.aedt
```

## 研究记录

详细的本轮研究结论见 `docs/v5_research_update_20260922.md`；v5 原始仿真结果和审计文件分别位于 `simulation/v5_post_joint_screen/`、`simulation/v5_through_post_screen/`、`simulation/v5_through_post_extend/` 和 `simulation/v5_e_step_screen/`。
