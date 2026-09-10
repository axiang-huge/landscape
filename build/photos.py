#!/usr/bin/env python3
"""为每个地点抓取维基百科/维基共享资源的实景照片 URL。
策略：用人工指定的精确条目名直接查 pageimages（比全文搜索准得多），
拿不到再退回 Commons 分类搜图。输出 build/photos.json {地点名: url}
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = json.load(open(os.path.join(HERE, "names.json"), encoding="utf-8"))

# 地点名 -> 维基条目名（人工指定，避免搜索命中错误条目）
Q = {
    "梅里雪山 · 飞来寺 / 雾浓顶": "梅里雪山", "冷嘎措 / 子梅垭口": "贡嘎山",
    "珠峰绒布寺 / 大本营": "絨布寺", "索松村 / 直白村": "南迦巴瓦峰",
    "稻城亚丁 · 牛奶海 / 五色海": "亚丁自然保护区", "塔县 · 白沙湖 / 金草滩": "慕士塔格峰",
    "赛里木湖": "赛里木湖", "大柴旦翡翠湖": "大柴旦镇", "敦煌 · 鸣沙山 / 雅丹": "鸣沙山",
    "纳木错": "纳木错", "普莫雍错": "普莫雍错", "冈仁波齐": "冈仁波齐峰",
    "扎尕那": "扎尕那", "巴丹吉林沙漠": "巴丹吉林沙漠", "额济纳胡杨林": "额济纳旗",
    "萨普神山": "比如县", "元阳哈尼梯田": "红河哈尼梯田", "羊卓雍措": "羊卓雍错",
    "然乌湖 + 来古冰川": "然乌湖", "拉姆拉措": "拉姆拉措", "佩枯错": "佩枯错",
    "当惹雍错 / 扎日南木错": "当惹雍错", "米堆冰川 / 卡若拉冰川": "米堆冰川",
    "巴松措": "巴松措", "吉隆沟 / 陈塘沟": "吉隆县", "新都桥 – 塔公草原": "塔公寺",
    "四姑娘山双桥沟": "四姑娘山", "达古冰川": "黑水县", "海螺沟冰川": "海螺沟",
    "墨石公园 / 八美": "道孚县", "措卡湖": "新龙县", "党岭葫芦海": "丹巴县",
    "格聂之眼": "格聂神山", "莲宝叶则": "阿坝县", "木格措 / 红海子": "康定市",
    "丹巴 · 中路 / 甲居藏寨": "甲居藏寨", "若尔盖 · 黄河九曲第一湾": "若尔盖县",
    "稻城亚丁 · 珍珠海 / 冲古草甸": "仙乃日", "色达 / 亚青寺": "五明佛学院",
    "玉龙雪山 · 牦牛坪 / 云杉坪": "玉龙雪山", "雨崩 · 神瀑 / 冰湖": "雨崩村",
    "泸沽湖 · 尼塞 / 小落水": "泸沽湖", "白马雪山垭口": "白馬雪山",
    "哈巴雪山 / 虎跳峡": "虎跳峡", "腾冲 · 火山 / 银杏村": "腾冲市",
    "东川红土地": "东川区", "千湖山 / 石卡雪山": "香格里拉市",
    "纳帕海 / 依拉草原": "纳帕海", "沙溪古镇": "沙溪镇 (剑川县)",
    "老君山 · 九十九龙潭": "老君山 (云南)", "丙中洛 / 秋那桶": "怒江傈僳族自治州",
    "独龙江": "独龙江乡", "禾木 / 白哈巴": "禾木村", "喀拉库勒湖": "喀拉库勒湖",
    "喀拉峻 / 琼库什台": "特克斯县", "昭苏 · 天马场": "昭苏县",
    "那拉提 / 唐布拉 / 库尔德宁": "那拉提草原", "巴音布鲁克": "巴音布鲁克草原",
    "可可托海 / 额尔齐斯大峡谷": "可可托海镇", "乌尔禾魔鬼城": "乌尔禾区",
    "交河故城 / 高昌故城": "交河故城", "温宿 / 库车大峡谷": "库车市",
    "艾丁湖": "艾丁湖", "卓尔山": "祁连县", "茫崖 · 艾肯泉": "茫崖市",
    "俄博梁雅丹": "柴达木盆地", "东台吉乃尔湖": "柴达木盆地",
    "察尔汗盐湖": "察尔汗盐湖", "坎布拉 / 贵德": "坎布拉国家森林公园",
    "年保玉则": "年保玉则", "阿尼玛卿": "阿尼玛卿山", "黄河源 · 牛头碑": "鄂陵湖",
    "平山湖大峡谷": "张掖市", "郎木寺 / 桑科草原": "郎木寺",
    "拉卜楞寺": "拉卜楞寺", "嘉峪关 / 玉门关 / 汉长城": "嘉峪关",
    "阿尔山": "阿尔山市", "阿拉善 · 通湖草原": "阿拉善盟",
    "呼伦贝尔 / 额尔古纳 / 室韦": "呼伦贝尔市", "沙坡头": "沙坡头区",
    "西夏王陵": "西夏王陵", "靖边波浪谷 / 雨岔大峡谷": "靖边县",
    "壶口瀑布": "壶口瀑布", "华山": "華山", "梵净山 · 红云金顶": "梵净山",
    "加榜梯田": "从江县", "万峰林": "兴义市", "荔波小七孔": "荔波县",
    "武隆天生三桥": "武隆区", "涠洲岛": "涠洲岛", "德天跨国瀑布": "德天瀑布",
    "龙脊梯田": "龙脊梯田", "陵水分界洲 / 万宁 / 东方鱼鳞洲": "分界洲岛",
    "长白山天池": "天池 (长白山)", "漠河北极村": "漠河市",
    "罗布泊 / 塔克拉玛干沙漠公路": "塔克拉玛干沙漠",
    "独库公路 + 伊犁环线": "独库公路",
    "大柴旦翡翠湖 + 水上雅丹 + 东台吉乃尔": "柴达木盆地",
    "张掖七彩丹霞 + 敦煌雅丹": "张掖丹霞国家地质公园",
    "新都桥 – 塔公 – 墨石公园": "新都桥镇",
    "塔县金草滩 + 白沙湖 + 石头城": "塔什库尔干塔吉克自治县",
    "稻城亚丁（长线）": "央迈勇", "喀纳斯 / 禾木 / 白哈巴": "喀纳斯湖",
    "林芝桃花沟 + 索松村": "林芝市", "羊湖 + 普莫雍错": "羊卓雍错",
    "米堆冰川 / 来古冰川": "米堆冰川", "珠峰 / 阿里线": "珠穆朗玛峰",
    "丹巴甲居 / 中路藏寨": "甲居藏寨", "毕棚沟": "理县",
    "理塘 / 海子山": "理塘县", "泸沽湖 + 香格里拉": "泸沽湖",
    "罗平油菜花": "罗平县", "普者黑": "普者黑", "沙溪 / 诺邓": "诺邓村",
    "腾冲银杏村 + 火山": "腾冲市", "扎尕那 + 郎木寺": "扎尕那",
    "青海湖 + 门源": "青海湖", "茫崖艾肯泉 / 俄博梁": "茫崖市",
    "额济纳胡杨林 ": "额济纳旗", "沙坡头 + 黄河宿集": "沙坡头区",
    "靖边波浪谷 + 雨岔大峡谷": "靖边县", "加榜梯田 + 肇兴侗寨": "肇兴侗寨",
    "武隆天生三桥 / 芙蓉洞": "武隆区", "涠洲岛 + 德天瀑布": "涠洲岛",
    "长白山 + 魔界": "长白山", "漠河 / 北红村": "漠河市",
    "交河故城 / 葡萄沟": "交河故城", "乌尔禾魔鬼城 ": "乌尔禾区",
}

API = "https://zh.wikipedia.org/w/api.php"


def get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "wedding-atlas/1.0 (personal trip planning)",
        "Accept-Encoding": "gzip",
    })
    delay = 2.0
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception:
            time.sleep(delay)
            delay *= 2
    return {}


def by_title(title):
    j = get({"action": "query", "prop": "pageimages", "piprop": "thumbnail|original",
             "pithumbsize": 1200, "titles": title, "redirects": 1, "format": "json"})
    for pg in j.get("query", {}).get("pages", {}).values():
        th = pg.get("thumbnail")
        if th:
            return th["source"].split("?")[0], pg.get("title")
    return None, None


def by_search(term):
    j = get({"action": "query", "prop": "pageimages", "piprop": "thumbnail",
             "pithumbsize": 1200, "generator": "search", "gsrsearch": term,
             "gsrlimit": 3, "format": "json"})
    pages = j.get("query", {}).get("pages", {})
    best = sorted(pages.values(), key=lambda p: p.get("index", 99))
    for pg in best:
        th = pg.get("thumbnail")
        if th:
            return th["source"].split("?")[0], pg.get("title")
    return None, None


OUT = os.path.join(HERE, "photos.json")
res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
miss = []
for i, n in enumerate(NAMES, 1):
    if n in res:                      # 断点续传
        print(f"[{i:3}/{len(NAMES)}] · {n}  (已有)")
        continue
    q = Q.get(n) or Q.get(n.strip()) or n.split(" ")[0].split("·")[0].split("/")[0].strip()
    url, hit = by_title(q)
    if not url:
        url, hit = by_search(q)
    if url:
        res[n] = url
        print(f"[{i:3}/{len(NAMES)}] ✓ {n}  ←  {hit}")
        json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    else:
        miss.append((n, q))
        print(f"[{i:3}/{len(NAMES)}] ✗ {n}  (查询: {q})")
    time.sleep(1.1)

json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"\n命中 {len(res)}/{len(NAMES)}；缺失 {len(miss)}")
for n, q in miss:
    print("  缺:", n, "|", q)
