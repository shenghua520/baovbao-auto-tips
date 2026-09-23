# -*- coding: utf-8 -*-
"""Step 2b: 批量新建 101 个二级分类（含 sort 统一）"""
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

CAT_ID = {
    "学习文具": 1604, "体育用品": 1607, "少儿护理": 1612, "少儿穿戴": 1611,
    "少儿食品": 1609, "家庭日用": 1608, "读物潮玩": 1610, "米面油品": 1606,
    "家用电器": 1605,
}
CAT_ORDER = ["学习文具", "体育用品", "少儿护理", "少儿穿戴", "少儿食品", "家庭日用", "读物潮玩", "米面油品", "家用电器"]

# 当前后台二级
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
cur_children = {}   # (pid, name) -> cid
for c in r.get('data', []):
    for ch in c.get('children', []):
        cur_children[(c['cate_id'], ch['cate_name'])] = ch['cate_id']
print(f'当前二级总数: {len(cur_children)}')

# 目标：101 个二级
plan = []  # (cat, cid, pid, sort)
for ci, cat in enumerate(CAT_ORDER):
    subs = list(BRAND_LIB[cat].keys())
    for si, sub in enumerate(subs):
        plan.append((cat, sub, CAT_ID[cat], 100 + si * 10))
print(f'目标二级: {len(plan)} 个\n')

# 执行
created = updated = skipped = failed = 0
for cat, sub, pid, sort in plan:
    key = (pid, sub)
    if key in cur_children:
        # 已存在 → 只调 sort
        cid = cur_children[key]
        d = post('/goodsCate/edit', {
            "cate_id": cid, "cate_name": sub, "cate_pid": pid, "cate_type": 1,
            "cate_icon": "", "shop_type": 1, "is_display": 1, "period": 72,
            "sort": sort, "state": 1,
        })
        if d.get('code') == 0:
            updated += 1
            print(f"  ↻ {cat} > {sub} (id={cid}, sort={sort})")
        else:
            failed += 1
            print(f"  ✗ {cat} > {sub} edit失败: {d.get('msg')}")
    else:
        d = post('/goodsCate/add', {
            "cate_name": sub, "cate_pid": pid, "cate_type": 1,
            "cate_icon": "", "shop_type": 1, "is_display": 1, "period": 72,
            "sort": sort, "state": 1,
        })
        if d.get('code') == 0:
            created += 1
            print(f"  ＋ {cat} > {sub} (sort={sort})")
        else:
            failed += 1
            print(f"  ✗ {cat} > {sub} add失败: {d.get('msg')}")
    time.sleep(0.12)

print(f'\n完成: 新建={created} 已存在={updated} 失败={failed}')

# === 验证 ===
print('\n=== 验证：各大类下的二级 ===')
r2 = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
total = 0
for c in sorted([x for x in r2.get('data', []) if x.get('cate_pid') == 0], key=lambda x: x['sort']):
    chs = c.get('children', [])
    total += len(chs)
    print(f"\n【{c['cate_name']}】(id={c['cate_id']}, sort={c['sort']}) {len(chs)} 个二级")
    for ch in chs:
        print(f"    sort={ch['sort']:>4} | {ch['cate_id']} | {ch['cate_name']}")
print(f'\n二级总数: {total}')
