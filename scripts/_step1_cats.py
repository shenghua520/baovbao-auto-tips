# -*- coding: utf-8 -*-
"""Step 1: 9 大类重排 sort + 1612 改名「个人洗护」→「少儿护理」
先备份，再执行，逐条验证。
"""
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
    r = requests.post(f"{BASE}{path}", data=payload, headers=H, timeout=20)
    try:
        return r.json()
    except Exception:
        return {"code": -1, "msg": r.text[:200]}

# === 备份 ===
print('=== 备份当前 9 大类 ===')
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
cats = r.get('data', [])
bak = os.path.join(P, 'review_assets', 'backup_cates_before_sort.json')
json.dump(cats, open(bak, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'  已备份 {len(cats)} 节点 → {bak}')
for c in cats:
    if c.get('cate_pid') == 0:
        print(f"    {c['cate_id']} | sort={c['sort']} | {c['cate_name']}")

# === 目标顺序 ===
# 用户指定: 学习文具 体育用品 少儿护理 少儿穿戴 少儿食品 家庭日用 读物潮玩 米面油品 家用电器
PLAN = [
    (1604, '学习文具', 1),
    (1607, '体育用品', 2),
    (1612, '少儿护理', 3),   # 原名"个人洗护"，改名
    (1611, '少儿穿戴', 4),
    (1609, '少儿食品', 5),
    (1608, '家庭日用', 6),
    (1610, '读物潮玩', 7),
    (1606, '米面油品', 8),
    (1605, '家用电器', 9),
]

print('\n=== 执行：重排 sort + 改名 ===')
ok = fail = 0
for cid, name, sort in PLAN:
    cur = next((c for c in cats if c['cate_id'] == cid), None)
    if not cur:
        print(f'  ✗ {cid} 不存在')
        fail += 1
        continue
    payload = {
        "cate_id": cid, "cate_name": name, "cate_pid": 0, "cate_type": 1,
        "cate_icon": cur.get('cate_icon', ''), "shop_type": 1, "is_display": 1,
        "period": 72, "sort": sort, "state": 1,
    }
    d = post('/goodsCate/edit', payload)
    status = '✓' if d.get('code') == 0 else '✗'
    if d.get('code') == 0:
        ok += 1
    else:
        fail += 1
    old_name = cur['cate_name']
    old_sort = cur['sort']
    print(f"  {status} {cid} {old_name}(sort{old_sort}) → {name}(sort{sort})  {d.get('msg','')}")
    time.sleep(0.15)

print(f'\n完成: ok={ok} fail={fail}')

# === 验证 ===
print('\n=== 验证结果 ===')
r2 = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
for c in sorted([x for x in r2.get('data', []) if x.get('cate_pid') == 0], key=lambda x: x['sort']):
    print(f"  sort={c['sort']} | {c['cate_id']} | {c['cate_name']}")
