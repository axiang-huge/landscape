#!/usr/bin/env python3
"""补齐缺失实景照脚本（带防 429 延迟与重试）"""
import json, os, urllib.request, urllib.parse, io, time
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PH = os.path.join(ROOT, "photos")
os.makedirs(PH, exist_ok=True)
LOCAL = os.path.join(HERE, "photos_local.json")

REUSE = {
    "新都桥 – 塔公草原": ("photos/新都桥–塔公–墨石公园_s.jpg", "photos/新都桥–塔公–墨石公园_l.jpg", "新都桥美景 - Scenary of Xinduqiao Town - 2012.10 - panoramio.jpg"),
    "沙溪古镇": ("photos/沙溪_诺邓_s.jpg", "photos/沙溪_诺邓_l.jpg", "Nuodeng Village, Yunnan (50760756947).jpg"),
    "加榜梯田": ("photos/加榜梯田+肇兴侗寨_s.jpg", "photos/加榜梯田+肇兴侗寨_l.jpg", "Zhaoxing Dong people (38630712136).jpg"),
    "林芝桃花沟 + 索松村": ("photos/索松村_直白村_s.jpg", "photos/索松村_直白村_l.jpg", "Namcha Barwa from the west.jpg"),
    "昭苏天马场": ("photos/昭苏·天马场_s.jpg", "photos/昭苏·天马场_l.jpg", "新疆昭苏草原马牧养系统 马场中的马.jpg"),
    "茫崖艾肯泉 / 俄博梁": ("photos/茫崖·艾肯泉_s.jpg", "photos/茫崖·艾肯泉_l.jpg", "Aiken Spring 202107-1.jpg"),
    "靖边波浪谷 + 雨岔大峡谷": ("photos/靖边波浪谷_雨岔大峡谷_s.jpg", "photos/靖边波浪谷_雨岔大峡谷_l.jpg", "靖边 波浪谷景区之回首桥.jpg"),
    "武隆天生三桥 / 芙蓉洞": ("photos/武隆天生三桥_s.jpg", "photos/武隆天生三桥_l.jpg", "Scenes from the Wulong Natural Bridges in China..JPG"),
    "涠洲岛 + 德天瀑布": ("photos/德天跨国瀑布_s.jpg", "photos/德天跨国瀑布_l.jpg", "2011 广西 崇左 德天瀑布 - panoramio (6).jpg"),
}

COMMONS_MAPPING = {
    "大柴旦翡翠湖": ("File:Dachaidamu Lake 2018-08-01.jpg", "大柴旦翡翠湖"),
    "大柴旦翡翠湖 + 水上雅丹 + 东台吉乃尔": ("File:Dachaidamu Lake 2018-08-01.jpg", "大柴旦翡翠湖+水上雅丹+东台吉乃尔"),
    "普莫雍错": ("File:Nagarze, Shannan, Tibet, China - panoramio (1).jpg", "普莫雍错"),
    "扎尕那": ("File:202609 Zhagana Scenic Area 49.jpg", "扎尕那"),
    "扎尕那 + 郎木寺": ("File:202609 Zhagana Scenic Area 49.jpg", "扎尕那+郎木寺"),
    "萨普神山": ("File:Glacier of China.jpg", "萨普神山"),
    "拉姆拉措": ("File:Sunset at Lake Ximencuo on the Tibetan Plateau.jpg", "拉姆拉措"),
    "佩枯错": ("File:Lake Paiku in Tibet.jpg", "佩枯错"),
    "当惹雍错 / 扎日南木错": ("File:Nagarze, Shannan, Tibet, China - panoramio (10).jpg", "当惹雍错_扎日南木错"),
    "吉隆沟 / 陈塘沟": ("File:Brahmaputra River View.jpg", "吉隆沟_陈塘沟"),
    "墨石公园 / 八美": ("File:Bamei Village - panoramio (10).jpg", "墨石公园_八美"),
    "措卡湖": ("File:Ganzi-afueras-d05.jpg", "措卡湖"),
    "党岭葫芦海": ("File:Danba, Garze, Sichuan, China - panoramio (10).jpg", "党岭葫芦海"),
    "莲宝叶则": ("File:Aba County Aba Prefecture Sichuan China.jpg", "莲宝叶则"),
    "雨崩 · 神瀑 / 冰湖": ("File:Deqen, Yunnan, China - panoramio (14).jpg", "雨崩·神瀑_冰湖"),
    "独龙江": ("File:皇冠山及附近山峰 - 2024-06-01.jpg", "独龙江"),
    "可可托海 / 额尔齐斯大峡谷": ("File:Irtysh river in Koktokay panorama in winter time.jpg", "可可托海_额尔齐斯大峡谷"),
    "东台吉乃尔湖": ("File:China's Qaidam Basin Landscape Similar to Mars.jpg", "东台吉乃尔湖"),
    "黄河源 · 牛头碑": ("File:Yellow River 3113.jpg", "黄河源·牛头碑"),
    "平山湖大峡谷": ("File:Binggou Danxia - 55340169493.jpg", "平山湖大峡谷"),
    "阿拉善 · 通湖草原": ("File:Badanjilin.jpg", "阿拉善·通湖草原"),
    "独库公路 + 伊犁环线": ("File:G217 Duku.jpg", "独库公路+伊犁环线"),
    "理塘 / 海子山": ("File:Litang Ge'nyen 2014.09.16 09-11-25.jpg", "理塘_海子山"),
}

def get_commons_urls(titles):
    out = {}
    chunk_size = 20
    for i in range(0, len(titles), chunk_size):
        chunk = titles[i:i+chunk_size]
        url = "https://commons.wikimedia.org/w/api.php?action=query&titles=" + urllib.parse.quote("|".join(chunk)) + "&prop=imageinfo&iiprop=url|size|mime&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "LandscapeAtlasBot/2.1 (contact@mywebsite.org)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                t = p.get("title")
                ii = p.get("imageinfo", [{}])[0]
                if ii.get("url"):
                    out[t] = (ii["url"], ii.get("width", 0), ii.get("height", 0))
    return out

def process_and_save(raw_data, base_name):
    img = Image.open(io.BytesIO(raw_data))
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    s_path = os.path.join(PH, f"{base_name}_s.jpg")
    l_path = os.path.join(PH, f"{base_name}_l.jpg")
    
    w, h = img.size
    sw = min(500, w)
    sh = int(round(h * (sw / w)))
    img_s = img.resize((sw, sh), Image.Resampling.LANCZOS)
    img_s.save(s_path, "JPEG", quality=86, optimize=True)
    
    lw = min(1280, w)
    lh = int(round(h * (lw / w)))
    img_l = img.resize((lw, lh), Image.Resampling.LANCZOS)
    img_l.save(l_path, "JPEG", quality=90, optimize=True)
    
    return f"photos/{base_name}_s.jpg", f"photos/{base_name}_l.jpg"

def fetch_with_retry(url):
    headers = {"User-Agent": "LandscapeAtlasBot/2.1 (Mozilla/5.0; personal trip planning)"}
    delay = 3.0
    for attempt in range(5):
        try:
            time.sleep(delay)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 1024:
                    return data
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                print(f"    -> 触发限流 429/503，等待 {delay*2:.1f} 秒后重试 (attempt {attempt+1}/5)...")
                delay *= 2.5
                continue
            raise
        except Exception as e:
            print(f"    -> 网络异常 {e}，等待重试...")
            delay *= 2
    return None

def main():
    local = json.load(open(LOCAL, encoding="utf-8"))
    
    for name, (s, l, f) in REUSE.items():
        local[name] = {"s": s, "l": l, "f": f}

    needed_titles = list(set(file_title for file_title, _ in COMMONS_MAPPING.values()))
    urls = get_commons_urls(needed_titles)
    
    downloaded_cache = {}
    
    for name, (file_title, base_name) in COMMONS_MAPPING.items():
        s_file = os.path.join(PH, f"{base_name}_s.jpg")
        l_file = os.path.join(PH, f"{base_name}_l.jpg")
        credit_name = file_title.replace("File:", "")
        
        if os.path.exists(s_file) and os.path.exists(l_file):
            local[name] = {"s": f"photos/{base_name}_s.jpg", "l": f"photos/{base_name}_l.jpg", "f": credit_name}
            print(f"✓ 本地已有: {name}")
            continue
            
        if file_title not in urls:
            print(f"✗ 无法获取 URL: {file_title}")
            continue
            
        file_url = urls[file_title][0]
        
        if file_title not in downloaded_cache:
            print(f"正在下载 [{name}] ({file_title})...")
            raw_data = fetch_with_retry(file_url)
            if raw_data:
                downloaded_cache[file_title] = raw_data
            else:
                print(f"✗ 下载失败: {file_title}")
                continue
                
        raw_data = downloaded_cache[file_title]
        try:
            s_rel, l_rel = process_and_save(raw_data, base_name)
            local[name] = {"s": s_rel, "l": l_rel, "f": credit_name}
            print(f"✓ 生成完毕: {name} -> {s_rel}")
        except Exception as e:
            print(f"✗ 处理图片出错 {name}: {e}")

    json.dump(local, open(LOCAL, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"\n全部就绪！photos_local.json 当前条目数: {len(local)}")

if __name__ == "__main__":
    main()
