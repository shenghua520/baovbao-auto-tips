# -*- coding: utf-8 -*-
"""深查：谁挂在 乳品饮料(2182) / 食用油(2178) 下（含 all source + 所有 cate 元素）"""
import requests, json, time, sys

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}


def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()


TARGET = {2182, 2178}
found = []
for src in (1, 3, 0):
    page = 1
    while True:
        d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": src,
                                  "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
        data = d.get('data') or []
        if not data:
            break
        for g in data:
            for gc in (g.get('good_cate') or []):
                if gc.get('cate_id2') in TARGET:
                    found.append({'good_id': g['good_id'], 'src': src, 'name': (g.get('good_name') or '')[:45],
                                  'cate2': gc.get('cate2'), 'cate_id2': gc.get('cate_id2'), 'state': g.get('state')})
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.1)
    print(f'source={src} 扫描完，命中 {len(found)}')
    if found:
        break

print(f'\n挂在 2182/2178 下的商品: {len(found)}')
for f in found:
    print(f"  id={f['good_id']} src={f['src']} state={f['state']} {f['cate2']}({f['cate_id2']}) {f['name']}")

# 直接用 detail 查这两个 cate 的商品（换一种 API 思路：用 cate 过滤）
print('\n=== 尝试 cate 过滤 API ===')
for cid in TARGET:
    d = post('/good/lists', {"page": 1, "limit": 100, "type": "all", "good_source": "all",
                              "good_field": "good_name", "good_value": "", "brand_id": [],
                              "createtime": [], "cate_id2": cid})
    data = d.get('data') or []
    print(f'  cate_id2={cid}: {len(data)} 条')
    for g in data[:5]:
        print(f"    {g['good_id']} {g.get('good_name','')[:40]}")
