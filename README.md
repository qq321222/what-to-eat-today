<div align="center">
🍔 今天吃什么 · 麦当劳智能点餐助手
基于麦当劳 MCP 的全流程点餐决策 Skill
选店 → 搭配 → 领券 → 真实比价 → 下单 → 支付跟踪，一条链路全包，算出券后实付最低方案
Skill
Version
MCP
Python
✨ 核心特性 · 🎬 使用示例 · 🚀 本地部署 · 📁 仓库结构 · ⚙️ 工作原理
</div>
麦当劳程序员节创意开发大赛参赛作品（非麦当劳官方产品）
💡 为什么做这个
在麦当劳点餐时，你是否也遇到过这些情况——
- 菜单几十个 SKU，不知道怎么搭配最划算
- 卡包里躺着一堆券，不知道哪张能用、怎么组合最省
- 到店、得来速、外送、团餐 4 种方式，参数不对就下单失败
- 反复对比试错，一顿饭的点单决策要花 5 分钟以上
这个 Skill 把整个决策过程交给智能体：吃透券规则做真实比价、按人数/预算/口味生成搭配、算出券后实付最低方案——点餐决策从约 5 分钟压缩到 30 秒。
✨ 核心特性
特性
说明
🧮 真实比价引擎
以门店维度可用券（query-store-coupons）为唯一权威数据源，硬过滤（有效期/品类/门槛/履约）+ 打分公式 score = E × R × (0.6 + 0.4T) 预筛候选，再逐候选真实试算，全流程算价预算 ≤5 次
🛍️ 四种履约全覆盖
到店自取（beType=1）· 得来速（5）· 麦乐送（2）· 团餐（6，含满减满折促销叠加与助餐服务）
🤖 状态机式交互
首轮不追问——收到意图立即给方案，每轮最多补一个问题；硬确认词表防止「嗯 / 随便」误触下单
🔁 一键复购
「再点一次上次那个」自动还原历史订单明细，按本次门店与履约重新试算后下单
🚫 绝不虚构
任何价格、订单状态均来自真实 MCP 调用；下单结论只复述 create-order 真实返回
🛡️ 依赖检查与降级
内置只读环境检查器（ready / needs_setup / partial / unavailable 四态路由）；脚本失败自动降级为人工推理并声明「估算价」
适合谁用： 纠结「怎么点最划算」的普通用户 · 多人拼餐预算有限的学生/上班族 · 需要团餐搭配与满减凑单的企业订餐人 · 开车路过想用得来速快速取餐的用户
🎬 使用示例
用户：帮我点麦当劳
助手：按默认先给你配一套：1 人、人均 30-40 元、到店自取——
     板烧鸡腿堡套餐 + 小食，预估 ¥35 左右（最终以门店实价和券后价为准）。
     想怎么吃？①到店自取 ②得来速 ③麦乐送 ④团餐

用户：麦乐送，两个人，预算 80，不辣
助手：（选定门店 → 展示可领券并征得同意 → 真实试算 → 输出比价表）

     【比价结果】XX 餐厅 · 麦乐送 · 试算时间 15:11

     | 方案 | 原价 | 用券 | 券后实付 | 省 | 折扣 |
     |------|------|------|----------|----|------|
     | ⭐方案A·板烧双人次 | ¥76.50 | 板烧立减券(满59减15) | ¥61.50 | ¥15.00 | 8折 |
     | 方案B·麦辣双人次 | ¥68.00 | 无可用券 | ¥68.00 | — | — |

     最划算：方案A，券后实付 ¥61.50

用户：就这套
助手：（复述券后价/门店/明细/地址四项硬确认 → 真实下单 → 引导扫码支付并跟踪状态）

用户：再点一次上次那个
助手：（自动还原最近一笔订单 → 按当前门店重新试算 → 硬确认 → 下单）
<b>💬 更多触发方式（点击展开）</b>
  - 直接触发：「麦当劳有什么优惠」「麦乐送点个汉堡」「找个得来速」「麦当劳团餐怎么点」
  - 隐式触发：「巨无霸多少钱」「中午吃什么」「板烧套餐来一份」
  - 复购触发：「跟昨天一样」「再点一次上次那个」
  - 不触发：竞品（肯德基/必胜客）、菜谱类（汉堡怎么做）、泛餐饮推荐（附近有什么好吃的）
🚀 本地部署
提供两种安装方式，按你的使用环境选择其一：
- 方式 A · 通过 WorkBuddy 安装（推荐）——开箱即用，连接器托管授权，全程 5 分钟
- 方式 B · 通用本地环境安装（不依赖 WorkBuddy）——适用于任意支持 MCP 协议的客户端/智能体
📦 方式 A：通过 WorkBuddy 安装（推荐）
前置条件
依赖
必需
用途
WorkBuddy 客户端
✅
Skill 宿主
麦当劳 MCP 连接器（mcd-mcp）
✅
门店/菜单/券/试算/下单的全部真实数据
Python 3.10+
可选
搭配生成与比价汇总脚本；缺失时自动降级为人工推理，不影响主流程
第 1 步：获取项目
git clone https://github.com/qq321222/what-to-eat-today.git
或到仓库页点击绿色 <> Code 按钮 → Download ZIP，解压备用。
第 2 步：安装到 WorkBuddy（用户级）
将仓库中的 SKILL.md、skill-dependencies.json、references/、scripts/ 四项复制到 WorkBuddy 用户级技能目录（文件夹名必须为 what-to-eat-today）：
# Windows
C:\Users\<用户名>\.workbuddy\skills\what-to-eat-today\

# macOS / Linux
~/.workbuddy/skills/what-to-eat-today/
安装后的目录结构应为：
what-to-eat-today/
├── SKILL.md
├── skill-dependencies.json
├── references/   (7 个 .md)
└── scripts/      (3 个 .py)
第 3 步：配置麦当劳 MCP 连接器
1. 打开 WorkBuddy 对话窗口左下角 「+」连接器菜单
2. 搜索 「麦当劳」，安装麦当劳 MCP 连接器
3. 按提示完成麦当劳账号授权
4. 在连接器管理页对 mcd-mcp 点击 「信任」 以启用
第 4 步：验证安装
新开一个 WorkBuddy 会话，对助手说：
帮我点麦当劳
能返回真实的时间判断与初步搭配方案，即部署成功。如需先确认依赖就绪，可运行只读环境检查器：
python scripts/check_environment.py --probe-results <宿主提供的探测结果.json>
🧰 方式 B：通用本地环境安装（不依赖 WorkBuddy）
本 Skill 的全部规则沉淀在 Markdown 文件中、全部脚本为纯标准库 Python，因此可以直接接入任意支持 MCP 协议的客户端或自建智能体。
前置条件
依赖
必需
用途
任意 MCP 客户端 / 智能体运行时
✅
宿主（如自建 Agent、其他 MCP 宿主应用）
mcd-mcp 服务访问能力
✅
门店/菜单/券/试算/下单数据（服务端点见下）
Python 3.10+
可选
搭配与比价脚本；缺失时按 SKILL.md 规则人工推理降级
第 1 步：获取项目（同方式 A）
第 2 步：注册 mcd-mcp 服务端点
在你的 MCP 客户端配置中注册麦当劳 MCP（streamablehttp）：
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn"
    }
  }
}
账号授权方式取决于所用客户端对 streamablehttp 协议的支持；请勿在配置中明文存放凭据。
第 3 步：加载 Skill 规则
将 SKILL.md 作为智能体的系统指令/规则文件加载（或粘贴到系统提示词），references/ 下的 7 个文件按 SKILL.md 中「资源加载索引」的时机按需提供。Skill 的触发方式、状态机推进、硬确认闸门等行为由这些规则驱动，与宿主无关。
第 4 步：接入脚本（可选，推荐）
智能体通过标准输入/输出调用脚本，获得自动化的搭配生成与比价汇总：
# 搭配生成：输入菜单+约束 JSON，输出候选搭配
echo '{"meals": [...], "people": 2, "budgetCent": 8000, "preferences": {...}}' | python scripts/combo_builder.py

# 比价汇总：输入各候选试算结果 JSON，输出 Markdown 比价表
echo '{"candidates": [...], "meta": {...}}' | python scripts/compare_plans.py
脚本仅使用 Python 标准库，无网络、无子进程、无文件读写，可离线运行。
第 5 步：验证
对智能体说 「帮我点麦当劳」，能返回真实的时间/门店数据并按状态机推进，即部署成功。
注：方式 B 下，环境检查器中依赖 WorkBuddy 配置路径的检查项（如 ~/.workbuddy/mcp.json）不适用，请以所用 MCP 客户端的连通性验证为准。
🔧 常见问题排查
现象
处理
说了触发词但没进入点餐流程
方式 A：确认文件在 ~/.workbuddy/skills/what-to-eat-today/，重启或新开会话；方式 B：确认 SKILL.md 已正确加载进系统指令
提示 mcd-mcp 不可用
方式 A：检查连接器「已安装、已授权、已信任」；方式 B：检查 MCP 客户端中 https://mcp.mcd.cn 注册与授权
提示 Python 缺失或脚本失败
属可选依赖，主流程不受影响；安装 Python 3.10+ 后恢复自动化
查不到附近门店
提供城市或商圈关键词，或先在麦当劳 APP 收藏常用门店
📁 仓库结构
├── SKILL.md                  # Skill 主入口：触发路由、六条铁律、状态机速查、资源索引
├── skill-dependencies.json   # 依赖清单：mcd-mcp / Python，检查项与降级映射
├── references/
│   ├── state-machine.md      # 9 状态 + 复购分支：调用序列、暂停点、话术、硬确认词表
│   ├── param-matrix.md       # beType/beCode/orderType/addressId 传参矩阵、特调规则
│   ├── pricing-engine.md     # 券预筛、打分公式、5 次试算预算管制、比价呈现
│   ├── combo-strategy.md     # 人均预算带、口味标签映射、脚本输入输出契约
│   ├── group-meal.md         # 团餐链路：助餐服务、满减满折、凑单建议
│   ├── order-ops.md          # 下单逐字段核对、支付跟踪、错误处理
│   └── setup-guide.md        # 依赖配置、验证、轮换与撤销
├── scripts/
│   ├── combo_builder.py      # 搭配生成（纯标准库，stdin JSON → stdout JSON）
│   ├── compare_plans.py      # 比价汇总（分转元、排序、Markdown 比价表）
│   └── check_environment.py  # 只读环境检查器（四态路由）
├── README.md                 # 本文件
├── CONTEST_DECLARATION.md    # 参赛声明（官方文件，内容不可修改）
├── MCP_INTEGRATION.md        # 麦当劳 MCP 集成说明
└── workbuddy.md              # WorkBuddy 开发对话上下文
⚙️ 工作原理
意图识别（now-time-info 判时段）
  → 履约确定 beType → 门店链路查询
    → query-meals 取菜单 → combo_builder.py 生成搭配
      → 列券确认 → auto-bind-coupons 领券
        → query-store-coupons → 硬过滤 + 打分预筛
          → calculate-price ×≤4 候选试算（预算 ≤5 次）
            → compare_plans.py 汇总比价表 → 用户选定
              → 特调/明细确认 → 最终复核 ×1
                → 硬确认四项 → create-order → query-order 支付跟踪
三条核心纪律：
1. 比价唯一权威数据源是 query-store-coupons——卡包券（query-my-coupons）不做门店/渠道/履约校验，不得承诺可用
2. 每次调 MCP 前核对传参矩阵——beCode 必须与 storeCode 同源，到店自取不传 beCode，价格单位为分
3. 全流程状态机推进——每个状态结束停下等用户确认，下单前必须通过硬确认词表
详见 MCP_INTEGRATION.md。
🧪 质量与实测
- ✅ 结构校验、静态预检通过（0 高危）
- ✅ MCP 只读冒烟实测通过：服务器时间、积分账户、卡包券、历史订单均可真实读取
- ✅ 环境检查器 ready / needs_setup / unavailable 路由实测通过
- ✅ 脚本经多场景实测（正常/边界/非法输入/口味过滤/忌口/预算降档），发现并修复 2 个缺陷后回归通过
- ⚠️ 如实声明未验证项：触发词全量对话表现、复购全链路、外送地址新建（需安装后真实新会话验收）
⚠️ 免责声明
本项目为参赛独立开发作品，非麦当劳官方产品。所有餐品信息、价格、优惠及供应状态以麦当劳官方渠道（APP/小程序）实时结果为准；输出内容不构成医疗、营养等专业建议。详见 CONTEST_DECLARATION.md。
<div align="center">
Made with 🍟 using WorkBuddy + McDonald's MCP
</div>
