"""Step 1 修复版：
1. 修复"待新加" bug（米面油系列列被误读成品牌）
2. 试改 brand sort 解决 1002 错误
3. 完整对比 v2 品牌 vs 后台品牌
"""
import requests, json, openpyxl, os, re
from collections import defaultdict

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

# === 1) 修复提取：分文件类型使用不同列 ===
p = r"C:\Users\shenghua\Desktop\新建文件夹"
FILE_TO_CAT_NAME = {
    '学习文具.xlsx': '学习文具', '体育用品.xlsx': '体育用品', '少儿穿戴.xlsx': '少儿穿戴',
    '读物潮玩.xlsx': '读物潮玩', '少儿食品.xlsx': '少儿食品', '家庭日用.xlsx': '家庭日用',
    '米面油品.xlsx': '米面油品', '家用电器.xlsx': '家用电器', '少儿护理.xlsx': '少儿护理',
}
# 文件级别 col 设置：brand 列在哪
FILE_BRAND_COL = {
    '学习文具.xlsx': 3, '体育用品.xlsx': 3, '少儿穿戴.xlsx': 3,
    '读物潮玩.xlsx': 3, '少儿食品.xlsx': 3, '家庭日用.xlsx': 1,
    '米面油品.xlsx': 1, '家用电器.xlsx': 3, '少儿护理.xlsx': 1,
}

def extract_v2(path, brand_col):
    """brand_col: 1 或 3"""
    wb = openpyxl.load_workbook(path, data_only=True)
    subs = []
    current = None
    for sn in wb.sheetnames:
        if '汇总' in sn: continue
        ws = wb[sn]
        for r in range(1, ws.max_row + 1):
            row = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            v1, v2, v3 = row[0], row[1], row[2]
            if not v1: continue
            # 分类标题
            if isinstance(v1, str) and re.match(r'^[一二三四五六七八九十]+、', v1) and len(v1) < 35 and (v2 is None or v2 == ''):
                current = re.sub(r'^[一二三四五六七八九十]+、', '', v1).strip()
                continue
            if isinstance(v1, str) and re.match(r'^\d+\.', v1) and len(v1) < 60 and (v2 is None or v2 == ''):
                current = re.sub(r'^\d+\.\s*', '', v1).strip()
                continue
            # 数据行：品牌按列取
            brand = None
            if brand_col == 3:
                if isinstance(v3, str) and v3.strip() and v3 not in ('品牌', '品类', '序号', '规格', '系列', '品牌/书名', '规格/内容'):
                    brand = v3.strip()
            else:
                # col 1
                if isinstance(v1, str) and v1.strip() and v1 not in ('品牌', '品类', '序号', '规格', '系列', '品牌/书名', '规格/内容', '微唯宝供货价', '京东供货价', '京东零售价', '微唯宝价', '京东价', '备注', '备注/报价说明'):
                    if v2 and isinstance(v2, str) and v2 not in ('品牌', '品类', '序号', '规格', '系列', '品牌/书名', '规格/内容'):
                        brand = v1.strip()
            if brand and current:
                subs.append((current, brand))
    return subs

v2_data = {}
for f, cat_name in FILE_TO_CAT_NAME.items():
    fp = os.path.join(p, f)
    if not os.path.exists(fp): continue
    subs = extract_v2(fp, FILE_BRAND_COL[f])
    v2_data[cat_name] = subs
    print(f'{f}: {len(subs)} SKU')

# 收集 v2 所有品牌
v2_brands = set()
for cat, subs in v2_data.items():
    for sub, brand in subs:
        v2_brands.add(brand)
print(f'\nv2 唯一品牌: {len(v2_brands)}')

# === 2) 拉后台品牌 ===
r = requests.post(f"{BASE}/goodsCate/lists", data={"cate_type": 3, "page": 1, "limit": 500}, headers=H, timeout=15).json()
backend_brands = [b for b in r.get("data", []) if b.get("cate_pid") == 0]
backend_names = {b["cate_name"]: b for b in backend_brands}
print(f'后台 L1 品牌: {len(backend_brands)}')

# === 3) 对比 ===
existing = v2_brands & set(backend_names.keys())
new_brands = v2_brands - set(backend_names.keys())
print(f'\n精确匹配: {len(existing)}')
print(f'v2 需新加: {len(new_brands)}: {sorted(new_brands)[:50]}')
print(f'后台有但 v2 没有: {len(set(backend_names.keys()) - v2_brands)}')

# === 4) 试改 brand sort 解决 1002 ===
# 1002 错误：试加 mall_id / mall_cate_id 字段
print('\n=== 试改 brand sort (修复版) ===')
sample_name = '中华'
if sample_name in backend_names:
    b = backend_names[sample_name]
    print(f'  完整后端数据: {json.dumps(b, ensure_ascii=False)[:500]}')
    # 后端 brand 字段样例：mall=护稚佳品, shop_type=1, is_display=1, period=72
    # 1002 错误 "上架的商城 必须为正整数" 可能需要 mall 字段
    payload = {
        "cate_id": b["cate_id"],
        "cate_name": b["cate_name"],
        "cate_pid": 0,
        "cate_type": 3,
        "sort": 20,
        "state": 1,
        "is_display": 1,
        "mall_cate_id": b.get("mall_cate_id", ""),
        "mall": "护稚佳品",  # 关键字段
    }
    print(f'  payload: {json.dumps(payload, ensure_ascii=False)[:400]}')
    r = requests.post(f"{BASE}/goodsCate/edit", data=payload, headers=H, timeout=15)
    print(f'  status: {r.status_code}')
    try:
        d = r.json()
        print(f'  body: {json.dumps(d, ensure_ascii=False)[:300]}')
    except:
        print(f'  body: {r.text[:300]}')

print('\n=== done ===')
