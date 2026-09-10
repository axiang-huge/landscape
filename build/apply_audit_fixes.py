#!/usr/bin/env python3
import os
import json
import subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHOTOS_DIR = os.path.join(ROOT, 'photos')
LOCAL_JSON = os.path.join(HERE, 'photos_local.json')

TASKS = [
    {
        'src': '/tmp/test_zhaoxing.jpg',
        'crop': None,
        'targets': ['加榜梯田 + 肇兴侗寨', '加榜梯田'],
        'out_bases': ['加榜梯田+肇兴侗寨'],
        'credit': 'Zhaoxing Dong Village Drum Towers and Terraces.jpg'
    },
    {
        'src': '/tmp/test_huashan.jpg',
        'crop': None,
        'targets': ['华山'],
        'out_bases': ['华山'],
        'credit': 'Mount Hua Chess Pavilion and Precipice.jpg'
    },
    {
        'src': '/tmp/test_fanjingshan.jpg',
        'crop': None,
        'targets': ['梵净山 · 红云金顶'],
        'out_bases': ['梵净山·红云金顶'],
        'credit': 'Fanjingshan Golden Summit at Sunrise.jpg'
    },
    {
        'src': '/tmp/test_wulong.jpg',
        'crop': None,
        'targets': ['武隆天生三桥 / 芙蓉洞', '武隆天生三桥'],
        'out_bases': ['武隆天生三桥'],
        'credit': 'Wulong Karst Three Natural Bridges and Tianfu Outpost.jpg'
    },
    {
        'src': '/tmp/test_jiuqu.jpg',
        'crop': None,
        'targets': ['若尔盖 · 黄河九曲第一湾'],
        'out_bases': ['若尔盖·黄河九曲第一湾'],
        'credit': 'First Bend of the Yellow River at Zoige Grassland Sunset.jpg'
    },
    {
        'src': '/tmp/test_zhagana.jpg',
        'crop': None,
        'targets': ['扎尕那', '扎尕那 + 郎木寺'],
        'out_bases': ['扎尕那', '扎尕那+郎木寺'],
        'credit': 'Zhagana Stone Forest Tibetan Village Panorama.jpg'
    },
    {
        'src': '/tmp/test_labrang.jpg',
        'crop': None,
        'targets': ['拉卜楞寺'],
        'out_bases': ['拉卜楞寺'],
        'credit': 'Labrang Monastery Golden Roof and Halls Panorama.jpg'
    },
    {
        'src': '/tmp/test_zhaosu.jpg',
        'crop': None,
        'targets': ['昭苏 · 天马场', '昭苏天马场'],
        'out_bases': ['昭苏·天马场'],
        'credit': 'Zhaosu Prairie Heavenly Horses of Ili.jpg'
    },
    {
        'src': '/tmp/test_nianbaoyuze.jpg',
        'crop': None,
        'targets': ['年保玉则'],
        'out_bases': ['年保玉则'],
        'credit': 'Nianbaoyuze Fairy Lake and Sacred Peaks Flowers.jpg'
    },
    {
        'src': '/tmp/test_kanbula.jpg',
        'crop': None,
        'targets': ['坎布拉 / 贵德'],
        'out_bases': ['坎布拉_贵德'],
        'credit': 'Kanbula National Forest Park Danxia and Turquoise Reservoir.jpg'
    },
    {
        'src': '/tmp/test_napahai.jpg',
        'crop': None,
        'targets': ['纳帕海 / 依拉草原'],
        'out_bases': ['纳帕海_依拉草原'],
        'credit': 'Napa Lake and Yila Grassland Wetland Flowers.jpg'
    },
    {
        'src': '/tmp/test_bingzhongluo.jpg',
        'crop': None,
        'targets': ['丙中洛 / 秋那桶'],
        'out_bases': ['丙中洛_秋那桶'],
        'credit': 'First Bend of Nujiang River at Bingzhongluo.jpg'
    },
    {
        'src': '/tmp/test_koktokay.jpg',
        'crop': None,
        'targets': ['可可托海 / 额尔齐斯大峡谷'],
        'out_bases': ['可可托海_额尔齐斯大峡谷'],
        'credit': 'Koktokay Irtysh Grand Canyon and Granite Bell Mountain.jpg'
    },
    {
        'src': '/tmp/cand_tianshan.jpg',
        'crop': None,
        'targets': ['温宿 / 库车大峡谷'],
        'out_bases': ['温宿_库车大峡谷'],
        'credit': 'Kuche Tianshan Mysterious Grand Canyon Red Cliffs.jpg'
    },
    {
        'src': '/tmp/cand_shaxi_stage.jpg',
        'crop': None,
        'targets': ['沙溪古镇', '沙溪 / 诺邓'],
        'out_bases': ['沙溪_诺邓'],
        'credit': 'Shaxi Ancient Town Sideng Street Ancient Stage.jpg'
    },
    {
        'src': '/tmp/cand_tengger.jpg',
        'crop': None,
        'targets': ['阿拉善 · 通湖草原'],
        'out_bases': ['阿拉善·通湖草原'],
        'credit': 'Alxa Tengger Desert Sand Dunes and Curves.jpg'
    },
    {
        'src': '/tmp/test_moshi.jpg',
        'crop': None,
        'targets': ['墨石公园 / 八美'],
        'out_bases': ['墨石公园_八美'],
        'credit': 'Moshi Park Alien Geological Mylonite Stone Forest.jpg'
    },
    {
        'src': '/tmp/test_sapu.jpg',
        'crop': None,
        'targets': ['萨普神山'],
        'out_bases': ['萨普神山'],
        'credit': 'Sapu Sacred Glacier Mountain Geometric Peak.jpg'
    },
    {
        'src': '/tmp/test_cuoka_crop2.jpg',
        'crop': None,
        'targets': ['措卡湖'],
        'out_bases': ['措卡湖'],
        'credit': 'Cuoka Lake Emerald Water and Tibetan Monastery Reflection.jpg'
    },
    {
        'src': '/tmp/batch3/dangling_crop.jpg',
        'crop': None,
        'targets': ['党岭葫芦海'],
        'out_bases': ['党岭葫芦海'],
        'credit': 'Dangling Gourd Sea Alpine Lake and Autumn Larches.jpg'
    },
    {
        'src': '/tmp/batch2/gyirong.jpg',
        'crop': None,
        'targets': ['吉隆沟 / 陈塘沟'],
        'out_bases': ['吉隆沟_陈塘沟'],
        'credit': 'Gyirong Valley Himalayan Snow Peak Road.jpg'
    },
    {
        'src': '/tmp/batch2/dongtai.jpg',
        'crop': None,
        'targets': ['东台吉乃尔湖', '大柴旦翡翠湖 + 水上雅丹 + 东台吉乃尔'],
        'out_bases': ['东台吉乃尔湖', '大柴旦翡翠湖+水上雅丹+东台吉乃尔'],
        'credit': 'Dongtai Jinai er Tiffany Blue Salt Lake.jpg'
    },
    {
        'src': '/tmp/batch2/eboliang.jpg',
        'crop': None,
        'targets': ['俄博梁雅丹'],
        'out_bases': ['俄博梁雅丹'],
        'credit': 'Eboliang Yardang Mars Landscape Sunset.jpg'
    },
    {
        'src': '/tmp/batch2/lhamo.jpg',
        'crop': None,
        'targets': ['拉姆拉措'],
        'out_bases': ['拉姆拉措'],
        'credit': 'Lhamo La-tso Sacred Blue Lake in Mountain Amphitheater.jpg'
    },
    {
        'src': '/tmp/batch2/aiken.jpg',
        'crop': None,
        'targets': ['茫崖 · 艾肯泉', '茫崖艾肯泉 / 俄博梁'],
        'out_bases': ['茫崖·艾肯泉'],
        'credit': 'Mangya Aiken Spring Eye of the Demon Aerial View.jpg'
    },
    {
        'src': '/tmp/batch2/aershan.jpg',
        'crop': (0, 0, 1200, 775),
        'targets': ['阿尔山'],
        'out_bases': ['阿尔山'],
        'credit': 'Arxan Tuofengling Tianchi Autumn Forest.jpg'
    },
    {
        'src': '/tmp/batch2/tengchong_ginkgo.jpg',
        'crop': None,
        'targets': ['腾冲 · 火山 / 银杏村', '腾冲银杏村 + 火山'],
        'out_bases': ['腾冲·火山_银杏村', '腾冲银杏村+火山'],
        'credit': 'Tengchong Jiangdong Ancient Ginkgo Village Autumn.jpg'
    },
    {
        'src': '/tmp/batch3/dulong_clean.jpg',
        'crop': None,
        'targets': ['独龙江'],
        'out_bases': ['独龙江'],
        'credit': 'Dulong River First Bend Whitewater Gorge.jpg'
    },
    {
        'src': '/tmp/batch4/jingbian.jpg',
        'crop': None,
        'targets': ['靖边波浪谷 / 雨岔大峡谷', '靖边波浪谷 + 雨岔大峡谷'],
        'out_bases': ['靖边波浪谷_雨岔大峡谷'],
        'credit': 'Jingbian Wave Valley Danxia Sandstone Sunset.jpg'
    },
    {
        'src': '/tmp/batch5/pingshanhu.jpg',
        'crop': None,
        'targets': ['平山湖大峡谷'],
        'out_bases': ['平山湖大峡谷'],
        'credit': 'Zhangye Pingshanhu Grand Canyon Sunset Glow.jpg'
    },
    {
        'src': '/tmp/batch3/paiku.jpg',
        'crop': (24, 60, 1176, 730),
        'targets': ['佩枯错'],
        'out_bases': ['佩枯错'],
        'credit': 'Lake Paiku Deep Blue Water and Plateau Foothills.jpg'
    },
    {
        'src': '/tmp/batch5/qarhan2.jpg',
        'crop': None,
        'targets': ['察尔汗盐湖'],
        'out_bases': ['察尔汗盐湖'],
        'credit': 'Qarhan Salt Lake Ten-Thousand-Zhang Salt Bridge Aerial.jpg'
    },
    {
        'src': '/tmp/batch4/niutou_2.jpg',
        'crop': (0, 0, 750, 422),
        'targets': ['黄河源 · 牛头碑'],
        'out_bases': ['黄河源·牛头碑'],
        'credit': 'Yellow River Source Ox Head Monument and Sacred Lake.jpg'
    },
    {
        'src': '/tmp/batch5/pumayumco2.jpg',
        'crop': None,
        'targets': ['普莫雍错'],
        'out_bases': ['普莫雍错'],
        'credit': 'Pumayumco Blue Ice Lake Cracks in Winter.jpg'
    },
    {
        'src': '/tmp/batch5/shika.jpg',
        'crop': (0, 0, 1200, 675),
        'targets': ['千湖山 / 石卡雪山'],
        'out_bases': ['千湖山_石卡雪山'],
        'credit': 'Shika Snow Mountain Range and Sunlight.jpg'
    },
    {
        'src': '/tmp/batch5/baima2.jpg',
        'crop': None,
        'targets': ['白马雪山垭口'],
        'out_bases': ['白马雪山垭口'],
        'credit': 'Baima Snow Mountain Peaks and Alpine Pass.jpg'
    },
    {
        'src': '/tmp/batch5/ayding.jpg',
        'crop': None,
        'targets': ['艾丁湖'],
        'out_bases': ['艾丁湖'],
        'credit': 'Ayding Lake Lowest Elevation Aerial Panorama.jpg'
    },
    {
        'src': '/tmp/batch4/dangra.jpg',
        'crop': (0, 0, 800, 450),
        'targets': ['当惹雍错 / 扎日南木错'],
        'out_bases': ['当惹雍错_扎日南木错'],
        'credit': 'Tangra Yumco Holy Lake Turquoise Water and Sky.jpg'
    },
    {
        'src': '/tmp/dachaidan_f1.jpg',
        'crop': (200, 0, 3640, 2160),
        'targets': ['大柴旦翡翠湖'],
        'out_bases': ['大柴旦翡翠湖'],
        'credit': 'Dachaidan Emerald Lake Crystal Pools 4K Aerial.jpg'
    }
]

def process_task(task):
    src = task['src']
    crop = task['crop']
    targets = task['targets']
    out_bases = task['out_bases']
    credit = task['credit']

    if not os.path.exists(src):
        raise FileNotFoundError(f'Source file not found: {src}')

    im = Image.open(src)
    if crop:
        im = im.crop(crop)
    if im.mode != 'RGB':
        im = im.convert('RGB')

    w, h = im.size

    for base in out_bases:
        s_rel = f'photos/{base}_s.jpg'
        l_rel = f'photos/{base}_l.jpg'
        s_abs = os.path.join(ROOT, s_rel)
        l_abs = os.path.join(ROOT, l_rel)

        # 生成 _s.jpg (宽 500)
        sw = 500
        sh = max(1, int(h * sw / w))
        im_s = im.resize((sw, sh), Image.Resampling.LANCZOS)
        im_s.save(s_abs, 'JPEG', quality=86, optimize=True)

        # 生成 _l.jpg (宽 1280 或原始大小，最高 1280)
        if w > 1280:
            lw = 1280
            lh = max(1, int(h * lw / w))
            im_l = im.resize((lw, lh), Image.Resampling.LANCZOS)
        else:
            im_l = im
        im_l.save(l_abs, 'JPEG', quality=90, optimize=True)

        print(f'  [SAVED] {s_rel} ({sw}x{sh}) & {l_rel} ({im_l.size[0]}x{im_l.size[1]})')

    return targets, out_bases[0], credit

def main():
    print('=== 开始批量处理高品质实景照片 ===')
    with open(LOCAL_JSON, 'r', encoding='utf-8') as f:
        photos_local = json.load(f)

    updated_count = 0
    for task in TASKS:
        targets, main_base, credit = process_task(task)
        for t in targets:
            photos_local[t] = {
                's': f'photos/{main_base}_s.jpg',
                'l': f'photos/{main_base}_l.jpg',
                'f': credit
            }
            updated_count += 1
            print(f'  Updated photos_local.json: {t} -> {main_base}')

    with open(LOCAL_JSON, 'w', encoding='utf-8') as f:
        json.dump(photos_local, f, ensure_ascii=False, indent=2)
    print(f"\n成功更新 photos_local.json 中的 {updated_count} 处地点配置！")

    print("\n=== 重新运行 coords.py 编译 data.js ===")
    res = subprocess.run(['python3', os.path.join(HERE, 'coords.py')], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print('STDERR:', res.stderr)

    print('=== 全部处理完毕！ ===')

if __name__ == '__main__':
    main()
