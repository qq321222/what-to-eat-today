# 下单与支付

## create-order 逐字段核对清单

调用前逐项核对，参数与最后一次 calculate-price 完全一致：

| 字段 | 要求 |
|---|---|
| storeCode | 与试算同门店 |
| orderType | 1-到店（自取+得来速），2-外送（麦乐送+团餐） |
| beType | 1/2/5/6，与链路一致 |
| beCode | 除到店自取(beType=1)外必传，与试算同值 |
| addressId | orderType=2 必传（来自 delivery-query-addresses 或 delivery-create-address） |
| gmServiceCode | beType=6 必传（来自 query-meal-assistance） |
| takeWayCode | orderType=1 必传，取自最后一次 calculate-price 返回的 takeWayList[].code |
| items | productCode/quantity 与试算一致；特调按整组规则（selectedKey/unselectedKey）；couponId/couponCode 为选中方案的券 |
| roundList | 套餐子项，与试算一致 |
| withOrder | 随单购商品（来自 query-meals），与试算同口径 |
| remark | ≤50 字，仅 orderType=2 引导填写（如「无接触配送」） |
| needTableware | 与试算同口径 |
| reservationDate | 预约场景必传，格式 yyyy-MM-dd HH:mm，与试算一致 |

价格在试算与下单之间发生变化时，不调用 create-order，回到 S7 硬确认闸门重新确认。

## 下单后

create-order 成功后只复述真实返回（订单号等），引导用户：「您可以通过支付链接扫码或者打开麦当劳 APP 完成支付，支付完成后请回复『支付完成』或『支付失败』，会帮您查询最新的订单状态。」然后停住，不臆断支付状态。

## 支付跟踪

- 用户回复后 query-order(orderId) 查最新状态。
- 支付成功：报告状态，提醒取餐码/配送信息；可顺带提示满意度奖券（query-survey-coupon，orderId 用真实订单号，不做猜测）。
- 支付失败：二选一——继续等待重付，或取消订单。取消先问原因：cancel-order(orderId, cancelReasonCode)，原因码 1=改主意了、2=重复下单、3=点错了/点多了/点少了、4=地址/电话填错了、5=送达时间选错了、-1=其它原因。
- 历史订单查询走 order-list（餐品订单）；mall-order-list 是积分商城订单，与餐品复购无关。

## 错误处理

| 场景 | 处理 |
|---|---|
| 无收藏门店 | 改 query-nearby-stores searchType=2 按城市+关键词搜索，告知「按你所在城市搜索」 |
| 搜索无结果 | 明确说「没找到门店」，请用户提供城市/商圈关键词；禁止虚构门店 |
| 券不可用（calculate-price 校验失败） | 该方案标注「券不可用」，回退无券价并提示用户 |
| 门店不支持所选履约方式 | 提示换门店或换履约方式 |
| create-order 调用失败 | 如实报告错误原因，不虚构下单结果；引导稍后重试或改用麦当劳 APP，之后重新走硬确认 |
| 外送地址不可配送（delivery-query-stores 无返回） | 提示地址超出配送范围，建议更换地址或改到店自取 |
