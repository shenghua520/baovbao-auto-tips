# -*- coding: utf-8 -*-
"""Step 4a: 拉取全部商品，分析结构"""
import requests, json, os, time

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {
    "uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html",
}

def post(path, payload):
    r = requests.post(f"{BASE}{path}", data=payload, headers=H, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"code": -1, "msg": r.text[:300]}

all_goods = []
page = 1
while True:
    d = post('/good/lists', {
        "page": page, "limit": 100, "type": "all", "good_source": 1,
        "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": [],
    })
    data = d.get('data') or []
    if not data:
        break
    all_goods.extend(data)
    print(f'  page {page}: +{len(data)} (累计 {len(all_goods)})')
    if len(data) < 100:
        break
    page += 1
    if page > 40:
        break
    time.sleep(0.15)

print(f'\n共拉取商品: {len(all_goods)}')
if all_goods:
    g = all_goods[0]
    print('\n=== 商品字段样例 ===')
    print(json.dumps({k: v for k, v in g.items() if k in ('good_id','good_name','good_brand','good_cate','good_source','state')}, ensure_ascii=False, indent=2)[:800])

json.dump(all_goods, open(os.path.join(P, '_goods_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n保存 _goods_all.json')

# 统计
with_brand = sum(1 for g in all_goods if g.get('good_brand'))
with_cate2 = 0
for g in all_goods:
    gc = g.get('good_cate') or []
    if gc:
        c = gc[0] if isinstance(gc[0], dict) else None
        if c and c.get('cate_id2'):
            with_cate2 += 1
print(f'已有品牌: {with_brand} / {len(all_goods)}')
print(f'已挂二级: {with_cate2}')
