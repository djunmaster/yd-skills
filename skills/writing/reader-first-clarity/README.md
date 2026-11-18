# Reader-First Clarity｜读者优先的清晰表达 Skill

**版本：** 1.0  
**语言：** 中文为主，支持按用户要求使用其他语言  
**定位：** 可复用的 AI 表达优化与解释 Skill  
**核心目标：** 不降低专业准确性，而是降低读者理解专业内容的难度。

## 这个 Skill 能做什么

- 把专业、抽象、绕口的内容改写成清楚、自然、容易理解的表达。
- 解释陌生概念，主动识别专业术语，并集中整理到「新概念提示」或「术语说明」。
- 重新组织内容逻辑，减少读者一次需要处理的信息量。
- 为抽象内容补充具体例子、流程、对比或有限度的类比。
- 检查技术文档、业务分析、财务材料、产品需求、操作说明和管理汇报是否容易理解。
- 保留原文事实、数字、条件、例外和不确定性，不为了通俗而改变意思。

## 文件结构

```text
reader-first-clarity/
├── SKILL.md
├── README.md
├── manifest.json
├── agents/
│   └── openai.yaml
├── references/
│   ├── 01-reader-analysis.md
│   ├── 02-plain-language.md
│   ├── 03-terminology.md
│   ├── 04-cognitive-load.md
│   ├── 05-examples-and-analogies.md
│   ├── 06-document-modes.md
│   └── 07-quality-review.md
├── examples/
│   ├── 00-test-matrix.md
│   ├── 01-banking-cash-pool.md
│   ├── 02-api-idempotency.md
│   ├── 03-manufacturing-quality.md
│   ├── 04-cold-chain-logistics.md
│   ├── 05-health-screening.md
│   ├── 06-contract-liability.md
│   ├── 07-cybersecurity-mfa.md
│   ├── 08-statistics-correlation.md
│   ├── 09-product-requirements.md
│   ├── 10-procurement-sop.md
│   ├── 11-executive-summary.md
│   └── 12-customer-support.md
├── evals/
│   ├── 01-scoring-rubric.md
│   └── 02-regression-tests.md
└── 测试案例集_12个跨领域前后对照.md
```

## 怎么使用

本 Skill 收录在 [yd-skills 仓库](../../../README.md) 的 `skills/writing/reader-first-clarity/` 目录，可将整个目录复制到 WorkBuddy 的用户级 Skills 目录（`~/.workbuddy/skills/`）后启用。

这是一个可移植的 Markdown Skill 包，不会自动安装到 ChatGPT 的底层模型中。

**使用方法 A：上传整个 ZIP**
1. 在 ChatGPT 对话中上传本 ZIP 文件。
2. 告诉 ChatGPT：「请读取并遵循这个 Skill，帮我优化下面的内容。」
3. 如果任务较复杂，再补充读者、用途和希望保留的结构。

**使用方法 B：只使用核心文件**
1. 打开 `SKILL.md`。
2. 将其内容放入自定义 GPT 的指令，或作为对话附件。
3. 需要更严格的术语、案例或质量规则时，再提供 `references/` 对应文件。

## 最简调用语句

> 请按 Reader-First Clarity Skill 处理以下内容。保留事实和专业准确性，把正文改成没有相关专业背景的人也能理解的表达；主动识别所有专业名词，并集中放入「新概念提示」解释。重要内容请补充具体业务案例。最后检查是否有空话、抽象表述、逻辑跳跃或未经解释的术语。

## 版本原则

- 先保证事实正确，再优化表达。
- 先保证读者理解，再追求文风。
- 不把“短”当成“清楚”，不把“口语化”当成“通俗”。
- 不编造来源、案例、数据、银行能力、法律结论或技术承诺。
- 复杂任务先确认读者与用途；关键信息缺失时只问最重要的一个问题。
