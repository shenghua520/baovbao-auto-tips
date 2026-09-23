"""探查：9 大类、当前二级、当前品牌 sort 分布"""
import requests, json
from collections import Counter

with open(r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json", encoding='utf-8') as f:
    auth = json.load(f)
BASE = "https://mall.baovbao.com/admin"
H = {
    "uid": str(auth["admin_id"]),
    "sid": str(auth["sid"]),
    "token": auth["token"],
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Origin": "https://mall.baovbao.com",
    "Referer": "https://mall.baovbao.com/admin/index.html",
}

# 1) 9 大类 + 全部二级
r1 = requests.post(f"{BASE}/goodsCate/lists", data={"cate_type": 1, "page": 1, "limit": 500}, headers=H, timeout=15).json()
cats = r1.get("data", [])
print('=== 当前 9 大类（后台真实） ===')
for c in cats:
    if c.get("cate_pid") == 0:
        n = len(c.get("children", []))
        print(f"  {c['cate_id']:>5} | sort={c['sort']:>3} | {c['cate_name']} | {n} 二级")

print('\n=== 全部二级 (按 sort 排序) ===')
subs = []
for c in cats:
    if c.get("cate_pid") == 0:
        for ch in c.get("children", []):
            subs.append((ch.get("sort", 0), ch["cate_id"], c["cate_name"], ch["cate_name"]))
subs.sort()
for s, cid, p, n in subs:
    print(f"  sort={s:>3} | {cid} | {p} > {n}")

# 2) 品牌 sort 分布
r2 = requests.post(f"{BASE}/goodsCate/lists", data={"cate_type": 3, "page": 1, "limit": 500}, headers=H, timeout=15).json()
brands = r2.get("data", [])
print(f'\n=== 品牌 {len(brands)} 个，sort 分布 ===')
sorts = Counter(b.get("sort", 0) for b in brands)
for s, n in sorted(sorts.items()):
    print(f"  sort={s:>4}: {n} 品牌")

print('\n=== sort=20 的品牌（推测头部）===')
for b in brands:
    if b.get("sort") == 20:
        print(f"  {b['cate_id']} | {b['cate_name']}")

print('\n=== sort=999 的品牌（推测无商品/无品牌）===')
for b in brands:
    if b.get("sort") == 999:
        print(f"  {b['cate_id']} | {b['cate_name']}")
