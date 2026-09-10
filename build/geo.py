#!/usr/bin/env python3
"""把 DataV 中国省界 GeoJSON 简化成可内联的紧凑格式。
输出：build/china.json  —— {"p":[[name,[[ [x,y],... ],...]],...]}
坐标保留 2 位小数（约 1km 精度），并做距离抽稀。
"""
import json, urllib.request, math, os

SRC = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "cn_raw.json")
OUT = os.path.join(HERE, "china.json")

if not os.path.exists(RAW):
    urllib.request.urlretrieve(SRC, RAW)

gj = json.load(open(RAW, encoding="utf-8"))


def rdp(pts, eps):
    """Ramer–Douglas–Peucker 抽稀"""
    if len(pts) < 3:
        return pts
    x1, y1 = pts[0]
    x2, y2 = pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    imax, dmax = 0, 0.0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n if n else math.hypot(x0 - x1, y0 - y1)
        if d > dmax:
            imax, dmax = i, d
    if dmax > eps:
        return rdp(pts[: imax + 1], eps)[:-1] + rdp(pts[imax:], eps)
    return [pts[0], pts[-1]]


def rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in c]
    return []


out, total_before, total_after = [], 0, 0
for f in gj["features"]:
    name = f["properties"]["name"]
    geom = f.get("geometry")
    if not geom:
        continue
    rs = []
    for r in rings(geom):
        total_before += len(r)
        s = rdp([[p[0], p[1]] for p in r], 0.045)
        if len(s) < 4:
            continue
        s = [[round(p[0], 2), round(p[1], 2)] for p in s]
        # 去掉抽稀后产生的重复点
        d = [s[0]]
        for p in s[1:]:
            if p != d[-1]:
                d.append(p)
        if len(d) >= 4:
            rs.append(d)
            total_after += len(d)
    # 只保留面积够大的环，去掉细碎小岛以控制体积（南海诸岛单独保留）
    rs.sort(key=lambda r: -len(r))
    rs = [r for r in rs if len(r) >= 6][:14]
    if rs:
        out.append([name, rs])

json.dump({"p": out}, open(OUT, "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print(f"provinces={len(out)}  points {total_before} -> {total_after}  "
      f"size={os.path.getsize(OUT)/1024:.0f}KB")
