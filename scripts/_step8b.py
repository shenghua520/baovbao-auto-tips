# -*- coding: utf-8 -*-
"""Step 8b: 迁移 source=3 的 14 个商品 + 删除最后 2 个旧二级"""
import requests, json, time, sys, os
sys.path.insert(0, r"C:\Users\shenghua\Desktop\新建文件夹")
from _step6b import post, build_body

# 二级 id
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
ids = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            ids[(c['cate_id'], ch['cate_name'])] = ch['cate_id']

OIL_SUBS = [(('菜籽油'), ids[(1606, '菜籽油')]), (('花生油'), ids[(1606, '花生油')]),
            (('大豆油'), ids[(1606, '大豆油')]), (('橄榄油'), ids[(1606, '橄榄油')]),
            (('玉米', '葵花'), ids[(1606, '玉米葵花油')]), (('调和',), ids[(1606, '调和油')])]

TARGET_OLD = {2182, 2178}
found = []
for src in (3, 1):
    page = 1
    while True:
        d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": src,
                                  "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
        data = d.get('data') or []
        if not data:
            break
        for g in data:
            for gc in (g.get('good_cate') or []):
                if gc.get('cate_id2') in TARGET_OLD:
                    name = g.get('good_name') or ''
                    # 决定目标二级
                    if gc['cate_id2'] == 2182:   # 乳品饮料
                        tgt2 = ids[(1609, '牛奶/奶制品')]
                        tgt1 = 1609
                    else:                         # 食用油 → 按名细分
                        tgt1 = 1606
                        tgt2 = ids[(1606, '大豆油')]
                        for kws, sid in OIL_SUBS:
                            if any(k in name for k in kws):
                                tgt2 = sid
                                break
                    found.append({'good_id': g['good_id'], 'src': src, 'name': name[:45],
                                  'old2': gc['cate_id2'], 'new': [tgt1, tgt2]})
                    break
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.1)

print(f'待迁移(含 src=3): {len(found)}')
for f in found:
    print(f"  {f['good_id']} {f['old2']} -> {f['new'][1]}  {f['name']}")

DRY = os.environ.get('EXEC') != '1'
print('=== ' + ('DRY-RUN' if DRY else '执行') + ' ===')
ok = fail = 0
for f in found:
    if DRY:
        ok += 1
        continue
    try:
        detail = (post('/good/detail', {'good_id': f['good_id']}).get('data') or {})
        body = build_body(detail, [[1, f['new'][0], f['new'][1]]])
        eres = post('/good/edit?good_id=' + str(f['good_id']), body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print('  x', f['good_id'], eres.get('msg'))
        time.sleep(0.12)
    except Exception as e:
        fail += 1
        print('  ERR', f['good_id'], e)
print('迁移: ok=' + str(ok) + ' fail=' + str(fail))

# 删除最后 2 个
if not DRY:
    for cid, nm in [(2182, '少儿食品>乳品饮料'), (2178, '米面油品>食用油')]:
        d = post('/goodsCate/del', {"cate_id": cid})
        print(f'  删 {nm}: ' + ('OK' if d.get('code') == 0 else 'FAIL ' + str(d.get('msg'))))
        time.sleep(0.2)
