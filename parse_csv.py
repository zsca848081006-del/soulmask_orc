import csv
import json
import re
import sys

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

            if name not in talents:
                talents[name] = {"effect": desc, "star": star}
            else:
                if star > talents[name]["star"]:
                    talents[name] = {"effect": desc, "star": star}

    result = {}
    for name, info in sorted(talents.items()):
        result[name] = {"effect": info["effect"]}

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"生成 {OUT_PATH}，共 {len(result)} 个天赋")


if __name__ == "__main__":
    main()
