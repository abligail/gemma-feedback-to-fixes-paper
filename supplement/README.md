# Companion materials — Current Baseline

当前配套[主基准正稿](../manuscript.md)（[重构与归档说明](../review/baseline-rewrite-20261111.md)）。本版将完整过程与工具分配表移入补充，正文用两图、三表展示四阶段损耗链路主线；七条最终配置反证作为核心，四批八条完整保留。历史标签、语义审读与全部结局继续保留，早期迭代稿保存在主项目归档中。

## 当前基准分析与补充表

| 材料 | 内容 |
|---|---|
| [完整方法](methods.md) | 设计、预算、测量定义与两版口径的对应 |
| [英文复核指南](reproducibility.md) | 配置、seed、主要结果与关键案例的统一入口和重建命令 |
| [完整续修过程表](continuation-process-v04.md) | 全108题次的重跑、保留修改、D转移、最终通过及正常配对分母 |
| [图表预览](../figures/README.md)、[图表来源清单](../evidence/visuals-v04.json) | 两图的PNG/SVG、数据范围、输入与输出哈希、图内实际文字 |
| [过程分析JSON](../evidence/process-analysis-v04.json) | 三种配置范围的汇总、216份packet身份、四条完整编辑机会轨迹 |
| [阶段判断输入](../evidence/check-phase-judgments-v04.json) | 13条源码变化与共同检查交叉分支的事件判断，另记一条文档增量 |
| [check-phases-v04.csv](check-phases-v04.csv) | 全155条原共同检查重跑标签的初稿/修后阶段，原证据并存 |
| [check-construction-v04.csv](check-construction-v04.csv) | 全216题次的输出、命令启动、目标触达、公开依据与原语义 |
| [source-delivery-v04.csv](source-delivery-v04.csv) | 全432分支的源码差异、保留类别、原标签、补丁身份与D/返回结果 |
| [edit-opportunities-v04.csv](edit-opportunities-v04.csv) | 四条预算拒绝的前八次实际机会、首源码请求、时间与返回D |
| [result-action-outcome-v04.csv](result-action-outcome-v04.csv) | 全216题次连接共同结果类别、D状态、C/F检查阶段、源码变化与正常配对差异 |
| [交叉分析JSON](../evidence/reviewer-analysis-v04.json) | 最终/全部配置三组的汇总，八反证的双臂结果与首源码编辑事件，最终配置按批次/仓库及D状态分解 |
| [final-configuration-breakdown-v04.csv](final-configuration-breakdown-v04.csv) | 两批与四仓库的题数、质量分布、重跑、保留源码变化及正常配对结果 |
| [draft-status-breakdown-v04.csv](draft-status-breakdown-v04.csv) | 已过、未过、技术未知和未评分D的后续行为、正常D配对及通过保留/新增/丢失 |
| [tool-allocation-v04.csv](tool-allocation-v04.csv) | R03/R04按全体108、未过64、已过40、有依据20、反证7分组的C/F工具调用分布、8次上限耗尽与缺参编辑统计 |

## 原始结果与v0.3复核

- [逐端点评分](feedback-task-outcomes.csv)、[D转移](../evidence/draft-transitions.csv)、[全部十条差异](feedback-discordances-v03.csv)。
- [32条原源码标签审读](source-branch-retention-v03.csv)、[42条检查语义复核](check-semantic-review-v03.csv)与[原完整复核](../evidence/revision-public-review-v03.md)。
- [原构造诊断](checker-delivery-v03.csv)、[原四条拒绝](budget-denied-edits-v03.csv)、[原八反证](../evidence/counterevidence-slots.csv)。
- [Study A逐题结果](checking-task-outcomes.csv)、[同54题行为](../evidence/checking-official54.csv)、[完整额外范围/v2](../evidence/checking-outcomes.csv)。
- [原探索区间及缺失界限](uncertainty.md)、[未知端点](../evidence/missing-endpoints.csv)、[正常空补丁通过](../evidence/scored-empty-passes.csv)。
- [原标注分片信息](annotation-partitions.csv)、[固定版本文献](../references/ledger.md)。

原“同检重新执行”不再统称为初稿再获取。v0.4明确记录初稿与修后阶段，并保留调用修正及诊断变体。原32条源码标签也没有改写；全补丁核对补入一条原标为辅助变化的docstring增量。

依次运行build_v04_analysis.py、build_v04_review_analysis.py重建原分析；build_v04_visuals.py从冻结分析生成两图、两张展示表及完整过程表，另需Matplotlib；build_text_manuscript.py重建阅读版并将图内文字计入字数。阶段预算、完整过程、批次/仓库及D状态分解保留在补充材料。本轻量仓库包含[阶段提示词、周期报告与核心案例](../protocol/README.md)；两个分析脚本使用完整派生CSV/JSON重建汇总，并复算八反证案例。全量原packet提取需要完整源归档。当前5页PDF已编译并完成视觉检查。
