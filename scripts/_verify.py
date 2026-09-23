# -*- coding: utf-8 -*-
"""最终验证：拉后台真实状态，统计 9 大类/二级/品牌/商品分布"""
import requests, json, os, time
from collections import Counter, defaultdict

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}

def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()

# 1) 分类
cats = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500}).get('data', [])
l1 = sorted([c for c in cats if c.get('cate_pid') == 0], key=lambda x: x['sort'])
print('=== 9 大类 ===')
for c in l1:
    print(f"  sort={c['sort']} | {c['cate_id']} | {c['cate_name']} | {len(c.get('children',[]))} 二级")

# 2) 品牌
brands = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 600}).get('data', [])
bl1 = [b for b in brands if b.get('cate_pid') == 0]
print(f'\n=== 品牌: {len(bl1)} ===')
sc = Counter(b['sort'] for b in bl1)
for s in sorted(sc)[:8]:
    print(f'  sort={s}: {sc[s]}')

# 3) 商品
goods = json.load(open(os.path.join(P, '_goods_all.json'), encoding='utf-8'))
# 需要重新拉（因为已改）
all_g = []
page = 1
while True:
    d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": 1,
                              "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
    data = d.get('data') or []
    if not data:
        break
    all_g.extend(data)
    if len(data) < 100 or page > 40:
        break
    page += 1
    time.sleep(0.1)
print(f'\n=== 商品: {len(all_g)} ===')

# 二级分布
c2_dist = Counter()
c1_dist = Counter()
no_cate2 = 0
for g in all_g:
    gc = g.get('good_cate') or []
    if gc:
        c1_dist[gc[0].get('cate1')] += 1
        if gc[0].get('cate_id2'):
            c2_dist[(gc[0].get('cate1'), gc[0].get('cate2'))] += 1
        else:
            no_cate2 += 1
    else:
        no_cate2 += 1

print('\n=== 大类商品分布 ===')
for k, n in c1_dist.most_common():
    print(f'  {k}: {n}')

print(f'\n=== 二级覆盖: {sum(c2_dist.values())} 有二级 / {no_cate2} 无二级 ===')
for (c1, c2), n in c2_dist.most_common(25):
    print(f'  {c1} > {c2}: {n}')

# 品牌分布
br_dist = Counter()
no_brand = 0
for g in all_g:
    gb = g.get('good_brand') or []
    if gb and gb[0].get('brand1') and gb[0]['brand1'] != '无品牌':
        br_dist[gb[0]['brand1']] += 1
    else:
        no_brand += 1
print(f'\n=== 品牌覆盖: {sum(br_dist.values())} 有品牌 / {no_brand} 无品牌 ===')
for k, n in br_dist.most_common(20):
    print(f'  {k}: {n}')

# 保存
json.dump({'cats': l1, 'brands': bl1, 'goods': all_g}, open(os.path.join(P, 'review_assets', 'final_state.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\n保存 final_state.json')
