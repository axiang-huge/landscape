#!/usr/bin/env python3
"""把 Commons 图片 URL 统一成可变宽度的缩略图模板：
  https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/File.jpg/{W}px-File.jpg
页面按用途替换 {W}（卡片 560 / 详情 1200），避免卡片去拉几 MB 的原图。
"""
import json, os, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "photos.json")
d = json.load(open(p, encoding="utf-8"))

BASE = "https://upload.wikimedia.org/wikipedia/commons/"
out, bad = {}, []
for k, v in d.items():
    u = v["u"].split("?")[0]
    m = re.search(r"/commons/thumb/(\w)/(\w{2})/(.+?)/\d+px-", u)
    if m:                                   # 已是缩略图
        a, b, fn = m.groups()
        tpl = f"{BASE}thumb/{a}/{b}/{fn}/{{W}}px-{fn}"
    else:
        m = re.search(r"/commons/(\w)/(\w{2})/(.+)$", u)
        if not m:
            bad.append(k); continue
        a, b, fn = m.groups()
        # SVG/GIF 的缩略图后缀不同，这里只处理位图
        tpl = f"{BASE}thumb/{a}/{b}/{fn}/{{W}}px-{fn}"
    v["u"] = tpl
    out[k] = v

json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"已归一化 {len(out)} 条；失败 {len(bad)}")
for k in bad:
    print("  失败:", k)
print("示例:", urllib.parse.unquote(list(out.values())[0]["u"])[:120])
