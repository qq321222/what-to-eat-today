#!/usr/bin/env python3
"""汇总多次 calculate-price 试算结果，产出比价表。

通过标准输入接收 JSON，标准输出 Markdown 文本。仅使用 Python 标准库；
无网络、无子进程、无文件读写。
"""

import json
import sys

DELIVERY_TYPES = ("麦乐送", "团餐")


def die(message: str) -> None:
    sys.stderr.write(f"compare_plans 输入错误：{message}\n")
    raise SystemExit(2)


def yuan(cent) -> str:
    return f"{cent / 100:.2f}"


def load_candidates() -> tuple:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        die(f"标准输入不是合法 JSON：{exc}")
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list) or not data["candidates"]:
        die("输入必须包含非空 candidates 数组")
    meta = data.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}
    return data["candidates"], meta


def normalize(candidate, index: int) -> dict:
    if not isinstance(candidate, dict):
        die(f"candidates[{index}] 必须是对象")
    name = str(candidate.get("name", "")).strip() or f"方案{index + 1}"
    calc = candidate.get("calcResult")
    if not isinstance(calc, dict):
        die(f"candidates[{index}] 缺少 calcResult")
    original = calc.get("originalCent")
    payable = calc.get("payableCent")
    if not isinstance(original, (int, float)) or not isinstance(payable, (int, float)) or original < 0 or payable < 0:
        die(f"candidates[{index}] 的 originalCent/payableCent 非法")
    coupon = candidate.get("coupon")
    if coupon is not None and not isinstance(coupon, dict):
        die(f"candidates[{index}] 的 coupon 必须是对象或 null")
    return {
        "name": name,
        "original": int(original),
        "payable": int(payable),
        "coupon": coupon if isinstance(coupon, dict) else None,
        "items": candidate.get("items") if isinstance(candidate.get("items"), list) else [],
    }


def coupon_text(coupon: dict | None) -> str:
    if not coupon:
        return "无可用券"
    title = str(coupon.get("title", "")).strip() or "优惠券"
    threshold = coupon.get("thresholdCent")
    face = coupon.get("faceValueCent")
    if isinstance(face, (int, float)) and isinstance(threshold, (int, float)):
        if threshold > 0:
            return f"{title}(满{yuan(threshold)}减{yuan(face)})"
        return f"{title}(无门槛减{yuan(face)})"
    return title


def main() -> int:
    candidates, meta = load_candidates()
    plans = [normalize(candidate, index) for index, candidate in enumerate(candidates)]
    plans.sort(key=lambda plan: plan["payable"])

    best = plans[0]
    worst = plans[-1]
    store = str(meta.get("storeName", "")).strip() or "目标门店"
    fulfillment = str(meta.get("beTypeName", "")).strip() or "当前履约方式"
    calc_time = str(meta.get("calcTime", "")).strip()

    lines = [f"【比价结果】{store} · {fulfillment}"]
    if calc_time:
        lines[0] += f" · 试算时间 {calc_time}"
    lines += ["", "| 方案 | 原价 | 用券 | 券后实付 | 省 | 折扣 |", "|---|---|---|---|---|---|"]

    for rank, plan in enumerate(plans):
        saved = plan["original"] - plan["payable"]
        prefix = "⭐" if rank == 0 and len(plans) > 1 else ""
        saved_text = f"¥{yuan(saved)}" if saved > 0 else "—"
        if saved > 0 and plan["original"] > 0:
            rate = plan["payable"] / plan["original"] * 10
            rate_text = f"{rate:.1f}折".replace(".0折", "折")
        else:
            rate_text = "—"
        lines.append(
            f"| {prefix}{plan['name']} | ¥{yuan(plan['original'])} | {coupon_text(plan['coupon'])} "
            f"| ¥{yuan(plan['payable'])} | {saved_text} | {rate_text} |"
        )

    lines.append("")
    if len(plans) > 1 and worst["payable"] > best["payable"]:
        lines.append(f"最划算：{best['name']}，券后实付 ¥{yuan(best['payable'])}，比最贵候选省 ¥{yuan(worst['payable'] - best['payable'])}")
    else:
        lines.append(f"当前唯一方案：{best['name']}，券后实付 ¥{yuan(best['payable'])}")

    notes = ["以上为系统试算价，以支付页实时价为准"]
    if any(word in fulfillment for word in DELIVERY_TYPES):
        notes.append("本口径不含配送费，配送费以支付页为准")
    lines.append("注：" + "；".join(notes) + "。")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
