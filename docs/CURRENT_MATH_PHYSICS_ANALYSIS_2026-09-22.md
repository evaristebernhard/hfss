# HFSS v4 数学物理分析：当前失配机理与下一步匹配结构

日期：2026-09-22

基于最新 v4 单 Magic-T HFSS 数据：hfss/results/v4_local_identification/center.s4p。

## 1. 核心结论

当前问题已经不是“多扫几个参数”可以解决的。

最新 v4 的主要矛盾是：

1. H/even 模在 9 GHz 出现严重的等效实部阻抗塌陷；
2. H/even 模的反射随频率快速旋转，中心值和频率斜率都很大；
3. 当前局部 post 的高度和位置，本质上主要产生同一种 shunt-reactive 控制，无法补足 R11 中缺失的弱 Jacobian 方向；
4. E/odd 模自身也没有匹配闭合，因此即使只把 H/even 模修好，也无法让物理输入端的回波和输入间隔离同时达到 22 dB；
5. 下一版不应该继续扩大 post sweep，而应该把 J0 改成至少包含两种物理独立反应的低阶宽带匹配单元。

## 2. 奇偶模与真实物理端口

两个共线输入端定义

a+ = (a1 + a2)/sqrt(2)

a- = (a1 - a2)/sqrt(2)

对称 Magic-T 中：

even / c+ <-> H / sum arm

odd / c- <-> E / difference arm

在 parity leakage 已经很小时，共线输入端的散射关系近似为

S11 = (Gamma+ + Gamma-) / 2

S12 = (Gamma+ - Gamma-) / 2

因此严格有

|S11|^2 + |S12|^2 = (|Gamma+|^2 + |Gamma-|^2) / 2

这说明不能只优化 S11。

如果 Gamma+ 和 Gamma- 都很大但方向相反，S11 可以因为相消而看起来很好，同时 S12 会非常差。当前 v4 正是这种情况。

## 3. 当前物理端口真实指标

从最新 center.s4p 直接读取共线端口 P1/P2：

| 频率 | P1 回波损耗 | P1-P2 隔离 |
|---|---:|---:|
| 9.0 GHz | 13.17 dB | 5.49 dB |
| 10.25 GHz | 16.61 dB | 4.85 dB |
| 11.5 GHz | 24.21 dB | 4.58 dB |

因此如果客户指标定义为普通物理端口 Return Loss >= 22 dB、Input Isolation >= 22 dB，则当前最差物理端口回波约 13.17 dB，最差输入间隔离约 4.58 dB。

-45 dB 左右的 forbidden parity leakage 不是普通输入端隔离。

## 4. H/even 模的等效阻抗

由

z = (1 + Gamma) / (1 - Gamma)

将最新 HFSS 模态反射换算为归一化等效阻抗。

| 频率 | |Gamma+| | z+ |
|---|---:|---:|
| 9.0 GHz | 0.727 | 0.158 - j0.002 |
| 10.25 GHz | 0.708 | 0.852 + j1.843 |
| 11.5 GHz | 0.645 | 0.720 - j1.403 |

9 GHz 最关键：

z+ ≈ 0.158 - j0.002

它几乎是纯实数，但只有目标阻抗的 15.8%。

换成归一化导纳：

y+ ≈ 6.32 + j0.12

这意味着 9 GHz 低频端不是“多了点电容或电感”这么简单，而是出现了严重的等效阻抗变换错误。

如果在同一个参考面只加一个理想 shunt susceptance：

y_new = 6.32 + j(0.12 + b)

无论 b 取多少，Re(y_new) 都保持 6.32，不可能直接变成目标 1 + j0。

因此单独依靠一个局部 shunt-like post，在低频端从物理机制上就不够。它必须与另外一种能改变阻抗变换比 / conductance 的机制配合。

## 5. H/even 模还有严重的频率斜率问题

v4 在 10.25 GHz 的特征向量：

Gamma0 = 0.4573 + j0.5417

dGamma/df = 0.9338 - j0.8372 per GHz

因此

|Gamma0| ≈ 0.709

|dGamma/df| ≈ 1.254 / GHz

22 dB 回波目标要求：

|Gamma| <= 10^(-22/20) = 0.07943

频带中心到边缘 Delta f = 1.25 GHz。

如果只看一阶局部模型，即使中心反射完全消掉，为了不让边缘超出 0.0794，斜率大致也需要满足：

|dGamma/df| <= 0.07943 / 1.25 ≈ 0.0635 / GHz

而现在约为 1.254 / GHz，约大了 19.7 倍。

所以现在不是只需要把中心点拉到 Smith 圆心，还必须同时压低反射轨迹的频率斜率。

## 6. 为什么最新 post 方向测试失败

R11 的 step-normalized singular values：

[0.1646, 0.07230, 0.002146, 0.000390]

条件数约 421.6。

v4 新增 post-height 和 post-position 后：

post height weak projection = 0.000808

post y weak projection = 0.000460

合计 = 0.001269

而合理步长内补掉当前弱方向误差的估算门槛约为 0.130。

当前只有目标量级的约 0.98%。

另外，新 post 列真正落到旧 Jacobian 最弱方向上的比例仅约：

- post-height：3.2%
- post-y：3.6%

绝大部分变化仍然落在原来已有的强方向里。

因此扩大 post 高度、位置或半径 sweep，主要只是重复已有控制，不会解决秩亏。

## 7. 从传播相位解释 post-height / post-y 为什么不独立

WR90 的 TE10 导波波长约为：

| 频率 | lambda_g |
|---|---:|
| 9 GHz | 48.63 mm |
| 10.25 GHz | 38.05 mm |
| 11.5 GHz | 31.73 mm |

当前 post-y 的识别半步只有 0.5 mm。

局部反射位置变化的相位变化近似：

Delta phi = 2 beta Delta y

0.5 mm 对应：

- 9 GHz：约 7.4°
- 10.25 GHz：约 9.5°
- 11.5 GHz：约 11.3°

post-height 主要改变局部反射强度；post-y 在当前小范围内只把几乎同一个反射矢量旋转几度。

这两个变量在宽带复反射空间里天然接近共线，所以 Jacobian 没获得真正的新控制维度。

## 8. E/odd 模也必须闭合

当前 odd 模等效阻抗：

| 频率 | |Gamma-| | z- |
|---|---:|---:|
| 9.0 GHz | 0.364 | 1.771 + j0.700 |
| 10.25 GHz | 0.444 | 0.503 - j0.499 |
| 11.5 GHz | 0.538 | 0.420 + j0.590 |

因此 E/odd block 也远没有达到匹配状态。

即使未来把 Gamma+ 完全修到 0，如果 Gamma- 保持现在约 0.4–0.54，则

S11 ≈ Gamma-/2

S12 ≈ -Gamma-/2

物理回波和隔离仍只有约 11–15 dB。

所以最终必须形成两个相对独立的闭环：

H/even block -> Gamma+ -> 0

E/odd block -> Gamma- -> 0

## 9. 22 dB 物理回波 + 22 dB 隔离的模态条件

定义：

epsilon = 10^(-22/20) = 0.07943

要求：

|S11| <= epsilon

|S12| <= epsilon

由 Gamma+ = S11 + S12、Gamma- = S11 - S12，可得必要条件：

|Gamma+| <= 2 epsilon = 0.1589

|Gamma-| <= 2 epsilon = 0.1589

对应模态回波损耗至少约 15.98 dB。

这是必要条件，不是稳健设计条件。

更稳妥的工程目标仍应是：

RL_even >= 22 dB

RL_odd >= 22 dB

## 10. 当前合成效率为何还谈不上 95%

在 PEC、parity leakage 很小的情况下，H/even block 近似满足：

|Gamma+|^2 + |t_H|^2 ≈ 1

最新中心模型：

- 9 GHz：|tH| = 0.687
- 10.25 GHz：|tH| ≈ 0.705
- 11.5 GHz：|tH| ≈ 0.763

单个 Magic-T 的 sum-mode 功率传输大约只有 47%–58%。

若粗略把两个同样 stage 级联，并暂时忽略 interstage 多重反射，两级功率因子约为 |t_H|^4：

- 9 GHz：约 22%
- 10.25 GHz：约 25%
- 11.5 GHz：约 34%

这不是完整四合一网络结果，只用于说明：当前离 95% 的主要差距首先来自失配，不是铜损。

## 11. 达到 22 dB 匹配以后，95% 效率预算

若每个 stage 都恰好达到 22 dB：

|Gamma| = 0.07943

1 - |Gamma|^2 = 0.99369

两级只考虑反射：

eta_mismatch ≈ (1 - |Gamma|^2)^2 ≈ 98.74%

对应约 0.055 dB。

总 95% 目标对应约 0.223 dB。

因此匹配达到 22 dB 后，留给真实导体、接触、表面粗糙度等耗散的总预算约为：

0.223 - 0.055 ≈ 0.168 dB

所以 95% 最终仍然很严，但那是匹配闭合后的下一阶段问题。

## 12. 下一版 J0 的物理结构

建议保持整个 v4 总体架构不变，只替换 J0 的控制基底。

不要再把两个自由度都放在同一个 cylindrical post 上。

建议做成真正的 two-reactance matching cell：

junction
-> J0a: H-plane inductive / impedance-transforming step
-> short electrical spacing
-> J0b: rounded capacitive boss/ridge pair
-> existing mild throat
-> existing terminal ridge / taper

J0a 通过局部 broad-wall width / H-plane iris / stepped throat 控制等效 series / transformer action，负责改变实部阻抗变换和部分反射相位。

J0b 通过 top-bottom rounded boss / ridge gap 提供较强 shunt capacitive action，负责剩余虚部和反射零点位置。

关键不是具体名称，而是两个参数必须对应两种不同的场能储存机制，而不是同一个 post 的“强一点”和“挪一点”。

## 13. 两个局部反应建议相隔约 lambda_g / 8

10.25 GHz：

lambda_g ≈ 38.05 mm

lambda_g / 8 ≈ 4.76 mm

如果两个反应中心相隔 4.5 mm，则反射相位差 2 beta d 约为：

- 9 GHz：66.6°
- 10.25 GHz：85.1°
- 11.5 GHz：102.1°

这比当前 0.5 mm 扰动对应的 7–11° 强得多。

因此两列 Jacobian 在中心频率附近有机会接近正交，而不是再次塌在同一个方向。

## 14. 单频 L-match 计算说明需要的反应量级

把 9 GHz 的 z ≈ 0.158 暂时理想化成纯实负载。

若用标准两反应 L-match 将它变换到 1：

Q = sqrt(1/r - 1) ≈ 2.31

一种归一化解的量级约为：

|x_series| ≈ sqrt(r(1-r)) ≈ 0.365

|b_shunt| ≈ 2.31

这不是直接给 HFSS 几何尺寸，而是说明所需反应并不属于“微小修边”的量级。

当前 0.7 mm 高的小圆柱 post 更像残差修正元件，而不是承担低频大阻抗恢复的主匹配元件。

## 15. 下一轮仿真应该怎么跑

不做大 sweep。

只建立一个新的 J0 two-reactance candidate，然后先做局部辨识。

第一轮只留两个主参数：

p1 = junction H-plane / throat-step strength

p2 = downstream rounded capacitive boss height / gap

两者中心相距约 4.5–5.0 mm。

只跑：

center

p1-

p1+

p2-

p2+

然后计算每个新列对旧最弱方向的投影：

g_i = |u4^T c_i|

第一关不要看某个单频 S11 是否变漂亮。

先看 g1 + g2 能否从当前 0.00127 提升到 O(0.1) 量级。

如果仍明显低于 0.01，就直接淘汰该物理结构，不继续扫。

## 16. 优化目标应该改

后续不要以单个 S11 最小为目标。

在 parity leakage 已经足够小时，先直接优化 modal reflection：

J = max_f { |Gamma+(f)|, |Gamma-(f)| }

或者平方积分：

J2 = sum_f [ w+ |Gamma+(f)|^2 + w- |Gamma-(f)|^2 ]

并提高 9 GHz 和 11.5 GHz 两个带边权重。

当两个 modal block 都进入 15–18 dB 后，再切换到物理端口的 max |Sii| / max |Sij| 指标。

这样不会再出现靠 Gamma+ / Gamma- 相消“伪装出一个很好看的 S11”。

## 17. 最终判断

当前 cylindrical post pair 不是缺失的第四控制方向。

真正缺少的是：

一个能够改变阻抗实部变换 / 宽带斜率的独立反应

+

一个与之具有明显电气相位间隔的补偿反应。

因此下一步应从 single local post 转向：

two-reactance junction matching cell
= inductive / transforming element
+ approximately lambda_g/8 spacing
+ capacitive rounded element

然后重新做最小 Jacobian identification。

只有这一关通过，再进入 passive RL 10 -> 15 -> 18–20 dB，然后才值得启动三螺钉残差调谐和四合一系统闭合。
