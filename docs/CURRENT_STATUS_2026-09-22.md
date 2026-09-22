# HFSS 项目当前状态（2026-09-22）

> 本文只回答“现在做到哪一步、真实结果是多少、离目标还有多远、下一步做什么”。  
> 不把理论目标、计划参数或理想隔离度当成已经实现的仿真结果。

## 1. 当前基线

当前仓库：`evaristebernhard/hfss`  
当前主分支：`main`  
审计基线提交：`040de8b4351d7479da2797431e7fee78db2b0de7`

项目目标仍为：

- 频带：9.0–11.5 GHz
- 驱动端回波损耗：≥ 22 dB
- 输入端隔离度：≥ 22 dB
- 四路相干合成效率：≥ 95%
- 实物峰值输出功率：> 30 kW
- 连续平均功率：> 1 kW
- 结构尽量紧凑
- 总体结构采用三级 Magic-T 构成 4→1 二叉合成树，并使用阻抗变换 / 渐变脊波导 / 残余螺钉调谐

当前真正的工作阶段不是整机验收，而是：

**先把单个 Magic-T 单元的宽带无源匹配闭合，再进入螺钉残余调谐和四合一系统闭合。**

---

## 2. 当前已经冻结的架构

当前 v4 架构已基本冻结，不再建议频繁改变总拓扑。

单个 Magic-T 的 H / sum 路径为：

```text
Magic-T junction
  -> junction-local 对称局部匹配结构
  -> mild H-plane throat
  -> terminal double ridge
  -> smooth double-ridge transformer
  -> three-screw residual tuner
  -> WR90
```

E / difference 路径仍采用修正后的奇偶模方向，并保留 stepped septum + 短高度变换结构。

完整系统计划采用：

```text
IN1 ─┐
     ├─ MT-A ─┐
IN2 ─┘        │
              ├─ MT-C ─ OUT
IN3 ─┐        │
     ├─ MT-B ─┘
IN4 ─┘
```

三个 Magic-T 的 difference 端最终需要接匹配高功率负载。

对应文档：

- [v4 full architecture](v4_full_architecture.md)
- [v4 mathematical synthesis](v4_mathematical_synthesis.md)
- [v4 machine-readable seed](../design/seed_v4_full_architecture.json)

---

## 3. 当前最新真实 HFSS 结果

当前最新可信结果来自：

- `hfss/results/v4_local_identification/`
- AEDT Student 2025.2SV
- PEC 金属壁
- 9.0–11.5 GHz
- 101 个频点
- 三个调谐螺钉全部收回，未参与调谐

当前中心结构主要参数：

- 对称 partial-height post pair
  - 半径：1.5 mm
  - 高度：0.7 mm
  - 距 H-plane junction mouth：2.0 mm
- H throat：20.4 mm × 5.5 mm
- terminal ridge：w / g / L = 4.572 / 5.8 / 7.5 mm

注意：早期数学文档里出现过 1.5 mm 的 post 位置，但实际五组仿真已经改为 **2.0 mm**，因为 1.5 mm 向负方向扰动时会和 junction volume 相交。当前实际结果应以 `v4_local_identification` 为准。

### 最新中心点指标

先区分两种口径：

- **客户直接对应的物理端口指标**：P1/P2 的回波与相互隔离；
- **用于诊断的模态指标**：c+ / c− 的 modal return loss 与 forbidden parity leakage。

从最新 center.s4p 直接得到物理共线输入端：

| 频率 | 物理端口回波损耗 | P1-P2 输入隔离 |
|---|---:|---:|
| 9.0 GHz | 13.17 dB | 5.49 dB |
| 10.25 GHz | 16.61 dB | 4.85 dB |
| 11.5 GHz | 24.21 dB | 4.58 dB |

因此和客户“回波 / 隔离 ≥ 22 dB”直接比较时，当前应写成：**最差物理端口回波约 13.17 dB，最差输入隔离约 4.58 dB**。

下面的 c+ / c− 数值是奇偶模诊断量，不应直接当作客户物理端口指标。

| 指标 | 当前结果 | 目标 / 含义 |
|---|---:|---:|
| c+ 最差回波损耗 | **2.770 dB @ 9.0 GHz** | 目标 ≥ 22 dB |
| c− 最差回波损耗 | **5.406 dB @ 11.5 GHz** | 目标 ≥ 22 dB |
| c+ → H 最小耦合 | **−3.265 dB** | 当前仍有很大匹配损失 |
| c− → E 最小耦合 | **−1.475 dB** | 尚未闭合 |
| forbidden parity coupling | **−45.11 dB** | 奇偶模对称性很好 |

最重要的一点：

**−45.11 dB 是 forbidden parity leakage，不是“整机输入端隔离度 45.11 dB”。**

它说明当前几何的对称性隔离很好，但并不能证明客户要求的“四路输入端隔离度 ≥ 22 dB”已经完成。真正的输入端隔离必须在完整三 Magic-T 四合一网络中检查。

---

## 4. 与 R11 / v3.4 相比，是否真的进步

R11 / v3.4 中心点：

- c+ 最差回波：2.663 dB
- c− 最差回波：5.431 dB
- forbidden parity coupling：−48.728 dB
- H 路最小传输幅度：0.677

v4 中心点：

- c+ 最差回波：2.770 dB
- c− 最差回波：5.406 dB
- forbidden parity coupling：−45.11 dB
- H 路最小传输幅度：0.687

所以当前 v4 并没有把宽带匹配问题真正解决。

c+ 最差回波只从 2.663 dB 提高到 2.770 dB，改善约 **0.11 dB**；c− 基本没有改善。

当前 v4 的价值主要不是“指标变好了很多”，而是把问题进一步定位清楚：

**现有局部结构没有提供缺失的独立控制方向。**

---

## 5. 当前真正的瓶颈：局部控制方向失败

R11 的 step-normalized Jacobian 奇异值为：

```text
[0.1646, 0.07230, 0.002146, 0.000390]
```

条件数约：

```text
421.6
```

说明原来的几何参数虽然数学上满秩，但工程上已经接近秩亏，第四个控制方向几乎失效。

v4 为此新增了 junction-local post 高度和位置两个局部参数，并完成了五组 HFSS 中央差分识别。

结果：

- 最小奇异值增益：**2.23×**
- 预期第一道门槛：**≥ 5×**
- `sigma_min / sigma_max`：**0.00526**
- 筛选目标：**≥ 0.01**
- 判定：**FAIL_DIRECTION_GATE**

进一步按最新数学闭环里的弱方向投影判据：

```text
g_height = 0.000808
g_position = 0.000460

g_height + g_position = 0.001269
```

而理论上希望：

```text
g_height + g_position >= 0.130
```

现在只有目标量级的约 **1/102**。

这意味着当前 post 的问题不是“再调一点尺寸就行”，而是它对缺失的弱方向几乎没有控制能力。

另外已经补做了 post radius = 1.0 / 2.0 mm 的探测：

- 最小奇异值增益只有约 **1.32×**
- `sigma_min / sigma_max ≈ 0.00312`

因此继续扫 post 半径也没有意义。

---

## 6. 目前哪些指标已经完成，哪些还没有

### 已完成 / 已确认

1. **总体系架构已经确定**
   - Magic-T 四合一二叉树
   - H 路渐变脊阻抗变换
   - junction-local 被动匹配
   - 三螺钉只用于最后残差修正

2. **单 Magic-T HFSS 自动建模与 S4P 数据链已经跑通**

3. **奇偶模方向与对称性问题基本处理清楚**
   - forbidden parity leakage 已经达到约 −45 至 −49 dB 量级

4. **R11 Jacobian 与 v4 局部控制方向识别已经完成**
   - 已经知道为什么继续盲扫旧参数效率很低

### 尚未完成

1. **回波损耗 ≥ 22 dB：未完成**
   - 当前最差只有 2.77 dB / 5.41 dB
   - 这是当前最主要差距

2. **完整四路输入隔离度 ≥ 22 dB：未验证**
   - 当前 −45 dB 是 parity leakage，不能代替四路输入隔离度

3. **三螺钉调谐：尚未进入正式调谐阶段**
   - 当前被动回波远低于 18–20 dB 的螺钉激活门槛
   - 现在上螺钉只会把结构拖进高维盲调

4. **完整三级 Magic-T 网络：尚未闭环**
   - 目前没有完整四合一 HFSS 验证结果
   - interstage electrical length 尚未完成系统级优化

5. **合成效率 ≥ 95%：尚未验证**
   - 95% 对应总额外插损预算只有约 **0.223 dB**
   - 当前主要仿真仍为 PEC，PEC 不能证明真实导体损耗下的效率

6. **30 kW 峰值：尚未验证**
   - 还没有完整的局部峰值电场增强、圆角后场强、击穿裕度闭环

7. **1 kW CW：尚未验证**
   - 尚缺有限电导率损耗、热源分布和稳态温升分析

---

## 7. 当前不应该做什么

现阶段不建议：

- 直接大规模扫三颗调谐螺钉
- 继续对当前 post 的高度 / 位置 / 半径做大范围 Cartesian sweep
- 现在就搭完整四合一 3D 模型反复跑
- 用 −45 dB parity leakage 对外宣称“隔离度已经大于 22 dB”
- 用 PEC S 参数结果宣称 95% 效率、30 kW 峰值和 1 kW CW 已经完成

这些工作目前都会掩盖真正的问题：**单元的宽带匹配控制自由度还没有闭合。**

---

## 8. 下一步唯一优先级

下一步应继续保持 v4 总体架构不变，只替换 / 增强 **junction-local matching element**。

目标不是找“一个回波看起来更好”的参数，而是找到一个新几何变量，使它对 R11 的弱输出方向有足够大的投影。

推荐流程：

1. 设计新的 junction-local 对称结构候选
   - 可考虑局部 H-plane iris / capacitive-inductive loading
   - 非等价位置的 partial-height post / boss
   - junction 附近短局部 ridge / stepped reactive feature
   - 必须保持需要的奇偶模对称性和高功率圆角条件

2. 每个新候选只做少量 ± 扰动仿真

3. 先计算弱方向投影：
   `g_new = |u4^T c_new|`

4. 只有当新变量明显补足弱方向后，才重新识别完整 v4 Jacobian

5. 然后按阶段推进：
   - passive RL ≥ 10 dB
   - passive RL ≥ 15 dB
   - passive RL ≥ 18–20 dB
   - 再启动三螺钉残余调谐
   - nominal RL ≥ 22 dB
   - 再做三 Magic-T 四合一网络闭合
   - 最后进入有限电导率 / 峰值场 / 热分析

---

## 9. 当前文档里的两个需要统一的地方

仓库当前仍有少量版本漂移，后续应统一：

1. **post 位置**
   - 一些数学文字仍写 1.5 mm
   - 实际 v4 仿真已经使用 **2.0 mm**
   - 当前结果应以 `hfss/results/v4_local_identification/` 为准

2. **三螺钉轴向位置**
   - `v4_full_architecture.md` 和当前 seed 仍为：
     `[0, 8.4, 17.6] mm`
   - 最新 `v4_mathematical_synthesis.md` 已重新分析出更好的宽带基：
     `[0, 5.0, 19.5] mm`
   - 在真正开始螺钉识别前必须统一 builder / seed / 文档，避免按旧位置继续跑仿真

---

## 10. 一句话现状

**现在已经把四合一 Magic-T 的总体架构、HFSS 自动化和主要物理问题定位清楚了，但核心的单元宽带匹配还没有闭合；最新 v4 post 控制方向测试明确失败，所以当前重点不是继续堆螺钉或搭整机，而是先找到一个真正补足弱 Jacobian 方向的 junction-local 无源匹配结构。**

当前项目因此处于：

**“架构已定 + 单元诊断完成 + 宽带匹配控制结构待突破”阶段。**
