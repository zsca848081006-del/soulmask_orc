import csv
import json
import re

CSV_PATH = "../tianfuzongbiaoxin2.csv"
OUT_PATH = "data/talents.json"


def extract_nsloctext(raw: str) -> str:
    if not raw:
        return ""
    m = re.search(r'"([^"]+)"\)$', raw)
    if m:
        return m.group(1)
    return raw.strip()


def main():
    talents = {}

    with open(CSV_PATH, "r", encoding="utf-16") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_raw = row.get("Title", "").strip()
            desc_raw = row.get("Desc", "").strip()
            star_raw = row.get("Star", "").strip()

            if not name_raw:
                continue

            name = extract_nsloctext(name_raw)
            if not name:
                continue

            desc = extract_nsloctext(desc_raw)
            if not desc:
                continue

            try:
                star = int(star_raw)
            except ValueError:
                star = 0

            star_key = str(star)

            if name not in talents:
                talents[name] = {}
            talents[name][star_key] = desc

    result = {}
    for name in sorted(talents):
        result[name] = {k: talents[name][k] for k in sorted(talents[name], key=int)}

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total_names = len(result)
    total_entries = sum(len(v) for v in result.values())
    lvl1 = sum(1 for v in result.values() if "1" in v)
    lvl2 = sum(1 for v in result.values() if "2" in v)
    lvl3 = sum(1 for v in result.values() if "3" in v)
    print(f"生成 {OUT_PATH}，{total_names} 个天赋，{total_entries} 条等级数据")
    print(f"  1级: {lvl1}, 2级: {lvl2}, 3级: {lvl3}")


if __name__ == "__main__":
    main()
