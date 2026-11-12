# 主基准主张与来源

当前主基准沿用既有实证数据并补入完整工具分配、接口容错与跨周期提示消融审计。图2连接未过初稿中的重跑、8次工具上限耗尽、保留修改、新通过、工具替代效应和四条编辑阻断；表1包含完整108次构造尝试，表2拆分C/F数值列，表3汇总三轮855次运行（共2,565次）的提示级消融实验。图表与输入的绑定见[来源清单](visuals-v04.json)，重构与深化记录见[baseline-rewrite-20261111.md](../review/baseline-rewrite-20261111.md)。原实验评分、语义标签和完整八案例记录保持原样。

| 主张 | 数据与原文入口 | 测量口径 |
|---|---|---|
| 全研究规模：95道任务、15个仓库、3,517次运行与共享初稿题次（3,949个评分端点） | [交叉分析JSON](reviewer-analysis-v04.json) `program_scale_summary` | Study A 736次运行 + Study B 216题次（864会话/648评分端点） + 三轮提示消融 $3 \times 855 = 2,565$次运行 |
| 最终配置108题次中85有输出，20有依据且触达，7反证 | [新过程分析](process-analysis-v04.json)、[构造逐题表](../supplement/check-construction-v04.csv)；原behavior-summary-R03/R04 | 两批均为同54个不同任务 |
| 85份输出分解为38/7/9/11/20 | 新JSON summary.final_configuration.coverage；构造逐题表 | 38核对命令及实际找不到PY文件的stderr；其余沿原公开依据/目标触达标签 |
| 初稿与修后检查需要分别统计 | [阶段判断输入](check-phase-judgments-v04.json)、[155行阶段表](../supplement/check-phases-v04.csv) | 13条同时有源码已改/同检标签的分支直接核事件；其余沿原动作判断并核源码差异。原同检范围含调用修正及诊断变体 |
| R03/R04 C/F初稿重跑82/43，修后4/3 | 新JSON summary.final_configuration.responses | 计分支且两项可重叠；其中Rich3718/C修后是同输入的ANSI打印诊断，不冒充原断言通过 |
| FastAPI13537/R02/F和Rich3067/R03/F首次分支重跑发生在修后 | 阶段判断对应行；原packet事件6→7 | 未把这些修后验证计作初稿上的再获取 |
| 全432返回补丁中29保留可执行源码变化、3仅docstring；另有1中途变化后恢复D | [全分支交付表](../supplement/source-delivery-v04.csv)、新JSON；原[源码审读](revision-public-review-v03.json) | 29=原24保留类+4逻辑删除+1引号语法修订；3文档含新补入的Rich3052/R03/F。计源码部分，不将辅助文件变化当业务变化 |
| 最终配置C/F保留可执行源码变化10/9 | 新JSON及全分支交付表 | 表示最终存在非文档源码变化，包括不完整或未验证变化 |
| 最终配置D→C/F新增3/3、丢失0/1，最终43/42 | 新JSON responses；原analysis-R03/R04 | 正常D/C104对、D/F103对；完整108题次的通过数另列 |
| 最终D为40已过、64未过、3技术未知、1未评分no_patch | [初稿状态分解](../supplement/draft-status-breakdown-v04.csv)、交叉分析JSON final_configuration_draft_status_breakdown | 从原432行交付记录读取D状态；C/F的D状态与补丁哈希逐题一致；评分只用于事后分析 |
| 64个未过D中C/F共同检查重跑46/22、保留修改8/8、各有3次新通过；正常C/F63对为F两进两退 | 同上；[216行交叉表](../supplement/result-action-outcome-v04.csv)的draft_status列 | C正常64次、F正常63次和技术未知1次；行为分母均64，来自37个不同任务。相同通过总数包含不同成功续修 |
| 40个已过D中C/F保留通过40/39 | 同上 | 两支均40个正常配对；已过D的2/1条源码修改包含在全体10/9中 |
| 20份有依据且触达检查对应10已过D、10未过D | 交叉分析JSON final_grounded_checks_by_draft | 13份局部预期一致对应10已过和3未过D；7份反证全部为未过D |
| 最终C/F103正常对F两进三退；四批206正常对四进六退 | 原analysis-R03/R04与[v0.3全部差异](../supplement/feedback-discordances-v03.csv) | 不同批次保持身份；六个不同任务贡献四批十条差异 |
| 最终20个有依据且触达检查：C/F初稿重跑20/4、保留编辑1/3，F一进零退 | [第二轮分析](reviewer-analysis-v04.json)、[216行交叉表](../supplement/result-action-outcome-v04.csv) | 20题次来自16个不同任务；既有质量标签分组，正常C/F均20对 |
| 其他65输出F一进一退；无输出23题次零进两退 | 同上 summary.final_configuration | 正常C/F62/21对，未知端点仍保留；无输出表示没有共同结果，分支可以自己执行检查 |
| 两批初稿重跑C/F分别38/23、44/20，保留修改5/5、5/4 | [分解CSV](../supplement/final-configuration-breakdown-v04.csv)、交叉分析JSON final_configuration_breakdowns.by_batch | 同一最终配置，分别54题次；正常C/F52/51对，F新增/丢失1/1与1/2 |
| 三个较大仓库组均有较少的F初稿重跑，F新增/丢失1/0、1/2、0/1 | 同上 by_repository | FastAPI/Rich/Requests分别52/36/18题次、49/34/18正常对；HTTPX仅1题2题次并单列；描述范围内分布 |
| 四条反证分支首编辑被拒，仍余约30–79秒 | [完整机会轨迹](../supplement/edit-opportunities-v04.csv)、新JSON budget_timelines | 首八次实际消耗的普通机会、首源码请求、拒绝事件及D相同交付绑定；精确剩余范围约30.1–78.5秒 |
| FastAPI14986/15800前八次均定位/读取；Rich3518七读一检；FastAPI13786四读一搜三执行 | 同上 | 运行错误仍可消耗机会；已被BudgetExceeded拒绝的额外请求不再算已消耗机会 |
| 八反证三条保留且过、四条预算拒绝、一条未保留 | 原[v0.3八槽](revision-public-review-v03.json)；新时间线 | 保留全部八条范围；Requests6592的C也通过 |
| 最终配置七反证F两通过、四首编辑拒绝、一无保留修订；C一通过 | [八反证逐题记录](counterevidence-slots.csv)、交叉分析JSON counterevidence_comparison；仅取R03/R04 | 四条被拒案例中C/F均未过；R02的FastAPI13537是四批总计额外的一条F独有成功 |
| Rich3067/R03的C获得同一反证但编辑请求缺参，F修正请求后实际编辑并通过原检查 | [R03公开packet](../protocol/packets/study-b/R03/rich_3067.json)、[阶段判断](check-phase-judgments-v04.json)、[源码交付表](../supplement/source-delivery-v04.csv) | C事件0复现失败，17次缺old_string的请求未改源；F事件4/5缺参、6实际编辑、7执行与共同检查逐字相同的命令并exit0。D/C均为空补丁且正常评分未过，F保留源码且评分通过 |
| Rich3067/R03与R04是不同题次、分别生成的D | 两份公开packet及源码交付表 | R03 D为0字节；R04 D为1142字节，二者不串成同一连续修复轨迹 |
| FastAPI13537/R02/F通过记录已处理alias防止空字符串被再次加入，修后原目标断言通过；C返回失败D | [公开packet](../protocol/packets/study-b/R02/fastapi_13537.json)、阶段判断及案例证据 | 题面说明两轮字段处理；F事件6实际源码编辑、事件7执行原目标节点；保留的断言未改，原独立评分D/C失败、F通过 |
| 八反证D全部失败，C/F通过1/3；C有两条对应首编辑额度拒绝 | 第二轮JSON counterevidence_comparison；原counterevidence-slots.csv | FastAPI15800/R04/C及Rich3518/R04/C均为零基事件9，记录BudgetExceeded；不把F拒绝都写成F特有问题 |
| Requests7433删除题面要求的D逻辑，Rich3067/R04临时改后恢复 | 原[源码审读](revision-public-review-v03.md)、[案例证据](case-evidence.json) | 前者从已过D丢失通过；后者F保持未过D、C实现修复。二者均属F相对C退步，交付含义不同 |
| Study A同54题检查增加，正常对七进七退 | [原同范围表](checking-official54.csv)、[原结果表](checking-outcomes.csv) | 三批162题次；143正常配对（75 vs 75）。R03全95题反证39升至60，复验37升至53；外部29题48 vs 47 |
| 64个未过D中动作替代：F相对C的`run_command`减少29（$226 \to 197$）、`get_status`减少11（$17 \to 6$），但`read_file`增加30（$239 \to 269$）；全108题次`run_command` $387 \to 328$、`read_file` $390 \to 433$ | [工具分配表](../supplement/tool-allocation-v04.csv)、[交叉分析JSON](reviewer-analysis-v04.json) `tool_allocation_summary` | 直接汇总R03/R04全部108份公开packet中已执行的普通工具调用（不含已被`BudgetExceeded`拦截的请求） |
| R03/R04中58次已执行`read_file`（C 25次、F 33次；未过D上24次）传入带多余引号的畸形可选键（如`"start_line\"": "151"`），因`start_line`可选被静默忽略并在56/58次（C 24、F 32）中回退至第1–150行 | 同上 `malformed_read_key_calls` / `silent_line1_reset_reads` | 直接审计R03/R04全部已执行`read_file`调用的原始参数键与返回首行号 |
| Stage 1与Stage 2桥接：`Other output`（65题次，含38例`python3 -B PY`）中60%（39/65）F分支重跑/修补检查；`Grounded target`（20题次）中F重跑下降80%（$20/20 \to 4/20$）、首调用即`read_file`从$6/20 \to 16/20$、发起源码编辑分支翻倍（$4/20 \to 8/20$，其中4/8触发`BudgetExceeded`） | [表2](../tables/result-groups-v04.tex)、[工具分配表](../supplement/tool-allocation-v04.csv) `grounded_target_20` / `other_output_65` | 按检查质量分层审计C/F首步动作、重跑率与源码编辑尝试率 |
| 64个未过D中C/F分别有53/64（83%）和57/64（89%）耗尽8次普通工具额度（全108题次均为87/108） | 同上 `cap8_exhausted` / `budget_exceeded` | 统计至少达到8次已执行普通工具或触发`BudgetExceeded`的分支数 |
| R03/R04七反证中C/F发起目标源码`edit_file`尝试的分支为4/7 vs 6/7（全四批八反证为4/8 vs 7/8），F分支呈四类结局：额度内落地（2/7 F，四批3/8，100%通过评分）、精确唯一匹配补丁差1槽被拦截（2/7 F：`Rich3518/R04`与`FastAPI13786/R04`及`Rich3518/R04` C，对D静态校验`occurrences = 1`）、双文件任务定位中途截断触发event 9残缺编辑（2/7 F：`FastAPI14986/R03`与`FastAPI15800/R04`及`FastAPI15800/R04` C）、目标文件首读被拦截（1/7 F：`FastAPI15589/R04`） | 同上 `counterevidence_7`、[完整机会轨迹](../supplement/edit-opportunities-v04.csv)、[交叉分析JSON](reviewer-analysis-v04.json) `counterevidence_comparison` | 对7条R03/R04反证双臂的首个源码`edit_file`请求与初稿D已读窗口做确定性静态匹配校验 |
| FastAPI14986/R03、FastAPI13786/R04、FastAPI15800/R04的F分支（及FastAPI15800/R04、Rich3518/R04的C分支）在event index 8读取/命令触发`BudgetExceeded`后的下一轮（event index 9）立即发出源码`edit_file`补丁被拒 | [完整机会轨迹](../supplement/edit-opportunities-v04.csv)、[交叉分析JSON](reviewer-analysis-v04.json) `counterevidence_comparison` | 零基事件索引核验：第9次请求（index 8）首次收到`BudgetExceeded`，紧接第10次请求（index 9）即为首个源码`edit_file` |
| 64个未过D中C/F分别累计45次和48次（共93次，集中于11个分支）漏传`old_string`的`edit_file`拒绝：93/93（100%）原始参数实际包含被吞入`new_string`的`old_string:`，82/93（88%）将目标代码按`:`/`,`拆成伪参数键 | [工具分配表](../supplement/tool-allocation-v04.csv)、`reviewer-analysis-v04.json` `missing_param_swallowed_old_string` / `missing_param_bogus_split_keys` | 直接解析93次返回`Missing mandatory parameters: old_string`的`edit_file`原始参数字典 |
| 表3与讨论中引用的三项后续855次运行实验周期（共2,565次运行：原生子代理局部递归、编辑恢复、选择性继承） | [表3](../tables/prompt-ablations-v04.tex)、[局部递归报告](../protocol/cycles/2026-10-25-local-recursion/report.md)、[编辑恢复报告](../protocol/cycles/2026-10-15-strong-baseline-recovery/report.md)、[选择性继承报告](../protocol/cycles/2026-10-23-local-progress/report.md) | 局部递归子代理89–96%超软预算（中位21–24次请求，R03官方25 vs 19/22）；提示级编辑恢复R03仅3/33完成且0通过（官方均差0.0pp）；提示级`keep`/`reject`在190次运行中23次`keep`、0次`reject` |
| 648评分端点620正常、25未知、3未评分no-patch；5正常空补丁通过 | [原逐端点](../supplement/feedback-task-outcomes.csv)、[空补丁通过](scored-empty-passes.csv) | 沿用官方原判，空补丁不自动判失败 |

新增阶段、命令启动与源码分解是结果已知后的分析。源码身份核对和事件时序支持过程事实，公开语义判断保留AI审读来源。提议的结构化检查接口、编辑机会预留和接受政策属于讨论中的下一步研究。
