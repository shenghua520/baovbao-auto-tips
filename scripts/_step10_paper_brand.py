# -*- coding: utf-8 -*-
"""Step 10: 1) 新建「纸品」二级并把纸品类商品从「作业本」迁出
            2) 用「品牌反查」修正商品大类
"""
import requests, json, os, re, time, sys
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


def build_body(detail, good_cate):
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
        "tag_ids": detail.get("tag_ids") or [], "fake_sale": detail.get("fake_sale") or 0,
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


# ========== 1) 新建「纸品」二级 ==========
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
sub = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            sub[(c['cate_id'], ch['cate_name'])] = ch['cate_id']

PAPER_EXIST = sub.get((1604, '纸品'))
if not PAPER_EXIST:
    d = post('/goodsCate/add', {"cate_name": "纸品", "cate_pid": 1604, "cate_type": 1,
                                 "cate_icon": "", "shop_type": 1, "is_display": 1,
                                 "period": 72, "sort": 145, "state": 1})
    print('建 纸品:', d.get('code'), d.get('msg'))
    time.sleep(0.3)
    r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
    for c in r.get('data', []):
        if c.get('cate_pid') == 0:
            for ch in c.get('children', []):
                sub[(c['cate_id'], ch['cate_name'])] = ch['cate_id']
else:
    print('纸品 已存在 id=' + str(PAPER_EXIST))
PAPER_ID = sub.get((1604, '纸品'))

# ========== 2) 品牌 → 大类 反查表 ==========
BRAND2CAT = {
    # 少儿食品
    '伊利': 1609, '蒙牛': 1609, '光明': 1609, '君乐宝': 1609, '三元': 1609, '简爱': 1609,
    '卡士': 1609, '乐纯': 1609, '妙可蓝多': 1609, '百吉福': 1609, '认养一头牛': 1609,
    '洽洽': 1609, '三只松鼠': 1609, '良品铺子': 1609, '百草味': 1609, '沃隆': 1609,
    '西域果园': 1609, '楼兰蜜语': 1609, '小皮': 1609, '宝贝顾问': 1609, '力诚': 1609,
    '农夫山泉': 1609, '汇源': 1609, '露露': 1609, '六个核桃': 1609, '元气森林': 1609,
    '桂格': 1609, '西麦': 1609, '卡乐比': 1609, '家乐氏': 1609, '雀巢': 1609, '欧扎克': 1609,
    '汤臣倍健': 1609, '童年时光': 1609, '斯维斯': 1609, '禾博士': 1609, '自然之宝': 1609,
    '禾然': 1609, '六月鲜': 1609, '三井': 1609, '丸庄': 1609,
    # 少儿护理
    '好孩子': 1612, '青蛙王子': 1612, '云南白药': 1612, '舒客': 1612, '纳爱斯': 1612,
    '贝亲': 1612, '红色小象': 1612, '启初': 1612, '戴可思': 1612, '郁美净': 1612,
    '丝塔芙': 1612, '妙思乐': 1612, '安热沙': 1612, '红贝缇': 1612, '五羊': 1612, '保宁': 1612,
    '兔头妈妈': 1612, '艾惟诺': 1612, '松达': 1612, '贝德美': 1612, '子初': 1612, '欧乐': 1612,
    # 家用电器
    '欧普': 1605, '明基': 1605, '福库': 1605, '维他密斯': 1605, '摩飞': 1605,
    '科沃斯': 1605, '石头': 1605, '云鲸': 1605, '追觅': 1605, '徕芬': 1605, '飞科': 1605,
    '安吉尔': 1605, '沁园': 1605, '史密斯': 1605, '亚都': 1605, '好视力': 1605, '孩视宝': 1605,
    # 米面油品
    '金龙鱼': 1606, '福临门': 1606, '香满园': 1606, '九三': 1606, '鲁花': 1606,
    '胡姬花': 1606, '刀唛': 1606, '金浩': 1606, '道道全': 1606, '天助': 1606,
    '西王': 1606, '多力': 1606, '长寿花': 1606, '欧丽薇兰': 1606, '贝蒂斯': 1606, '品利': 1606,
    '十月稻田': 1606, '柴火大院': 1606, '太粮': 1606, '圣上壹品': 1606, '北纯': 1606,
    '香纳兰': 1606, '新良': 1606, '王后': 1606, '美玫': 1606, '北大荒': 1606, '三象': 1606,
    '五得利': 1606, '香雪': 1606, '中粮': 1606, '国宝': 1606, '泰山': 1606,
    # 读物潮玩
    '泡泡玛特': 1610, '52TOYS': 1610, '若来': 1610, '卡游': 1610, '万代': 1610, 'TOPTOY': 1610,
    '弥鹿': 1610, '图益': 1610, '邦臣小红花': 1610, '可来赛': 1610, '贝乐星': 1610,
    '曲一线': 1610, '金星教育': 1610, '人教': 1610, '华东师大': 1610, '开明出版社': 1610,
    '接力出版社': 1610, '明天出版社': 1610, '童趣': 1610, '中信出版': 1610,
    '商务印书馆': 1610, '外研社': 1610, '华语教学': 1610, '华阳文化': 1610,
    '经纶文化': 1610, '时代华语': 1610, '蒲公英': 1610, '信谊': 1610, '爱心树': 1610,
    '蒲蒲兰': 1610, '启发文化': 1610, 'DK': 1610, '圣手': 1610, '萌趣': 1610,
}
CAT_NAME = {1604: '学习文具', 1605: '家用电器', 1606: '米面油品', 1607: '体育用品',
            1608: '家庭日用', 1609: '少儿食品', 1610: '读物潮玩', 1611: '少儿穿戴', 1612: '少儿护理'}

# ========== 3) 拉商品，计算需改的 ==========
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

PAPER_KW = ['打印纸', '复印纸', '相纸', '相片纸', '标签纸', '热敏', '收银纸', '传真纸', '针式', '电脑打印纸', '不干胶', '条码纸', '铜版纸', '打印纸']
todo = []
for g in all_g:
    gc = g.get('good_cate') or []
    if not gc:
        continue
    c1, c2 = gc[0].get('cate_id1'), gc[0].get('cate_id2')
    name = g.get('good_name') or ''
    brand = ''
    gb = g.get('good_brand') or []
    if gb and gb[0].get('brand1'):
        brand = gb[0]['brand1']
    new_c1, new_c2, why = c1, c2, ''
    # 1) 纸品类从「作业本」迁到「纸品」
    if c2 == sub.get((1604, '作业本')) and any(k in name for k in PAPER_KW):
        new_c1, new_c2, why = 1604, PAPER_ID, '纸品'
    # 2) 品牌反查改大类
    elif brand in BRAND2CAT:
        tgt1 = BRAND2CAT[brand]
        if tgt1 != c1:
            # 找该大类下的合适二级
            cur2name = gc[0].get('cate2')
            new_c1 = tgt1
            # 二级名如果在目标大类下也存在于则沿用
            cand = sub.get((tgt1, cur2name))
            if cand:
                new_c2 = cand
            else:
                # 用品牌在大类里的默认二级
                default2 = {1609: '健康零食', 1612: '儿童面霜', 1605: '电饭煲', 1606: '大豆油', 1610: '益智拼图'}.get(tgt1)
                new_c2 = sub.get((tgt1, default2), cur2name)
            why = '品牌反查'
    if why and (new_c1 != c1 or new_c2 != c2):
        todo.append({'good_id': g['good_id'], 'name': name[:40], 'brand': brand,
                     'old': [c1, gc[0].get('cate2')], 'new': [new_c1, new_c2], 'why': why})

print('待改: ' + str(len(todo)))
for k, n in Counter(t['why'] for t in todo).most_common():
    print('  ' + k + ': ' + str(n))
print('  纸品迁入: ' + str(sum(1 for t in todo if t['why'] == '纸品')))
print('  品牌反查大类: ' + str(sum(1 for t in todo if t['why'] == '品牌反查')))
for t in todo[:10]:
    print(f"    {t['good_id']} [{t['why']}] {t['brand']} {t['old'][0]}→{t['new'][0]} {t['name']}")

json.dump(todo, open(os.path.join(P, '_step10_changes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

DRY = os.environ.get('EXEC') != '1'
print('=== ' + ('DRY-RUN' if DRY else '执行') + ' ===')
ok = fail = 0
for i, t in enumerate(todo, 1):
    if DRY:
        ok += 1
        continue
    try:
        detail = (post('/good/detail', {'good_id': t['good_id']}).get('data') or {})
        body = build_body(detail, [[1, t['new'][0], t['new'][1]]])
        eres = post('/good/edit?good_id=' + str(t['good_id']), body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print('  x ' + str(t['good_id']) + ': ' + str(eres.get('msg')))
        time.sleep(0.08)
    except Exception as e:
        fail += 1
        print('  ERR ' + str(t['good_id']) + ': ' + str(e))
    if i % 100 == 0:
        print('  progress ' + str(i) + '/' + str(len(todo)) + ' ok=' + str(ok) + ' fail=' + str(fail), flush=True)
print('完成: ok=' + str(ok) + ' fail=' + str(fail))
