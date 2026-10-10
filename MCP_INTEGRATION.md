# 麦当劳 MCP 集成说明

## 使用的 MCP Server

| 项目 | 内容 |
|---|---|
| Server 名称 | mcd-mcp |
| 协议 | MCP（streamablehttp） |
| 服务端点 | https://mcp.mcd.cn |
| 认证方式 | WorkBuddy 连接器托管的账号授权（凭据不落盘到项目，配置文件仅由平台管理） |
| 官方主页 | https://www.mcdonalds.com.cn |

## 使用的 MCP Tool 与业务价值

### 履约与门店（消灭履约试错成本）

| Tool | 用途 | 业务价值 |
|---|---|---|
| `query-nearby-stores` | 到店自取（beType=1）/ 得来速（beType=5）门店查询，收藏优先、城市+关键词兜底 | 不同履约方式返回不同字段（beCode），Skill 固化配对规则避免参数错配 |
| `delivery-query-addresses` / `delivery-create-address` | 外送地址查询与新建 | 复用已有地址，缺地址时引导补齐五要素 |
| `delivery-query-stores` | 麦乐送（beType=2）/ 团餐（beType=6）可配送门店 | 地址→门店→beCode 链路一次打通 |

### 商品与搭配

| Tool | 用途 | 业务价值 |
|---|---|---|
| `query-meals` | 门店在售餐品与随单购 | 搭配的真实数据源；团餐必须以 beType=6 菜单为准 |
| `query-meal-detail` | 商品详情与特调（modification） | 特调整组传参规则（selectedKey/unselectedKey）固化，避免下单失败 |
| `list-nutrition-foods` | 餐品营养成分 | 为「指定热量搭配」等扩展预留 |

### 券与比价（核心价值）

| Tool | 用途 | 业务价值 |
|---|---|---|
| `available-coupons` | 麦麦省可领券列表（面额/门槛/有效期/适用范围） | 比价前列券，未展示不得领取 |
| `auto-bind-coupons` | 一键领取全部可领券 | 用户确认后执行，保证比价基数完整 |
| `query-my-coupons` | 卡包券展示 | 仅展示；因不做门店/渠道/履约校验，Skill 明确禁止以其作为比价依据 |
| `query-store-coupons` | 指定门店+订单类型可用券 | **比价唯一权威数据源**，领券完成后调用确认新券入包 |
| `calculate-price` | 含优惠试算（支持按商品挂券） | 每个候选 1 次试算，全流程 ≤5 次预算管制；返回单位为分，展示统一分转元 |
| `query-promotions` | 团餐满减（31）/满折（33）规则 | 与券并行作为独立优惠维度参与比价，不假设叠加 |

### 下单与订单

| Tool | 用途 | 业务价值 |
|---|---|---|
| `query-meal-assistance` | 团餐助餐服务 → gmServiceCode | 团餐算价与下单的必传参数来源 |
| `create-order` | 创建真实订单（orderType=1 到店 / 2 外送） | 参数与最后一次 calculate-price 完全一致；硬确认四项后才允许调用 |
| `query-order` / `order-list` / `cancel-order` | 订单状态、历史订单、取消 | 支付跟踪与复购分支的数据源；取消前先询问原因码 |
| `query-survey-coupon` | 订单满意度奖券查询 | 支付完成后的增值提示 |

### 辅助

| Tool | 用途 |
|---|---|
| `now-time-info` | 时段判断（10:30 前早餐池）、券有效期校验、环境检查最小探测目标 |
| `query-my-account` | 积分余额（仅查询展示，本期不接流程） |
| `campaign-calendar` | 当月活动（仅查询展示，本期不接流程） |

## 调用流程

```
意图识别（now-time-info 判时段）
  → 履约确定 beType
    → 门店链路（query-nearby-stores 或 delivery-query-addresses → delivery-query-stores）
      → query-meals 取菜单 → 搭配生成（combo_builder.py）
        → available-coupons 列券 → 用户确认 → auto-bind-coupons 领券
          → query-store-coupons 确认入包 → 预筛打分 → calculate-price ×≤4 候选试算
            → compare_plans.py 汇总比价表 → 用户选定
              → query-meal-detail 特调/明细 → calculate-price 最终复核 ×1
                → 硬确认四项 → create-order → 引导扫码支付
                  → query-order 支付跟踪（失败可 cancel-order）
```

团餐分支在门店确定后插入 `query-meal-assistance`（gmServiceCode）与 `query-promotions`（满减满折）；复购分支以 `order-list` → `query-order` 还原明细后重新试算。

## 参数治理要点（踩坑沉淀）

1. **beCode 配对**：必须与 storeCode 来自同一次查询；到店自取传 beCode 会直接报错。
2. **orderType 派生**：自取/得来速 → 1，麦乐送/团餐 → 2；orderType=1 下单必传 takeWayCode（来自 calculate-price 的 takeWayList）。
3. **价格单位**：calculate-price 返回价格单位为分，任何展示前除以 100。
4. **特调整组传参**：含 unselectedKey 的特调组，未选中项也必须按 unselectedKey 传入，否则下单失败或价格错算。
5. **卡包券 ≠ 可用券**：query-my-coupons 不做门店/渠道/履约校验，不能承诺可用。

以上规则固化在 `references/param-matrix.md` 与 `references/pricing-engine.md`，属于本 Skill 的核心信息增量。
