#!/usr/bin/env python3
"""从菜单与约束生成候选搭配。

通过标准输入接收 JSON，标准输出返回 JSON。仅使用 Python 标准库；
无网络、无子进程、无文件读写。
输入结构见 references/combo-strategy.md。
"""

import json
import sys

MAX_COMBOS = 5
BUDGET_BUFFER = 1.1

# 人均预算带（单位：分）：下限、上限（None 为开区间）、结构模板列表
BANDS = [
    (0, 2000, [["小食"]]),
    (2000, 3000, [["汉堡", "小食"], ["汉堡", "饮料"]]),
    (3000, 4000, [["汉堡", "小食", "饮料"]]),
    (4000, 5000, [["汉堡", "小食", "小食", "饮料"]]),
    (5000, None, [["汉堡", "小食", "小食", "小食", "饮料"]]),
]
DEFAULT_BAND_NOTE = "未提供预算，按人均 30-40 元默认带处理"

LETTERS = "ABCDE"


def die(message: str) -> None:
    """输入非法：向标准错误输出原因并以退出码 2 结束。"""
    sys.stderr.write(f"combo_builder 输入错误：{message}\n")
    raise SystemExit(2)


def load_input() -> dict:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        die(f"标准输入不是合法 JSON：{exc}")
    if not isinstance(data, dict):
        die("输入根节点必须是对象")
    return data


def parse_meals(raw) -> list:
    if not isinstance(raw, list) or not raw:
        die("meals 必须是非空数组")
    meals = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        code = str(item.get("code", "")).strip()
        name = str(item.get("name", "")).strip()
        price = item.get("priceCent")
        category = str(item.get("category", "")).strip()
        tags = item.get("tags", [])
        if not code or not name or not isinstance(price, (int, float)) or price < 0:
            die(f"meals[{index}] 缺少 code/name 或 priceCent 非法")
        if not isinstance(tags, list):
            tags = []
        meals.append({
            "code": code,
            "name": name,
            "priceCent": int(price),
            "category": category,
            "tags": [str(tag) for tag in tags],
        })
    if not meals:
        die("meals 中没有可用商品")
    return meals


def parse_positive_int(data: dict, key: str, default: int) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < (1 if key == "people" else 0):
        die(f"{key} 必须是合法整数")
    return value


def parse_preferences(data: dict) -> dict:
    prefs = data.get("preferences", {})
    if prefs is None:
        prefs = {}
    if not isinstance(prefs, dict):
        die("preferences 必须是对象")
    avoid = prefs.get("avoid", [])
    if not isinstance(avoid, list):
        die("preferences.avoid 必须是数组")
    return {
        "meat": str(prefs.get("meat", "") or ""),
        "spicy": str(prefs.get("spicy", "") or ""),
        "drink": str(prefs.get("drink", "") or ""),
        "avoid": [str(k) for k in avoid if str(k).strip()],
    }


def drop_avoided(meals: list, prefs: dict) -> tuple:
    """按名称关键词剔除忌口商品，返回过滤后菜单与剔除说明。"""
    kept, dropped = [], []
    for meal in meals:
        if any(keyword and keyword in meal["name"] for keyword in prefs["avoid"]):
            dropped.append(meal["name"])
        else:
            kept.append(meal)
    return kept, dropped


def matches_tags(meal: dict, prefs: dict, slot: str) -> bool:
    tags = set(meal["tags"])
    if slot == "汉堡":
        if prefs["meat"] and prefs["meat"] not in tags:
            return False
        if prefs["spicy"]:
            if prefs["spicy"] == "不辣" and "辣" in tags:
                return False
            if prefs["spicy"] == "辣" and "辣" not in tags:
                return False
    if slot == "饮料" and prefs["drink"] and prefs["drink"] not in tags:
        return False
    return True


def category_pool(meals: list, prefs: dict, category: str) -> list:
    pool = [m for m in meals if m["category"] == category and matches_tags(m, prefs, category)]
    if not pool:
        pool = [m for m in meals if m["category"] == category]
    return sorted(pool, key=lambda m: (m["priceCent"], m["name"]))


def build_variant(structure: list, meals: list, prefs: dict, people: int, rotate: int, notes: list) -> dict | None:
    used_codes: set = set()
    items = []
    for slot in structure:
        pool = category_pool(meals, prefs, slot)
        if not pool:
            notes.append(f"菜单中没有「{slot}」类商品，已跳过该结构位")
            continue
        candidates = [m for m in pool if m["code"] not in used_codes] or pool
        pick = candidates[rotate % len(candidates)]
        used_codes.add(pick["code"])
        items.append({"productCode": pick["code"], "name": pick["name"],
                      "quantity": people, "priceCent": pick["priceCent"]})
    if not items:
        return None
    total = sum(item["priceCent"] * item["quantity"] for item in items)
    return {"items": items, "total": total}


def band_label_of(band_index: int) -> str:
    low, high, _ = BANDS[band_index]
    if high is None:
        return "人均50元以上带"
    return f"人均{low // 100}-{high // 100}元带"


def current_band_index(avg_cent: int) -> int:
    for index, (low, high, _) in enumerate(BANDS):
        if avg_cent >= low and (high is None or avg_cent < high):
            return index
    return 0


def fit_budget(variant: dict | None, structure: list, band_index: int,
               meals: list, prefs: dict, people: int, budget_cent: int, notes: list) -> tuple:
    """超预算时先换同带最低价组合，再逐级降档预算带；返回(组合, 结构, 带序号)。"""
    if not budget_cent or variant is None or variant["total"] <= budget_cent * BUDGET_BUFFER:
        return variant, structure, band_index
    cheapest = build_variant(structure, meals, prefs, people, 0, notes)
    if cheapest and cheapest["total"] < variant["total"]:
        variant = cheapest
        notes.append("超出预算 10%，已替换为更低价组合")
    if variant["total"] > budget_cent * BUDGET_BUFFER:
        for lower in range(band_index - 1, -1, -1):
            _, _, alt_structures = BANDS[lower]
            for alt in alt_structures:
                candidate = build_variant(alt, meals, prefs, people, 0, notes)
                if candidate and candidate["total"] <= budget_cent * BUDGET_BUFFER:
                    notes.append(f"已降档至{band_label_of(lower)}以贴合预算")
                    return candidate, alt, lower
    return variant, structure, band_index


def main() -> int:
    data = load_input()
    meals = parse_meals(data.get("meals"))
    people = parse_positive_int(data, "people", 1)
    budget_cent = parse_positive_int(data, "budgetCent", 0)
    prefs = parse_preferences(data)

    notes: list = []
    meals, dropped = drop_avoided(meals, prefs)
    if dropped:
        notes.append("已按忌口剔除：" + "、".join(dropped))
    avg = budget_cent // people if budget_cent and people else 0
    if avg == 0:
        notes.append(DEFAULT_BAND_NOTE)
        avg = 3500
    band_index = current_band_index(avg)
    structures = BANDS[band_index][2]

    combos = []
    seen = set()
    for structure in structures:
        for rotate in range(2):
            variant = build_variant(structure, meals, prefs, people, rotate, notes)
            if variant is None:
                continue
            variant, structure_used, band_used = fit_budget(
                variant, structure, band_index, meals, prefs, people, budget_cent, notes)
            key = frozenset((item["productCode"], item["quantity"]) for item in variant["items"])
            if key in seen:
                continue
            seen.add(key)
            if budget_cent and variant["total"] > budget_cent * BUDGET_BUFFER:
                notes.append(f"组合 {variant['total'] / 100:.2f} 元超出预算，请用户确认或调整")
            main_item = next((item for item in variant["items"] if item["quantity"] == people), variant["items"][0])
            combos.append({
                "name": f"方案{LETTERS[len(combos)]}·{main_item['name']}{people}人次",
                "items": variant["items"],
                "estTotalCent": variant["total"],
                "perPersonCent": variant["total"] // people,
                "structureNote": "+".join(structure_used) + f"（{band_label_of(band_used)}）",
            })
            if len(combos) >= MAX_COMBOS:
                break
        if len(combos) >= MAX_COMBOS:
            break

    if not combos:
        notes.append("过滤后无可用商品，无法生成搭配")
    print(json.dumps({"combos": combos, "notes": notes}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
