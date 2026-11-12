# Local rendering and delivery — Current Baseline (2026-11-12)

## 当前主基准 PDF 验收（2026-11-12，原生SVG图1正式接入）

主稿（*Knowing the Bug Is Not Landing the Fix: Why Execution Feedback Stalls Before Patch Delivery in Budget-Constrained Coding Agents*，署名 `Team xiakongxin`，采用 NeurIPS 风格顶底横线抬头与单栏 5 页版式）使用 2 幅图、3 张正文表及 8 项固定版本引用，通过 Tectonic 0.17.0（原生 Unicode OpenType Latin Modern）编译退出码 0，生成 **5 页 PDF**。图1采用已确认的原生SVG模板，正文嵌入其矢量PDF导出，Markdown使用PNG预览；图2和全部科学数值保持。TeX/BibTeX 日志未出现未解析引用、Overfull/Underfull 或元数据警告（`tex_diagnostics: []`）。

全部可读文字采用两种提取和布局计数的最大值（含标题、署名、正文、图表文字/图注、全部三张表格、参考文献和页码）：

| 计数方法 | 总计 |
|---|---:|
| pdfplumber whitespace tokens | 2,509（逐页：`498 / 439 / 399 / 737 / 436`） |
| pypdf whitespace tokens | 2,971 |
| pdfplumber layout words | 2,509 |
| PDF 提取保守最大值（含参考文献） | **2,971** |
| Markdown/LaTeX 主文计数（含图内全部文字、不含参考文献） | **2,942（2,993 word tokens）** |

全部计数均严格低于 Kaggle Paper Track 3,000 词上限。

主项目最终全部5页在 `build/pages-svg-figure1-20261112/` 渲染并逐页完成目视检查：标题、署名、正文、矢量图1及其图注、图2、表1–表3、代码内联标记和全部8条参考文献均清晰完整，无裁切、重叠、溢出或缺字。伴随仓库使用相同源码和图形导出；重建PDF以交付副本的SHA256验收。

- **交付副本**：[`output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf`](output/pdf/knowing-the-bug-is-not-landing-the-fix.pdf)（444,324 字节 / 433.91 KiB）
- **SHA256**：`4f9fb0b5ef26eeecff036bf728c022b9df460b05f231fb08604431dcd454da90`
- **图1资源**：[可编辑SVG](figures/study-design-v04.svg)、[3072×2048 PNG](figures/study-design-v04.png)、[矢量PDF](figures/study-design-v04.pdf)及[导出清单](evidence/study-design-svg-v04.json)。图1 PDF文字可检索，含0个嵌入位图。
- **仓库状态**：独立伴随仓库，本地提交，尚未上传GitHub。

## 本机编译和重建

在仓库根依次执行：

```powershell
python -X utf8 scripts/build_v04_analysis.py
python -X utf8 scripts/build_v04_review_analysis.py
python -X utf8 scripts/build_v04_visuals.py
python -X utf8 scripts/build_text_manuscript.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

PDF 提取与逐页渲染核验命令：

```powershell
python -X utf8 scripts/verify_pdf.py --poppler pdftoppm --tag svg-figure1-20261112
```

历史PDF保存在主项目归档中。依赖版本与轻量重建范围见[复核指南](supplement/reproducibility.md)。

当前发布版PDF固定构建时间戳 `SOURCE_DATE_EPOCH=1794441600`（2026-11-12 UTC），用于新克隆重建时复现同一PDF字节。该时间戳是发布构建元数据。

默认图表构建重建图1 SVG并校验仓库内提供的PNG/PDF指纹，图2继续使用Matplotlib 3.11.1。只有修改图1后重新导出PNG/PDF才需要Node.js与Playwright/Chromium；步骤见[复核指南](supplement/reproducibility.md)。
