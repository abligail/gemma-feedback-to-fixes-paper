# Writing checklist — Current Baseline (2026-11-12)

## 当前主基准已完成交付

- [x] 早期草稿与旧图表/脚本/PDF保存在主项目归档；本伴随仓库提供当前定稿。
- [x] 以自然、正面、去防御化、去AI套话的学术英文重写全篇，确立新标题 *Knowing the Bug Is Not Landing the Fix: Why Execution Feedback Stalls Before Patch Delivery in Budget-Constrained Coding Agents*。
- [x] 将 Study A（736次运行/95题）、Study B（216题次/54题/648评分端点）与后续三轮提示消融实验（$3 \times 855 = 2,565$次运行）统一为 **95道任务、15个仓库、3,517次运行与题次（3,949个评分端点）** 的四阶段损耗链路。
- [x] 直接汇总108份R03/R04公开packet的工具分配与接口诊断数据（[`supplement/tool-allocation-v04.csv`](supplement/tool-allocation-v04.csv)），量化未过D上的动作替代效应（`run_command` $226 \to 197$、`read_file` $239 \to 269$、8次上限耗尽 $53/64 \to 57/64$）、56/58次畸形`start_line"`分页键静默回退第1行、Stage 1$\to$2跨表桥接（`Grounded target`重跑降80%、首调用`read_file`从$6/20 \to 16/20$、源码编辑尝试从$4/20 \to 8/20$）及93/93次缺`old_string`拒绝中`old_string:`被吞入`new_string`（82/93拆出伪参数键）。
- [x] 完成七条R03/R04反证（四批八条）的四类结局静态验证：（1）额度内落地100%通过评分（2/7 F，四批3/8）；（2）精确唯一匹配补丁（`occurrences = 1`）差1槽被拦截（`Rich3518/R04` F/C与`FastAPI13786/R04` F）；（3）双文件任务定位中途截断触发event 9残缺编辑（`FastAPI14986/R03` F与`FastAPI15800/R04` F/C）；（4）目标文件首读被拦截（`FastAPI15589/R04` F）。
- [x] 新增**表3**（[`tables/prompt-ablations-v04.tex`](tables/prompt-ablations-v04.tex)）并在 Discussion 中汇总后续三个855次运行实验周期（Local Recursion、Edit Recovery、Selective Inheritance，共2,565次运行）的定量实证，提炼三项运行时机制设计原则。
- [x] 图1采用共享材料与F专属结果线路的原生SVG模板，正文嵌入矢量PDF；图2保留原内容。默认构建重建SVG并校验随仓库提供的PNG/PDF导出。
- [x] 含标题、署名（`Team xiakongxin`）、三张表格、图注和两图内全部文字的正文词数为2,942（2,993 word tokens，不含参考文献），严格满足 Kaggle Paper Track $\le 3,000$词限制。
- [x] 采用方案 A（NeurIPS 风格单栏 5 页版式，移除内部草稿日期行），通过 Tectonic 0.17.0（Unicode OpenType Latin Modern）零警告编译 5 页 PDF（[`output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf`](output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf)，SHA256 `4f9fb0b5ef26eeecff036bf728c022b9df460b05f231fb08604431dcd454da90`，PDF提取保守最大词数2,971）并完成全部5页渲染版面逐页目视检查（见[`rendering.md`](rendering.md)）。
- [x] 创建独立公开伴随仓库（Apache-2.0 许可），通过脱敏审查、图表/文本/PDF 构建复验并完成本地 Git 提交（按用户指示暂不上传 GitHub）。

## 内容讨论后的交付事项

- [x] 抬头署名采用参赛队名 `Team xiakongxin`（单人参赛）。
- [ ] 视最终投稿/发布需要决定是否将本地伴随仓库推送到 GitHub 公开仓库。
- [x] 2026-11-10直接核验官方概览/Rules及主办方澄清：3,000词不含参考文献，附录不保证主要评审阅读，Notebook/PDF可选；见[官方标准对齐讨论](review/kaggle-alignment-20261110.md)。
- [x] 将关键贡献与适用范围放在正文，准备项目内与独立伴随仓库中均可用的复核材料入口。
- [ ] 正式发布/投稿按用户授权执行并保存回执。

当前主基准交付为[Markdown正文](manuscript.md)、[编译版PDF](output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf)及[两图资源（图1含矢量PDF）](figures/README.md)；历史PDF与早期审稿记录保存在主项目归档中。
