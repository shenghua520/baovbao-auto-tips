# -*- coding: utf-8 -*-
"""Step 7: 删除旧的 37 个二级分类（商品已迁完）"""
import requests, json, os, time

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}

def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()

OLD_NAMES = {'书写工具','纸品本册','文件管理','修正与粘贴','测量与裁剪','美术画材','财务办公',
             '运动鞋服','球类运动','健身训练','户外运动','运动配件',
             '洗发护发','身体清洁','口腔护理','面部护理',
             '童鞋','童装','书包配饰','儿童零食','乳品饮料','营养辅食',
             '清洁工具','收纳整理','厨房用品','居家织品','日用百货',
             '儿童读物','教辅工具','益智玩具','潮流玩具',
             '食用油','米面杂粮','调味干货','个护电器','厨房电器','生活电器'}

# 拉分类
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
to_del = []
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            if ch['cate_name'] in OLD_NAMES:
                to_del.append((c['cate_name'], ch['cate_name'], ch['cate_id']))

print(f'待删除旧二级: {len(to_del)}')
for c1, c2, cid in to_del:
    print(f'  {c1} > {c2} (id={cid})')

DRY = os.environ.get('EXEC') != '1'
print(f'\n=== {"DRY-RUN" if DRY else "执行删除"} ===')
ok = fail = 0
for c1, c2, cid in to_del:
    if DRY:
        ok += 1; continue
    d = post('/goodsCate/del', {"cate_id": cid})
    if d.get('code') == 0:
        ok += 1
        print(f'  ✓ 删除 {c1} > {c2}')
    else:
        fail += 1
        print(f'  ✗ 删除 {c1} > {c2}: {d.get("msg")}')
    time.sleep(0.15)
print(f'\n完成: ok={ok} fail={fail}')

# 验证
r2 = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
print('\n=== 最终 9 大类 + 二级 ===')
total = 0
for c in sorted([x for x in r2.get('data', []) if x.get('cate_pid') == 0], key=lambda x: x['sort']):
    chs = [ch for ch in c.get('children', [])]
    total += len(chs)
    print(f"\n【{c['cate_name']}】(sort={c['sort']}) {len(chs)} 二级")
    print('   ' + ' → '.join(ch['cate_name'] for ch in sorted(chs, key=lambda x: x['sort'])))
print(f'\n二级总数: {total}')
