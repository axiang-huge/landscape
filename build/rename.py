#!/usr/bin/env python3
"""把 photos/ 里的哈希文件名改成对应地点的中文名。
文件名用「显示名」而非检索词——显示名天然唯一，检索词会撞车
（例如「泸沽湖 · 尼塞 / 小落水」和「泸沽湖 + 香格里拉」检索词都是泸沽湖）。
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PH = os.path.join(ROOT, "photos")
LOCAL = os.path.join(HERE, "photos_local.json")

data = json.load(open(LOCAL, encoding="utf-8"))

BAD = re.compile(r'[/\\:*?"<>|]')          # 文件系统保留字符


def safe(name):
    s = BAD.sub("_", name)                  # 斜杠等换成下划线
    s = re.sub(r"\s+", "", s)               # 去掉空格
    s = s.strip("._")
    return s or "unnamed"


# 先算目标名并处理重名
targets, used = {}, {}
for name in data:
    base = safe(name)
    if base in used:
        used[base] += 1
        base = f"{base}-{used[base]}"
    else:
        used[base] = 1
    targets[name] = base

renamed, skipped, missing = 0, 0, []
for name, v in data.items():
    base = targets[name]
    for key, suf in (("s", "s"), ("l", "l")):
        old = os.path.join(ROOT, v[key])
        new = os.path.join(PH, f"{base}_{suf}.jpg")
        if os.path.abspath(old) == os.path.abspath(new):
            skipped += 1
        elif os.path.exists(old):
            if os.path.exists(new):
                os.remove(new)
            os.rename(old, new)
            renamed += 1
        else:
            missing.append(v[key])
            continue
        v[key] = f"photos/{base}_{suf}.jpg"

json.dump(data, open(LOCAL, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"重命名 {renamed} 个，已就位 {skipped} 个，源文件缺失 {len(missing)} 个")
for m in missing[:5]:
    print("  缺:", m)

left = [f for f in os.listdir(PH) if re.fullmatch(r"[0-9a-f]{12}_[sl]\.jpg", f)]
print("残留哈希文件:", len(left))
print("示例:", sorted(os.listdir(PH))[:4])
