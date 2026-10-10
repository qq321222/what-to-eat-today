# WorkBuddy 开发对话上下文

本文件记录本项目使用 WorkBuddy 开发的对话上下文摘要，用于核验 WorkBuddy 专项联动活动奖励条件。开发全程在 WorkBuddy 客户端内完成，由「技能匠人（skill-smith）」专家工作流驱动。

## 开发环境

- 工具：WorkBuddy（内置智能体 + 麦当劳 MCP 连接器 + skill-smith 专家包）
- 日期：2026-10-10
- 运行环境：Windows，Python 3.13（托管运行时）

## 对话与开发过程摘要

### 1. 需求提出（用户）

用户基于麦当劳 MCP 能力提出「今天吃什么」智能点餐助手创意：用户面对几十个 SKU、4 种履约方式（到店自取/得来速/麦乐送/团餐）和一堆券算不清怎么点最划算；Skill 价值在于吃透券规则做真实比价、按人数/预算/口味出搭配、算出「券后实付最低」方案，把点餐决策从约 5 分钟压缩到 30 秒。

### 2. 方案设计（WorkBuddy 规划模式）

- 枚举麦当劳 MCP 全部工具的 schema，固化 beType/beCode/orderType 传参矩阵、特调整组传参规则、价格分转元等 Gotchas。
- 经交互确认四项产品决策：全闭环（状态机式推进、每步等用户明确选择、绝不虚构下单结论）；先领券后比价；智能预筛控试算成本（≤5 次）；用户级安装。
- 产出计划文件并经用户批准。

### 3. 规格补充（用户）

用户一次性给出 8 项补充规格：首轮不追问规则（默认 1 人/人均 30-40 元/到店自取，每轮最多一个问题）、S-R 复购分支（排除积分商城订单）、触发词三级分类（主/隐式/复购/不触发）、硬确认词表（嗯/随便等模糊词不下单）、外送地址子步骤、四项口径澄清（5 次算价、先列券后领、takeWayCode 映射、gmServiceCode 来源）、错误处理专节、范围声明与脚本降级。

### 4. 制作与自检（WorkBuddy + skill-smith 工具链）

- 使用包内 skill_ops.py 完成 render → validate → preflight → package → install 全流程。
- 产出 SKILL.md（109 行）+ 7 个 references + 3 个 scripts + skill-dependencies.json。
- 实测：MCP 只读冒烟 4 项通过（now-time-info / query-my-account / query-my-coupons / order-list）；环境检查器 ready/needs_setup/unavailable 路由实测通过；combo_builder.py 实测发现 2 个缺陷（忌口过滤未生效、超预算替换在去重之后导致方案重复）并修复、新增预算带降档，回归 3 场景通过；compare_plans.py 3 场景通过。
- 如实声明未验证项：触发词三类各 5 例、复购全链路、外送地址新建、模糊确认词对话表现（需真实新会话验收）。

### 5. 交付

Skill v1.0.0 安装至用户级目录 `~/.workbuddy/skills/what-to-eat-today/`，附分发 ZIP 与使用说明（含 15 条触发测试矩阵）。

## 结论

本项目从创意、规格、编码、测试到交付全程在 WorkBuddy 内完成，符合 WorkBuddy 联动开发的认定条件。
