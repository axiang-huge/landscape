#!/usr/bin/env python3
"""把维基共享资源的照片下载到本地 photos/，并把 data.js 指向本地路径。
每张存两个尺寸：500px（卡片）和 1280px（详情）。
"""
import hashlib, json, os, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PH = os.path.join(ROOT, "photos")
os.makedirs(PH, exist_ok=True)

photos = json.load(open(os.path.join(HERE, "photos.json"), encoding="utf-8"))
UA = {"User-Agent": "wedding-atlas/1.0 (personal trip planning; local cache)"}


def slug(name):
    """用地点名的哈希做文件名，避免中文/斜杠/空格带来的路径问题"""
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:12]


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return "cached", os.path.getsize(dest)
    delay = 2.0
    for _ in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) < 1024:
                return "too small", 0
            with open(dest, "wb") as f:
                f.write(data)
            return "ok", len(data)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(delay); delay *= 2; continue
            return f"HTTP {e.code}", 0
        except Exception as e:
            time.sleep(delay); delay *= 2
            last = str(e)[:40]
    return "failed", 0


total = 0
local = {}
items = list(photos.items())
for i, (name, v) in enumerate(items, 1):
    s = slug(name)
    got = {}
    for w, suffix in ((500, "s"), (1280, "l")):
        dest = os.path.join(PH, f"{s}_{suffix}.jpg")
        st, sz = fetch(v["u"].replace("{W}", str(w)), dest)
        total += sz
        if st in ("ok", "cached"):
            got[suffix] = f"photos/{s}_{suffix}.jpg"
        else:
            print(f"    ! {w}px {st}")
        if st == "ok":
            time.sleep(.35)
    if "s" in got and "l" in got:
        local[name] = {"s": got["s"], "l": got["l"], "f": v["f"]}
        print(f"[{i:3}/{len(items)}] ✓ {name[:24]}")
    else:
        print(f"[{i:3}/{len(items)}] ✗ {name[:24]}  下载不全，回落生成图")

json.dump(local, open(os.path.join(HERE, "photos_local.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print(f"\n本地化 {len(local)}/{len(items)} 组；photos/ 共 {total/1024/1024:.1f}MB")
