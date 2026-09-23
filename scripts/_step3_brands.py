# -*- coding: utf-8 -*-
"""Step 3: 品牌 sort 重排 + 新建缺失品牌（L1+L2 cascader）"""
import requests, json, os, sys, time
sys.path.insert(0, r"C:\Users\shenghua\Desktop\新建文件夹")
from _brand_lib import BRAND_LIB

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
    r = requests.post(f"{BASE}{path}", data=payload, headers=H, timeout=20)
    try:
        return r.json()
    except Exception:
        return {"code": -1, "msg": r.text[:200]}

# === 1) 拉后台品牌 ===
r = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 500})
backend = {}
for b in r.get('data', []):
    if b.get('cate_pid') == 0:
        backend[b['cate_name']] = {
            'l1': b['cate_id'],
            'l2': (b['children'][0]['cate_id'] if b.get('children') else None),
            'sort': b['sort'],
        }
print(f'后台品牌: {len(backend)}')

# === 2) 计算品牌库的全局权重（取最优档位） ===
brand_rank = {}   # brand -> (档位, 出现小类数)
for cat, subs in BRAND_LIB.items():
    for sub, brands in subs.items():
        for idx, (b, lvl) in enumerate(brands):
            if b == '无品牌':
                continue
            cur = brand_rank.get(b)
            if cur is None or lvl < cur[0]:
                brand_rank[b] = (lvl, 1)
            else:
                brand_rank[b] = (cur[0], cur[1] + 1)

# 档位 → sort
SORT_MAP = {1: 10, 2: 30, 3: 60, 4: 200}
print(f'品牌库唯一品牌（不含无品牌）: {len(brand_rank)}')

# === 3) 分类：已有 / 新增 ===
existing = [b for b in brand_rank if b in backend]
new_brands = [b for b in brand_rank if b not in backend]
print(f'  已有: {len(existing)}')
print(f'  需新建: {len(new_brands)}')

# === 4) 已有品牌改 sort ===
print('\n=== 4a) 已有品牌改 sort ===')
ok = fail = 0
for b in existing:
    info = backend[b]
    target_sort = SORT_MAP.get(brand_rank[b][0], 200)
    if info['sort'] == target_sort:
        continue
    d = post('/goodsCate/edit', {
        "cate_id": info['l1'], "cate_name": b, "cate_pid": 0, "cate_type": 3,
        "cate_icon": "", "shop_type": 1, "is_display": 1, "period": 72,
        "sort": target_sort, "state": 1,
    })
    if d.get('code') == 0:
        ok += 1
    else:
        fail += 1
        print(f"  ✗ {b}: {d.get('msg')}")
    time.sleep(0.1)
print(f'  sort 更新: ok={ok} fail={fail}')

# === 5) 新建缺失品牌（L1 + L2） ===
print(f'\n=== 4b) 新建 {len(new_brands)} 个品牌 ===')
created = cfail = 0
for b in sorted(new_brands, key=lambda x: SORT_MAP.get(brand_rank[x][0], 200)):
    target_sort = SORT_MAP.get(brand_rank[b][0], 200)
    # add L1
    d1 = post('/goodsCate/add', {
        "cate_name": b, "cate_pid": 0, "cate_type": 3,
        "cate_icon": "", "shop_type": 1, "is_display": 1, "period": 72,
        "sort": target_sort, "state": 1,
    })
    if d1.get('code') != 0:
        cfail += 1
        print(f"  ✗ {b} L1: {d1.get('msg')}")
        time.sleep(0.1)
        continue
    # 查询 L1 id
    time.sleep(0.1)
    r2 = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 500})
    l1_id = None
    for x in r2.get('data', []):
        if x.get('cate_pid') == 0 and x['cate_name'] == b:
            l1_id = x['cate_id']
            break
    if not l1_id:
        cfail += 1
        print(f"  ✗ {b}: add 后查不到 id")
        continue
    # add L2
    d2 = post('/goodsCate/add', {
        "cate_name": b, "cate_pid": l1_id, "cate_type": 3,
        "cate_icon": "", "shop_type": 1, "is_display": 1, "period": 72,
        "sort": target_sort, "state": 1,
    })
    if d2.get('code') == 0:
        created += 1
        print(f"  ＋ {b} (L1={l1_id}, sort={target_sort})")
    else:
        cfail += 1
        print(f"  ✗ {b} L2: {d2.get('msg')}")
    time.sleep(0.12)

print(f'\n  新建: ok={created} fail={cfail}')

# === 6) 验证 ===
print('\n=== 验证 ===')
r3 = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 500})
l1s = [x for x in r3.get('data', []) if x.get('cate_pid') == 0]
print(f'  品牌总数: {len(l1s)}')
from collections import Counter
sc = Counter(x['sort'] for x in l1s)
for s in sorted(sc):
    print(f'    sort={s}: {sc[s]} 个')
