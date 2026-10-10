# 团餐场景（beType=6）

企业团餐有独立链路与专属优惠维度。参数细则见 `references/param-matrix.md`。

## 链路

1. delivery-query-addresses → 用户选定或新建地址 → addressId。
2. delivery-query-stores(beType=6, addressId) → 可配送门店 + beCode → 用户选店。
3. query-meal-assistance(storeCode, orderType=2, beType=6, beCode)：查当前门店可用助餐服务 → 用户选择 → 取 gmServiceCode。
4. query-promotions(storeCode, beCode, orderType=2, beType=6)：读取满减（promotionType=31）/满折（promotionType=33）规则原始数据。返回结构含 promotionId、promotionType、ruleCategory、beTypes、startTime/endTime、gmServiceCode、products、ruleDetail；products 中 type=1 包含、2 不包含、3 全部。时间无效或与在售餐品无交集的规则已被服务端过滤。
5. calculate-price / create-order 必传 gmServiceCode。

## 官方预算带（团餐搭配）

- 20 元以下：小食
- 20-30 元：汉堡+小食 或 汉堡+饮料
- 30-40 元：汉堡+薯条/小食+饮料
- 40-50 元：汉堡+薯条+小食+饮料
- 50 元以上：丰富组合，优先不重复小食

团餐菜单可能不含常规单品，必须以 query-meals(beType=6) 返回为准。

## 比价处理

- 满减/满折规则作为独立优惠维度，与券并行生成候选进入比价引擎，不假设可叠加，以 calculate-price 实际返回为准。
- 满减场景优先做「凑单到下一档门槛」建议：如满 100 减 20、当前合计 95 元时，给出 +5 元凑单候选供用户选择。
- 券与促销规则的候选均消耗试算预算，仍受 5 次管制约束，预筛时优先 score 高且门槛贴近的规则。

## 异常

- 门店不支持团餐（delivery-query-stores 无返回）→ 提示换门店或改走麦乐送流程。
- query-meal-assistance 失败 → 告知无法获取助餐服务，询问是否继续（无法继续则停止下单，如实说明）。
- query-promotions 失败 → 跳过满减满折维度，仅按券比价并向用户声明。
