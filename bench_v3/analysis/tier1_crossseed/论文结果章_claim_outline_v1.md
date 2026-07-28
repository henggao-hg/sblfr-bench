# 论文结果章 Claim Outline v1

来源: `三seed分析报告.md`, `01_outcome_by_seed.md`, `02_contrasts_C1_C5_paired.md`, `03_C6_safety_by_class.md`, 以及 `v3_ablation_weak_seed0.jsonl`。本文件用于写论文结果章与机制章,不替代原始分析表。

## 结果章主线

一句话版本: agent architecture 的收益取决于它补上的失败环节。weak actor 的主要问题是不会稳定生成/提交正确终局和可靠修复动作,外部 critic 与 persona aggregation 能改变动作分布; strong actor 的动作分布已经接近可用,step-level committee 收益有限,独立轨迹重试最有效; rubric 主要降低 dangerous failure,对 success 的提升有限且有预算成本。

建议结果章按四个问题展开:

1. 不同 architecture 是否提高成功率?
2. 成功率提升是否伴随 critical failure?
3. architecture 改变的是哪个失败环节:修复计算、终局收束、动作分布,还是采样方差?
4. ablation 是否支持这些机制解释?

## Claim 1: weak actor 的失败不是随机采样不够,同模型数量堆叠几乎无效

**结论。** qwen32b 在 single 下几乎不会完成任务;把同一个模型多采样、投票或 best-of-3 都不能有效修复。

**核心数字。**

| arm | SUCCESS seed0/1/2 | mean |
|---|---:|---:|
| single | 1/2/1 | 0.5% |
| sc3_vote | 1/0/0 | 0.1% |
| sc3_agg | 5/4/2 | 1.3% |
| bo3 | 1/1/2 | 0.5% |
| team_vote | 0/1/0 | 0.1% |

**统计支撑。**

- C5 weak: bo3 vs single, SUCCESS Δ = +0.0 pp, p = 1.000。
- C4-sel-sc3 weak: sc3_agg vs sc3_vote 虽显著,但绝对值很小: 1.3% vs 0.1%。

**机制解释。**

- weak 的基础动作分布里几乎没有终局动作: UNMANAGED 中终结动作提议 0/5518。
- 同模型温度采样只在原分布附近游走,无法创造足够多的 accept/handoff 终局候选。

**推荐图表。**

- 主 outcome stacked bar: weak single/sc3/bo3/team_vote 全部接近地板。
- C1-C5 contrasts 图: weak C5 接近 0。

**写作注意。**

- 不要把 weak 的失败写成模型“完全不会化学”。报告里有 evidence: 修复类曾达标 32%/27%/26%,但达标后自提 accept 为 0。
- 重点写成“会偶尔修到,但不会收束;同模型采样无法解决这个动作分布缺口”。

## Claim 2: weak actor 上,外部 critic 大幅提高 success,但 free 与 thin 体现不同交换

**结论。** qwen32b + external critic 是 weak 侧最大 success 增益。free critic 成功率最高; thin critic 更安全,但牺牲吞吐。

**核心数字。**

| arm | SUCCESS seed0/1/2 | CF seed0/1/2 | mean SUCCESS | mean CF |
|---|---:|---:|---:|---:|
| single | 1/2/1 | 26/37/32 | 0.5% | 11.5% |
| free_critic | 149/147/144 | 29/27/23 | 53.4% | 9.6% |
| thin_critic | 122/134/135 | 16/19/5 | 47.4% | 4.8% |

**统计支撑。**

- C2 weak: free_critic vs single, SUCCESS Δ = +52.8 pp, p = 1.1e-131。
- C3a weak: thin_critic vs free_critic, SUCCESS Δ = -5.9 pp, CF Δ = -4.7 pp, 两者均显著。
- C3b weak: thin_critic vs actor_rubric, SUCCESS Δ = +27.0 pp。

**机制解释。**

- free critic 提供两个通道:
  - 转向:批评里含具体操作和体积计算,把修复类达标率抬高。
  - 收束:达标后强制 accept,成功局中 accept 几乎都来自 critic revise。
- thin critic 把 critic 行为推向核验/计划采纳,减少 CF,同时在 8-step budget 下更容易 UNMANAGED。

**推荐图表。**

- weak outcome stacked bar。
- safety trade-off scatter: free_critic 在 high success / higher CF 区域; thin_critic 在 lower CF / lower success 区域。
- C6 safety table: weak thin CF% 6.0 vs free 21.3 on safety-discriminative classes, instrument fault_cleared 33.3 vs 4.0。

**写作注意。**

- free_critic 的 critic 是 qwen_max,这是能力落差注入。必须明说模型角色,避免读者误解为“critic 结构自身”无条件有效。
- thin_critic 的价值主要是安全性,不是总成功率最高。

## Claim 3: actor-rubric 能帮助 weak,但效果明显小于外部 critic

**结论。** 把 L2 rubric 直接写进 qwen32b actor prompt 有稳定收益,但不能替代外部 critic。

**核心数字。**

| arm | SUCCESS seed0/1/2 | CF seed0/1/2 |
|---|---:|---:|
| single | 1/2/1 | 26/37/32 |
| actor_rubric | 56/61/51 | 16/17/16 |
| free_critic | 149/147/144 | 29/27/23 |
| thin_critic | 122/134/135 | 16/19/5 |

**统计支撑。**

- C1 weak: actor_rubric vs single, SUCCESS Δ = +19.9 pp, CF Δ = -5.6 pp, 均显著。
- C3b weak: thin_critic vs actor_rubric, SUCCESS Δ = +27.0 pp, 显著。

**机制解释。**

- actor-rubric 主要帮助 easy/early cases,尤其 no_fault 或首测即可达标的场景。
- 随着 episode 变长,actor 对 rubric 的状态条件化执行衰减。

**推荐图表。**

- C1-C5 contrasts: weak C1 正向,但 C3b 更大。
- decay curve: actor-rubric 的收束率随首次达标 step k 下降。

**写作注意。**

- rubric 是 information injection。结果章应把它作为 architecture 的控制条件,用于判断 critic 增益是否只是“多给原则”。

## Claim 4: team_agg 揭示 weak actor 的生成-判别差距,但收益不如外部 critic且更不稳定

**结论。** 同一个 qwen32b 作为 aggregator,可以从 persona 多样性候选中选出比 single 好得多的动作; vote 选不出来。这个结果支持“多样化生成 + 判别式选择”机制。

**核心数字。**

| arm | SUCCESS seed0/1/2 | CF seed0/1/2 |
|---|---:|---:|
| team_vote | 0/1/0 | 7/2/5 |
| team_agg | 72/74/56 | 32/34/33 |
| sc3_agg | 5/4/2 | 19/43/28 |

**统计支撑。**

- C4-sel-team weak: team_agg vs team_vote, SUCCESS Δ = +24.4 pp, p = 6.2e-61。
- C4-prop-agg weak: team_agg vs sc3_agg, SUCCESS Δ = +23.2 pp。
- team_agg CF 高: C4-sel-team CF Δ = +10.3 pp。

**机制解释。**

- persona candidates 增加终局动作基础率; aggregator 能捞出少数派终局动作。
- vote 会埋掉少数派 accept/handoff。
- team_agg 的 seed 间波动较大: 72/74/56, 说明它依赖候选池抽样。

**推荐图表。**

- weak 2x2 mechanism figure: proposer=sc3/team, selector=vote/agg。
- action distribution/JSD 或 candidate proposal audit 作为补充。

**写作注意。**

- 这个 claim 适合说“同模型也能自举一部分”,因为 aggregator=actor 自己。
- 同时要报 CF: team_agg 成功提升伴随 CF 32/34/33。

## Claim 5: strong actor 上,step-level wrappers 大多处于等效带; bo3 是唯一稳定成功率提升

**结论。** qwen_max single 已经很强。大多数 per-step architecture 对 success 没有稳定提升; bo3 明显提高 success。

**核心数字。**

| arm | SUCCESS seed0/1/2 | mean |
|---|---:|---:|
| single | 212/210/218 | 77.6% |
| actor_rubric | 217/221/218 | 79.5% |
| free_critic | 208/208/214 | 76.3% |
| thin_critic | 203/197/225 | 75.7% |
| sc3_vote | 215/215/226 | 79.5% |
| sc3_agg | 222/225/226 | 81.6% |
| team_vote | 216/226/223 | 80.6% |
| team_agg | 212/222/217 | 78.9% |
| bo3 | 244/235/251 | 88.5% |

**统计支撑。**

- C5 strong: bo3 vs single, SUCCESS Δ = +10.9 pp, p = 7.9e-17。
- C5 strong: bo3 vs team_agg, SUCCESS Δ = +9.6 pp, p = 1.4e-16。
- C1/C2/C4 多数 success contrast 不显著或很小。

**机制解释。**

- strong 的失败很多是 stochastic closeout/rebuild trajectory variation; independent trajectory retry 可以收割方差。
- step-level committee 仍受同一局部决策分布约束,在强 actor 已经接近饱和时收益有限。

**推荐图表。**

- strong outcome stacked bar。
- C5 contrast 单独标出 bo3。
- 可在 appendix 展示 bo3 token/call 成本,因为它是 3x compute。

**写作注意。**

- bo3 是 compute-heavy baseline,别把它写成普通低成本 multi-agent。
- 和 weak 形成对照: weak bo3 无效, strong bo3 有效,说明失败类型不同。

## Claim 6: strong actor 上,rubric 主要买安全性,不买大幅成功率

**结论。** qwen_max 上 rubric/critic-rubric 对 success 贡献小,但明显降低 critical failure。

**核心数字。**

| arm | SUCCESS mean | CF mean |
|---|---:|---:|
| single | 77.6% | 1.7% |
| actor_rubric | 79.5% | 0.3% |
| thin_critic | 75.7% | 0.3% |
| team_agg | 78.9% | 3.1% |

**统计支撑。**

- C1 strong CF: actor_rubric vs single, Δ = -1.5 pp, p = 0.004。
- C3a strong CF: thin_critic vs free_critic, Δ = -1.2 pp, p = 0.013。
- C1 strong SUCCESS: actor_rubric vs single, Δ = +1.9 pp, p = 0.236, 不显著。

**机制解释。**

- strong actor 已有较好的修复和收束能力,原则的边际收益主要体现在避免危险动作。
- rubrics 也可能增加核验和谨慎倾向,在 tight budget 类上有吞吐代价。

**推荐图表。**

- success-CF tradeoff scatter。
- C6 safety classes table/figure。

**写作注意。**

- 这条要和 Claim 5 搭配: success 和 CF 是两根轴。

## Claim 7: SUCCESS 与 CRITICAL_FAIL 必须分开报告

**结论。** 同一 architecture 可以提高 success 也提高 CF,或者降低 CF 但降低 success。单一 success rate 会掩盖 safety-relevant behavior。

**关键例子。**

- weak free_critic: success 最高 53.4%, CF 9.6%。
- weak thin_critic: success 47.4%, CF 4.8%。
- weak team_agg: success 24.5%, CF 12.0%。
- strong team_agg: success 78.9%, CF 3.1%, 比 strong single CF 1.7% 更高。

**推荐图表。**

- Safety trade-off scatter: x=SUCCESS%, y=CF%, 分 weak/strong。
- C6 safety classes table。

**写作注意。**

- 用 Good Management / Critical Failure 解释为什么 endpoint success 不够。
- 避免把 HANDOFF 一律写成失败;在当前 main sweep 多数可解,但 held-out 可能有正确 handoff。

## Claim 8: ablation 支持 critic 的两通道解释:收束通道可由 stop-rule 复现,转向通道需要外部反馈

**结论。** A2 stop-rule 成功数落入预注册区间,说明 critic 的一大部分收益来自“达标后收尾”。free critic 额外成功来自转向/修复指导。

**核心数字 weak seed0。**

| arm | SUCCESS | CF | HANDOFF | UNMG |
|---|---:|---:|---:|---:|
| single | 1 | 26 | -- | -- |
| single_stoprule | 109 | 20 | 0 | 146 |
| free_critic | 149 | 29 | -- | -- |

**机制解释。**

- stop-rule 只看 visible fresh in-band measurement,不碰 hidden truth。
- 它复现 closeout channel,无法解决 instrument 类追假读数; instrument e_broke 17 例保留。
- free critic 相比 stop-rule 多出的约 38 个 success 是转向通道的估计。

**推荐图表。**

- ablation bar: single / stoprule / free_critic。
- stacked outcomes for A1/A2/A3。

**写作注意。**

- stop-rule 是机制控制,不要写成可部署 architecture。
- 它用 visible measurement,会有少量 a_accept CF,报告中为 3 例。

## Claim 9: rubric 重复刷新不是 free critic 的替代品

**结论。** A1 rubric_reassert 没有恢复 critic 的效果;它让 weak actor 过度抓住 accept 指令,造成大量 bad accept。

**核心数字 weak seed0。**

| arm | SUCCESS | CF | UNMG |
|---|---:|---:|---:|
| actor_rubric | 56 | 16 | -- |
| rubric_reassert | 88 | 85 | 100 |
| free_critic | 149 | 29 | -- |

**关键审计。**

- A1 CF 85 全部是 `a_accept_out_of_tol`。
- 修复类已提交纠正动作只有 3。
- k=1 桶成功较多,说明重复提示能让 actor 更愿意 accept,但条件化失败。

**机制解释。**

- 静态重复原则会持续施压,但 weak actor 不能可靠判断何时满足条件。
- critic 的优势在于状态条件化投递:只在具体草稿需要拦截或收尾时介入。

**推荐图表。**

- ablation stacked outcome。
- A1 CF reason pie/bar。

**写作注意。**

- 这是反驳“把 rubric 每轮塞进去就行”的关键实验。
- 表述时强调 harmful over-acceptance。

## Claim 10: personaB 单飞证明 persona token 能移动行为,但缺少 selector 会增加伤害

**结论。** A3 single_personaB 提升 success 到 team_agg 区间附近,但 CF 高,伤害主要来自鲁莽干预。

**核心数字 weak seed0。**

| arm | SUCCESS | CF |
|---|---:|---:|
| single | 1 | 26 |
| single_personaB | 60 | 61 |
| team_agg | 72 | 32 |

**CF reason。**

- single_personaB: `e_broke_good` 52, `d_discard_in_tol` 7, `a_accept_out_of_tol` 2。

**机制解释。**

- personaB 提高行动/终结倾向,但也推高 irreversible intervention。
- team_agg 的 selector 可拦截部分鲁莽动作,所以 CF 约减半。

**推荐图表。**

- personaB vs team_agg outcome/CF bar。
- CF reason breakdown。

**写作注意。**

- 原预测“a_accept 上升”被否,实际是 intervention CF 上升。论文里要把这一点作为预注册预测修正。

## 建议图表顺序

**主文图 1: Overall Outcomes Across Architectures.**

- Two panels: weak / strong。
- Stacked bars: SUCCESS, CF, HANDOFF, UNMANAGED。
- 信息: weak 的外部 critic 和 team_agg 能拉开地板; strong 的 bo3 明显最高。

**主文图 2: Success-Safety Trade-off.**

- x=SUCCESS%, y=CF%, 每点一个 arm, weak/strong 分面。
- 信息: success 与 CF 分离; thin/free/team_agg 的 trade-off 可见。

**主文图 3: Pre-registered Contrasts.**

- C1-C5 forest plot, success 与 CF 分开。
- 信息: weak C2/C3/C4 明显; strong C5 明显。

**主文图 4: Mechanism/Ablation.**

- A1/A2/A3 + key baselines。
- 信息: stop-rule 复现收束通道; repeated rubric harmful; personaB moves behavior with CF cost。

**补充图 A: Class-level heatmap.**

- 展示哪些 fault class 是 architecture-sensitive,哪些是全员 hard。

**补充图 B: C6 safety-discriminative classes.**

- CF%, OVER%, fault_cleared。

## 结果章可用小节结构

### 4.1 Overall performance separates weak and strong actors

讲主表。先交代 3 seeds × 2 actor × 9 arms × 275 episodes。weak 地板明显,strong baseline 高。

### 4.2 More samples do not rescue the weak actor

讲 weak single/sc3/bo3/team_vote。重点是数量堆叠归零。

### 4.3 External feedback rescues weak performance through redirection and closeout

讲 free_critic/thin_critic/actor_rubric/team_agg。这里放 C2/C3/C4。

### 4.4 Strong actors benefit mainly from independent trajectory retry

讲 bo3。强调 compute cost 和和 step-level committee 的差别。

### 4.5 Safety requires a separate axis

讲 CF, C6, thin/free trade-off, strong rubric 降 CF。

### 4.6 Ablations identify the mechanism

讲 A1/A2/A3。把机制从观察性 claim 变成干预证据。

## 讨论章可承接的点

1. 架构有效性的条件:必须补上 actor 缺的失败环节。
2. weak 的系统性错误需要改变/过滤动作分布。
3. strong 的随机失败适合独立重试。
4. Rubric 是 safety tool,也可能引入预算税。
5. 外部 critic 的效果和模型能力差相关; strong 侧 deepseek critic 证据较弱,需在 limitation 中说明。
6. 结果来自模拟实验室,held-out 与非 Qwen 探针是下一步泛化防守。

## 写作红线

- 不要把 free_critic 的 weak 增益写成纯 architecture 魔法;它包含 qwen_max critic 的能力注入。
- 不要把 bo3 写成低成本多智能体;它是 3x trajectory retry。
- 不要只报 SUCCESS;CF 是核心安全指标。
- 不要隐藏 A1 负结果;它是 critic 不可替代论点的关键。
- 不要把所有 HANDOFF 写成坏;主 sweep 可解性强,held-out 会改变 handoff 语义。
- strong 侧 free/thin critic 使用 deepseek,weak 侧使用 qwen_max;跨 actor 对比 critic 时必须说明角色不对称。
