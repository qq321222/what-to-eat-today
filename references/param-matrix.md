# 传参矩阵

每次调用麦当劳 MCP 前核对本文件。beCode 必须与 storeCode 来自同一次查询返回，禁止跨查询拼凑。

## beType / orderType / beCode / addressId 矩阵

| beType | 履约方式 | orderType | beCode | addressId | 门店来源 |
|---|---|---|---|---|---|
| 1 | 到店自取 | 1 | 不传（传了会报错） | 不传 | query-nearby-stores(beType=1, searchType) |
| 5 | 得来速 | 1 | 必传，来自 query-nearby-stores 返回 | 不传 | query-nearby-stores(beType=5, searchType) |
| 2 | 麦乐送 | 2 | 必传，来自 delivery-query-stores 返回 | 必传 | delivery-query-stores(beType=2, addressId) |
| 6 | 团餐 | 2 | 必传，来自 delivery-query-stores 返回 | 必传 | delivery-query-stores(beType=6, addressId) |

addressId 来源：delivery-query-addresses（已有地址）或 delivery-create-address（新建地址，需城市/联系人/手机号/地址/门牌号五要素）。

query-nearby-stores 参数：beType 必传；searchType=1 查收藏餐厅（默认），searchType=2 按位置搜索（此时 city 与 keyword 必填）。

## 各工具共用的场景参数

- storeCode：必填，全程使用同一门店。
- orderType / beType / beCode：按上表。到店自取场景 beCode 是无效参数，不要传，传了会报错。
- reservationDate：预约场景必传，格式 yyyy-MM-dd HH:mm；非预约场景一律不传。query-meals、query-store-coupons、calculate-price、create-order 四处同传或同不传，不得不一致。

## 特调 modification 传参规则（来自 query-meal-detail）

对包含 unselectedKey 的特调组，该组内所有特调项都必须传入 values：

- 用户选中的特调项：key = query-meal-detail 返回的 selectedKey。
- 用户未选中的特调项：若该项 unselectedKey 不为空，key = unselectedKey，也必须传入。

正确示例（选中去冰可乐、未选加冰但仍整组传入）：

```json
{
  "productCode": "SKU123",
  "quantity": 1,
  "modification": {
    "values": [
      {"code": "OPT_NO_ICE", "key": "selectedKey的值", "quantity": 1},
      {"code": "OPT_ICE", "key": "unselectedKey的值", "quantity": 1}
    ]
  }
}
```

错误示例：只传选中项、漏传带 unselectedKey 的未选中项——会导致下单失败或价格错算。

## takeWayCode（取餐方式）

- 仅 orderType=1（到店自取、得来速）必传；orderType=2 不传。
- 取值来自 calculate-price 返回的 data.takeWayList[].code。
- S7 下单时让用户从 takeWayList 选取；S1 已确定 beType=5（得来速）时直接取列表中对应项，不再重复询问。
- create-order 与最后一次 calculate-price 必须使用同一门店与取餐方式。

## gmServiceCode（团餐助餐服务）

- 来源：query-meal-assistance(storeCode, orderType=2, beType=6, beCode) 返回。
- 仅 beType=6 场景传递；该场景下 calculate-price 与 create-order 均必传。

## 价格与单位

- calculate-price 返回的价格字段单位为分；任何展示前除以 100 转为元。
- 菜单价（query-meals）同样按分处理，组装脚本输入时原样传 priceCent。

## 组参前检查清单

1. beType 与门店来源工具是否匹配（到店走 query-nearby-stores，外送走 delivery-query-stores）。
2. 除到店自取外，beCode 是否来自最近一次门店查询。
3. orderType=2 时 addressId 是否已缓存。
4. 预约场景 reservationDate 是否四处一致。
5. 团餐场景 gmServiceCode 是否已获取。
