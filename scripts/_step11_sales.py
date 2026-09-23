# -*- coding: utf-8 -*-
"""Step 11: 按用户画像设置商品销量（fake_sale）
画像：小学生 + 初中生；决策者=女性家长
原则：高频消耗品高、高客单低；区间内随机（偏态）避免整齐划一
"""
import requests, json, os, re, time, random, sys
from collections import Counter

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}

APIUNION = "https://d5ma.img.apiunion.com"
JD = "https://img13.360buyimg.com"
PICING = "https://img.picing.com"
MALL = "https://mall.baovbao.com"


def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()


def restore_url(u):
    if not u:
        return ""
    s = str(u).strip()
    if s.startswith(("http://", "https://")):
        return s
    if s.startswith("//"):
        path = s[2:]
        if path.startswith("upload/") or re.match(r"^\d{4}/\d{2}/", path) or path.startswith("images/"):
            return "https://mall.baovbao.com/" + path
        if path.startswith("i/"):
            return APIUNION + "/" + path
        return "https:" + s
    path = s if s.startswith("/") else "/" + s
    while path.startswith("//"):
        path = path[1:]
    if path.startswith("/i/") or "/i/" in path[:6]:
        return APIUNION + path
    if "/jfs/" in path or path.startswith("/n12/") or path.startswith("/sku/jfs"):
        return JD + path
    if "imageMogr2" in s or re.search(r"/\d{10,}_\d{2,4}X\d{2,4}_", path):
        return PICING + path
    if path.startswith("/upload/") or path.startswith("upload/"):
        if not path.startswith("/"):
            path = "/" + path
        return MALL + path
    if path.startswith("/images/") or re.match(r"^/\d{4}/\d{2}/", path):
        return MALL + path
    return MALL + path


def build_body(detail, good_cate, fake_sale=None):
    skus, seen = [], set()
    for s in detail.get("skus") or []:
        key = (s.get("spec_val1"), s.get("spec_val2"), s.get("spec_val3"))
        if key in seen:
            continue
        seen.add(key)
        o = dict(s)
        if o.get("cover_img"):
            o["cover_img"] = restore_url(o["cover_img"])
        if o.get("wheel_img"):
            o["wheel_img"] = [restore_url(x) for x in o["wheel_img"]]
        if o.get("detail_img"):
            o["detail_img"] = [restore_url(x) for x in o["detail_img"]]
        if not o.get("pay_setting"):
            o["pay_setting"] = [{"checked": 0, "account_id": "", "money": 0}]
        if not o.get("spec_val1"):
            sd = o.get("spec_data") or []
            o["spec_val1"] = (sd[0].get("val") if sd else "默认") or "默认"
        skus.append(o)
    if not skus:
        skus = [{"cover_img": "", "spec_val1": "默认", "spec_val2": "", "unit_quatity": 1,
                 "cost_price": detail.get("cost_price") or 0, "sale_price": detail.get("sale_price") or 0,
                 "crossed_price": detail.get("crossed_price") or 0, "stock": 0, "state": 1,
                 "pay_setting": [{"checked": 0, "account_id": "", "money": 0}]}]
    raw = detail.get("good_brand") or []
    mapped = []
    for b in raw:
        if isinstance(b, dict):
            mapped.append([b.get("brand_id1") or "", b.get("brand_id2") or ""])
        elif isinstance(b, (list, tuple)):
            mapped.append([b[0] if b else "", b[1] if len(b) > 1 else ""])
    wheel = [restore_url(x) for x in (detail.get("wheel_img") or [])]
    dimgs = [restore_url(x) for x in (detail.get("detail_img") or [])]
    return {
        "good_name": detail.get("good_name") or "", "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"), "good_type": detail.get("good_type"),
        "good_brand": mapped or [["", ""]], "good_cate": good_cate,
        "tag_ids": detail.get("tag_ids") or [],
        "fake_sale": fake_sale if fake_sale is not None else (detail.get("fake_sale") or 0),
        "good_desc": detail.get("good_desc") or "", "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0, "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0, "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": restore_url(detail.get("cover_img")),
        "wheel_img": wheel, "wheel_img_arr": [{"name": "", "url": x} for x in wheel],
        "video_type": detail.get("video_type") or 1, "video_url": detail.get("video_url") or "",
        "video_url_upload": detail.get("video_url_upload") or "", "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": dimgs, "detail_img_arr": [{"name": "", "url": x} for x in dimgs],
        "content": detail.get("content") or "", "recommend": detail.get("recommend") or "",
        "sort": detail.get("sort") if detail.get("sort") is not None else 100,
        "unit": detail.get("unit") or "", "buy_min": detail.get("buy_min") or 1,
        "buy_max": detail.get("buy_max") or 1000, "spec_name1": detail.get("spec_name1") or "规格",
        "spec_name2": detail.get("spec_name2") or "", "spec_name3": detail.get("spec_name3") or "",
        "spec_name4": detail.get("spec_name4") or "", "skus": skus,
        "stock_warn": detail.get("stock_warn") or 0,
    }


# ===== 销量区间（按二级分类）=====
SALES = {
    # 学习文具 —— 学生每日消耗，高
    '铅笔': (3000, 9000), '橡皮擦': (3000, 9000), '笔芯': (2500, 8000), '作业本': (2500, 8000),
    '中性笔': (2000, 7000), '自动铅笔': (1500, 5000), '卷笔刀': (1200, 4000),
    '尺子': (800, 3000), '书皮': (600, 2500), '笔袋': (600, 2500), '美术用品': (800, 3000),
    '修正带': (500, 2000), '固体胶': (400, 1500), '学生剪刀': (400, 1500),
    '钢笔': (300, 1200), '纸品': (1500, 5000),
    # 体育用品
    '跳绳': (2000, 6000), '篮球': (800, 3000), '足球': (700, 2500),
    '羽毛球': (600, 2500), '乒乓球': (500, 2000), '排球': (300, 1200), '其他体育用品': (300, 1500),
    # 少儿护理 —— 妈妈高频回购
    '儿童牙膏': (2500, 8000), '儿童牙刷': (2000, 7000), '儿童洗手液': (1500, 5000),
    '儿童洗发水': (1000, 4000), '儿童沐浴露': (1000, 4000), '儿童洗面奶': (600, 2500),
    '儿童面霜': (800, 3000), '儿童润唇膏': (500, 2000), '儿童防晒': (400, 2000),
    '儿童护臀膏': (400, 1500), '儿童洗衣液': (800, 3000),
    # 少儿穿戴
    '内裤': (2000, 7000), '袜子': (2000, 7000), '校服内搭': (1000, 4000),
    '儿童运动鞋': (800, 3000), '拖鞋': (700, 2500), '帽子': (500, 2000),
    '书包': (800, 3000), '喝水杯': (600, 2500), '毛巾': (700, 2500), '雨衣雨鞋': (400, 1800),
    # 少儿食品 —— 家长囤货
    '牛奶/奶制品': (3000, 9000), '早餐麦片': (1200, 4000), '天然饮品': (1000, 4000),
    '健康零食': (1500, 5000), '坚果/果干': (1200, 4500), '营养补充': (600, 2500), '儿童调味品': (300, 1200),
    # 家庭日用 —— 全家消耗
    '抽纸/面巾纸': (3000, 9000), '卷纸/卫生纸': (2500, 8000), '洗衣液': (2000, 7000),
    '衣物柔顺剂': (800, 3000), '洗手液': (1500, 5000), '牙膏/牙刷': (2000, 7000),
    '洗发水': (1500, 5000), '沐浴露': (1500, 5000), '洗面奶': (600, 2500),
    '洗洁精': (1500, 5000), '保鲜用品': (800, 3000), '垃圾袋': (1500, 5000),
    '消毒除菌': (600, 2500), '厨房湿巾': (600, 2500), '洁厕灵': (500, 2000),
    '地板清洁剂': (400, 1500), '电蚊香液': (500, 2000), '驱蚊水': (400, 1800),
    # 读物潮玩
    '同步练习': (1500, 5000), '课外阅读': (1200, 4500), '工具书': (800, 2500),
    '思维训练': (600, 2500), '科普/百科': (600, 2500), '绘本/图画书': (800, 3000),
    '益智拼图': (800, 3000), '盲盒/卡牌': (1000, 4000), '手办/摆件': (300, 1500),
    '减压玩具': (400, 1800), '解压玩具': (400, 1800),
    # 米面油品 —— 囤货刚需
    '大豆油': (2000, 6000), '调和油': (1500, 5000), '花生油': (1000, 4000),
    '菜籽油': (800, 3000), '玉米葵花油': (600, 2500), '橄榄油': (200, 900),
    '东北珍珠米': (2000, 6000), '长粒香米': (2000, 6000), '丝苗米': (800, 3000),
    '五常大米': (800, 3000), '泰国香米': (400, 1800), '胚芽米': (300, 1200),
    '中筋面粉': (1500, 5000), '高筋面粉': (600, 2500), '低筋面粉': (500, 2000),
    '全麦面粉': (400, 1500), '糯米粉': (300, 1200),
    # 家用电器 —— 高客单，压低
    '护眼台灯': (600, 2500), '加湿器': (300, 1200), '电饭煲': (400, 1800),
    '破壁机': (200, 900), '扫地机器人': (80, 400), '电吹风': (300, 1200), '净水器': (100, 500),
}
DEFAULT_RANGE = (200, 900)


def pick_sale(lo, hi):
    """偏态随机：更靠近下限（真实商品多集中在中低位），少量爆款靠近上限"""
    r = random.random()
    if r < 0.15:      # 15% 爆款
        v = random.uniform(hi * 0.7, hi)
    elif r < 0.55:    # 40% 中位
        v = random.uniform((lo + hi) / 2 * 0.8, hi * 0.7)
    else:             # 45% 靠下限
        v = random.uniform(lo, (lo + hi) / 2 * 0.8)
    # 取整到 10（更真实）
    return int(round(v / 10) * 10)


# ===== 拉商品 =====
all_g = []
for src in (1, 3):
    page = 1
    while True:
        d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": src,
                                  "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
        data = d.get('data') or []
        if not data:
            break
        all_g.extend(data)
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.08)
print('商品: ' + str(len(all_g)))

random.seed(20260923)
plan = []
for g in all_g:
    gc = g.get('good_cate') or []
    c2 = gc[0].get('cate2') if gc else ''
    lo, hi = SALES.get(c2, DEFAULT_RANGE)
    target = pick_sale(lo, hi)
    cur = g.get('fake_sale') or 0
    if cur == target:
        target = target + 10
    plan.append({'good_id': g['good_id'], 'name': (g.get('good_name') or '')[:35],
                 'cate2': c2, 'old': cur, 'new': target})

print('销量分布预览:')
buckets = Counter()
for p in plan:
    v = p['new']
    k = '10000+' if v >= 10000 else ('5000-9999' if v >= 5000 else ('2000-4999' if v >= 2000 else ('500-1999' if v >= 500 else '<500')))
    buckets[k] += 1
for k in ['10000+', '5000-9999', '2000-4999', '500-1999', '<500']:
    print('  ' + k + ': ' + str(buckets.get(k, 0)))
print('示例:')
for p in plan[:8]:
    print(f"  {p['good_id']} [{p['cate2']}] {p['old']} -> {p['new']}  {p['name']}")

json.dump(plan, open(os.path.join(P, '_step11_sales.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

DRY = os.environ.get('EXEC') != '1'
print('=== ' + ('DRY-RUN' if DRY else '执行') + ' ===')
ok = fail = 0
for i, p in enumerate(plan, 1):
    if DRY:
        ok += 1
        continue
    try:
        detail = (post('/good/detail', {'good_id': p['good_id']}).get('data') or {})
        gc = detail.get('good_cate') or []
        cate = [[1, gc[0].get('cate_id1'), gc[0].get('cate_id2')]] if gc else [[1, 0, 0]]
        body = build_body(detail, cate, fake_sale=p['new'])
        eres = post('/good/edit?good_id=' + str(p['good_id']), body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print('  x ' + str(p['good_id']) + ': ' + str(eres.get('msg')))
        time.sleep(0.08)
    except Exception as e:
        fail += 1
        print('  ERR ' + str(p['good_id']) + ': ' + str(e))
    if i % 100 == 0:
        print('  progress ' + str(i) + '/' + str(len(plan)) + ' ok=' + str(ok) + ' fail=' + str(fail), flush=True)
print('完成: ok=' + str(ok) + ' fail=' + str(fail))
