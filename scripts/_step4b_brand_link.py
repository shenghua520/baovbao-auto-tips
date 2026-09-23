# -*- coding: utf-8 -*-
"""Step 4b: 品牌关联（按商品名匹配新品牌库，只改有变化的）"""
import requests, json, os, time

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {
    "uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html",
}

def post(path, payload):
    """good/edit 需要 JSON body（嵌套数组）"""
    r = requests.post(f"{BASE}{path}", json=payload, headers=H, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"code": -1, "msg": r.text[:300]}

def strip_url(u):
    if not u:
        return ""
    s = str(u)
    if s.startswith("http://") or s.startswith("https://"):
        rest = s.split("//", 1)[-1]
        slash = rest.find("/")
        return rest[slash:] if slash >= 0 else ""
    return s

def build_body(detail, good_cate, good_brand):
    skus = []
    seen = set()
    for s in detail.get("skus") or []:
        key = (s.get("spec_val1"), s.get("spec_val2"), s.get("spec_val3"))
        if key in seen:
            continue
        seen.add(key)
        o = dict(s)
        o["cover_img"] = strip_url(o.get("cover_img"))
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
    return {
        "good_name": detail.get("good_name") or "",
        "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"),
        "good_type": detail.get("good_type"),
        "good_brand": good_brand,
        "good_cate": good_cate,
        "tag_ids": detail.get("tag_ids") or [],
        "fake_sale": detail.get("fake_sale") or 0,
        "good_desc": detail.get("good_desc") or "",
        "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0,
        "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0,
        "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": strip_url(detail.get("cover_img")),
        "wheel_img": [strip_url(x) for x in (detail.get("wheel_img") or [])],
        "wheel_img_arr": [{"name": "", "url": strip_url(x)} for x in (detail.get("wheel_img") or [])],
        "video_type": detail.get("video_type") or 1,
        "video_url": strip_url(detail.get("video_url") or ""),
        "video_url_upload": detail.get("video_url_upload") or "",
        "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": [strip_url(x) for x in (detail.get("detail_img") or [])],
        "detail_img_arr": [{"name": "", "url": strip_url(x)} for x in (detail.get("detail_img") or [])],
        "content": detail.get("content") or "",
        "recommend": detail.get("recommend") or "",
        "sort": detail.get("sort") if detail.get("sort") is not None else 100,
        "unit": detail.get("unit") or "",
        "buy_min": detail.get("buy_min") or 1,
        "buy_max": detail.get("buy_max") or 1000,
        "spec_name1": detail.get("spec_name1") or "规格",
        "spec_name2": detail.get("spec_name2") or "",
        "spec_name3": detail.get("spec_name3") or "",
        "spec_name4": detail.get("spec_name4") or "",
        "skus": skus,
        "stock_warn": detail.get("stock_warn") or 0,
    }

# === 拉后台品牌 → 映射 ===
r = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 600})
brand_map = {}
for b in r.get('data', []):
    if b.get('cate_pid') == 0 and b.get('children'):
        brand_map[b['cate_name']] = (b['cate_id'], b['children'][0]['cate_id'])
print(f'后台品牌: {len(brand_map)}')

# 只用「规范品牌库」的品牌匹配（避免匹配到后台脏名如 TANGO/paperb）
import sys
sys.path.insert(0, P)
from _brand_lib import BRAND_LIB
LIB_BRANDS = set()
for cat, subs in BRAND_LIB.items():
    for sub, brands in subs.items():
        for b, w in brands:
            if b != '无品牌':
                LIB_BRANDS.add(b)
print(f'规范品牌库: {len(LIB_BRANDS)}')

# 易误匹配的品牌（商品名里会撞普通词），禁用自动匹配
DISABLE = {'729', 'DK', '3M', 'UV100', '人教', '童趣', '蝴蝶', '樱花', '泰格', '玛丽',
           '天堂', '小米', '英雄', '白雪', '真彩', '红旗', '金号'}
brand_names = [b for b in sorted([b for b in LIB_BRANDS if b in brand_map], key=len, reverse=True)
               if b not in DISABLE]
print(f'可匹配品牌: {len(brand_names)}（已排除 {len(DISABLE)} 个易误匹配）')

goods = json.load(open(os.path.join(P, '_goods_all.json'), encoding='utf-8'))
print(f'商品: {len(goods)}')

# === 计算变化 ===
NO_BRAND_ID = 1757  # 后台"无品牌"
changes = []
for g in goods:
    name = g.get('good_name') or ''
    cur = g.get('good_brand') or []
    cur_bid = None
    if cur and isinstance(cur[0], dict):
        cur_bid = cur[0].get('brand_id1')
    # 只处理「无品牌/空品牌」的商品（已有品牌的保持不动，避免误覆盖）
    if cur_bid not in (None, 0, NO_BRAND_ID):
        continue
    # 匹配（只用规范品牌库，长度降序）
    hit = None
    for bn in brand_names:
        if bn in name:
            hit = bn
            break
    if not hit:
        continue
    new_pair = brand_map[hit]
    changes.append({'good_id': g['good_id'], 'name': name[:60], 'brand': hit,
                    'old_bid1': cur_bid, 'new': list(new_pair)})

print(f'需改品牌: {len(changes)} / {len(goods)}')
print('\n前 20 条:')
for c in changes[:20]:
    print(f"  {c['good_id']} {c['brand']:8s} {c['old_bid1']} → {c['new'][0]}  {c['name'][:40]}")

json.dump(changes, open(os.path.join(P, '_brand_changes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n保存 _brand_changes.json')

# === 执行 ===
DRY = os.environ.get('EXEC') != '1'
print(f'\n=== {"DRY-RUN" if DRY else "执行"} ===')
ok = fail = 0
for i, c in enumerate(changes, 1):
    if DRY:
        ok += 1
        continue
    gid = c['good_id']
    try:
        dres = post('/good/detail', {'good_id': gid})
        detail = dres.get('data') or {}
        # 保留原 cate
        gc = detail.get('good_cate') or []
        cate = [[1, gc[0].get('cate_id1'), gc[0].get('cate_id2')]] if gc else [[1, 0, 0]]
        body = build_body(detail, cate, [c['new']])
        eres = post(f'/good/edit?good_id={gid}', body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print(f"  ✗ {gid}: {eres.get('msg')}")
        time.sleep(0.1)
    except Exception as e:
        fail += 1
        print(f"  ERR {gid}: {e}")
    if i % 100 == 0:
        print(f'  进度 {i}/{len(changes)} ok={ok} fail={fail}', flush=True)

print(f'\n完成: ok={ok} fail={fail}')
