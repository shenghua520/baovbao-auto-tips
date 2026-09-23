# -*- coding: utf-8 -*-
"""Step 12: 大类一致性修正
1) 由后台结构建立「二级id → 父大类id」映射
2) 商品 cate_id1 != 父大类(cate_id2) 的，修正大类
3) 补充：商品名强信号（食品/护理/家电）修大类
"""
import requests, json, os, re, time
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
        "tag_ids": detail.get("tag_ids") or [],
        "fake_sale": detail.get("fake_sale") or 0,
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


# 二级 → 父大类
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
sub2parent = {}
parent_name = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        parent_name[c['cate_id']] = c['cate_name']
        for ch in c.get('children', []):
            sub2parent[ch['cate_id']] = c['cate_id']
print('二级→大类映射: ' + str(len(sub2parent)))

# 商品名强信号 → (大类, 二级名)
SIGNAL = [
    (['纯牛奶', '儿童奶', '成长奶', '酸奶', '奶酪棒', '乳酸菌'], 1609, '牛奶/奶制品'),
    (['每日坚果', '巴旦木', '核桃仁', '葡萄干', '新疆红枣'], 1609, '坚果/果干'),
    (['全谷物饼干', '儿童海苔', '鳕鱼肠', '果蔬干', '水果条', '婴儿米饼'], 1609, '健康零食'),
    (['纯果汁', 'NFC', '椰子水', '杏仁露', '核桃乳', '气泡水'], 1609, '天然饮品'),
    (['即食燕麦', '水果麦片', '谷物圈', '脆谷乐'], 1609, '早餐麦片'),
    (['钙铁锌', 'DHA软糖', '维生素软糖', '益生菌冻干'], 1609, '营养补充'),
    (['儿童有机酱油', '儿童减盐酱油', '儿童芝麻酱'], 1609, '儿童调味品'),
    (['儿童牙膏', '婴幼儿牙膏', '儿童益生菌牙膏', '儿童健齿牙膏'], 1612, '儿童牙膏'),
    (['儿童牙刷', '婴幼儿牙刷', '儿童声波电动牙刷'], 1612, '儿童牙刷'),
    (['儿童氨基酸洗发水', '儿童洗发水', '婴幼儿洗发'], 1612, '儿童洗发水'),
    (['儿童沐浴露', '婴幼儿沐浴露', '洗发沐浴二合一'], 1612, '儿童沐浴露'),
    (['儿童洗面奶', '婴幼儿洗面奶'], 1612, '儿童洗面奶'),
    (['儿童面霜', '儿童润肤', '婴儿润肤', '儿童润肤霜'], 1612, '儿童面霜'),
    (['儿童润唇膏', '婴幼儿润唇膏'], 1612, '儿童润唇膏'),
    (['儿童洗手液', '婴幼儿洗手液', '儿童泡沫洗手液'], 1612, '儿童洗手液'),
    (['儿童防晒乳', '儿童防晒霜', '儿童防晒露'], 1612, '儿童防晒'),
    (['婴儿护臀膏'], 1612, '儿童护臀膏'),
    (['儿童洗衣液', '婴幼儿洗衣液'], 1612, '儿童洗衣液'),
    (['护眼台灯', '学习台灯'], 1605, '护眼台灯'),
    (['加湿器'], 1605, '加湿器'),
    (['电饭煲', '电压力锅'], 1605, '电饭煲'),
    (['破壁机', '便携榨汁机', '豆浆机'], 1605, '破壁机'),
    (['扫地机器人', '拖地机器人'], 1605, '扫地机器人'),
    (['电吹风', '高速电吹风'], 1605, '电吹风'),
    (['净水器', '净水机'], 1605, '净水器'),
    (['非转基因大豆油', '一级大豆油', '压榨大豆油'], 1606, '大豆油'),
    (['花生油'], 1606, '花生油'),
    (['菜籽油'], 1606, '菜籽油'),
    (['橄榄油'], 1606, '橄榄油'),
    (['调和油'], 1606, '调和油'),
    (['麦芯粉', '饺子粉', '中筋面粉', '多用途面粉'], 1606, '中筋面粉'),
    (['东北大米', '长粒香', '珍珠米', '丝苗米', '五常大米'], 1606, '长粒香米'),
    (['计数跳绳', '中考训练跳绳', '竞速跳绳'], 1607, '跳绳'),
    (['护脊书包', '儿童书包', '双肩包'], 1611, '书包'),
]

# 拉商品
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

# 目标二级 id
tgt2 = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            tgt2[(c['cate_id'], ch['cate_name'])] = ch['cate_id']

todo = []
for g in all_g:
    gc = g.get('good_cate') or []
    if not gc:
        continue
    c1, c2 = gc[0].get('cate_id1'), gc[0].get('cate_id2')
    name = g.get('good_name') or ''
    why = None
    new1, new2 = c1, c2
    # 1) 二级归属大类不一致
    if c2 in sub2parent and sub2parent[c2] != c1:
        new1 = sub2parent[c2]
        why = '二级归属修正'
    # 2) 商品名强信号
    if not why or why == '二级归属修正':
        for kws, tc1, tname in SIGNAL:
            if any(k in name for k in kws):
                nid = tgt2.get((tc1, tname))
                if nid and (tc1 != new1 or nid != new2):
                    new1, new2 = tc1, nid
                    why = '商品名强信号' if why != '二级归属修正' else why
                break
    if why and (new1 != c1 or new2 != c2):
        todo.append({'good_id': g['good_id'], 'name': name[:42], 'why': why,
                     'old': [c1, gc[0].get('cate2')], 'new': [new1, new2]})

print('待改: ' + str(len(todo)))
for k, n in Counter(t['why'] for t in todo).most_common():
    print('  ' + k + ': ' + str(n))
for t in todo[:12]:
    print(f"    {t['good_id']} [{t['why']}] {t['old'][0]}→{t['new'][0]} {t['name'][:34]}")
json.dump(todo, open(os.path.join(P, '_step12_changes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

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
