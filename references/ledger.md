# Literature ledger — fixed metadata reused in v0.3 and v0.4

2026-11-09已用[固定版本响应记录](../review/reference-check-20261109.json)核对8项标题、作者、首次发布日期、所读版本日期和URL，全部响应为HTTP 200。BibTeX由[update_references.py](../scripts/update_references.py)生成，作者姓名保留准确拼写；年份采用首次arXiv发布日期，另列固定版本日期。没有推断期刊/会议录用信息。

v0.2修订已核验首页元数据及最直接近邻的既有设计阅读；v0.3沿用同日固定响应和相同8项版本，没有重新请求元数据，不声称重新通读/复现全部8篇论文。下面作用来自原阅读账本和审稿核对；文献报告效果并非本项目复现结果。

| Key | 准确题名与固定版本 | 在当前论证中的作用 |
|---|---|---|
| looping | [Looping Is Not Reliability: State-Bound Evidence and Typed Revision Contracts for Agentic Code Repair — 2607.24604v3](https://arxiv.org/abs/2607.24604v3) | 最直接近邻；27/30共同状态选择、修复/损伤、版本及仓库实验已有先例 |
| feedbackeval | [FeedbackEval: A Benchmark for Evaluating Large Language Models in Feedback-Driven Code Repair Tasks — 2504.06939v2](https://arxiv.org/abs/2504.06939v2) | 反馈来源和错误起点，与完整自然初稿的估计范围对照 |
| selfrepair | [Is Self-Repair a Silver Bullet for Code Generation? — 2306.09896v5](https://arxiv.org/abs/2306.09896v5) | 修复、反馈和采样成本；原始年份2023，所读v5日期2024 |
| selfdebug | [Teaching Large Language Models to Self-Debug — 2304.05128v2](https://arxiv.org/abs/2304.05128v2) | 执行反馈/解释和公开测试覆盖 |
| swtbench | [SWT-Bench: Testing and Validating Real-World Bug-Fixes with Code Agents — 2406.12952v3](https://arxiv.org/abs/2406.12952v3) | 生成测试、issue复现与补丁验证 |
| cogeneration | [Dynamic Cogeneration of Bug Reproduction Test in Agentic Program Repair — 2601.19066v3](https://arxiv.org/abs/2601.19066v3) | 测试与修复共同生成 |
| coharden | [Beyond Fail-to-Pass: Iterative Hardening of Co-Generated Bug Reproduction Tests and Fixes — 2607.19843v1](https://arxiv.org/abs/2607.19843v1) | 公开测试F→P不足以认证下游正确性 |
| genesis | [Persistent Recursive Worlds Enable Autonomous Software Evolution — 2608.10450v3](https://arxiv.org/abs/2608.10450v3) | 持久软件状态、有限寿命代理与接受；只进入未来问题讨论 |

原阅读入口包括research/cycles/2026-10-14-feedback-refinement/source-refresh-literature.md、2026-10-12-trigger-validity/source-refresh-literature.md及2026-10-26-post-residual-research-discussion.md。版本差异保留，不能将新版本内容自动套给旧实验。

## 仍需讨论

当前经验增量定位在完整固定自然初稿下的生成检查覆盖和交付关系，是否足以满足目标投稿的研究贡献要求仍需判断。换模型、共同状态或额外监控标签自身不承担新颖性。不存在引用元数据未核验而写入虚构作者/会议的情况。
