# -*- coding: utf-8 -*-
"""Step 8: 清理最后 2 个旧二级（乳品饮料、食用油）"""
import requests, json, os, time, sys
sys.path.insert(0, r"C:\Users\shenghua\Desktop\新建文件夹")
from _step6b import post, build_body

# 找这 2 个二级
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
targets = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            if ch['cate_name'] in ('乳品饮料', '食用油'):
                targets[ch['cate_id']] = (c['cate_id'], c['cate_name'], ch['cate_name'])
print('待清理二级:', targets)

# 目标新二级 id
new_ids = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            if ch['cate_name'] == '牛奶/奶制品' and c['cate_id'] == 1609:
                new_ids['乳品饮料'] = ch['cate_id']
            if ch['cate_name'] == '大豆油' and c['cate_id'] == 1606:
                new_ids['食用油'] = ch['cate_id']
print('目标新二级:', new_ids)

# 拉商品找挂在这 2 个下的
all_g, page = [], 1
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

todo = []
for g in all_g:
    gc = g.get('good_cate') or []
    if gc and gc[0].get('cate_id2') in targets:
        old_c2 = gc[0]['cate_id2']
        c1name = targets[old_c2][1]
        oldname = targets[old_c2][2]
        nid = new_ids.get(oldname)
        if nid:
            todo.append({'good_id': g['good_id'], 'name': (g.get('good_name') or '')[:45],
                         'old': oldname, 'new': [gc[0]['cate_id1'], nid]})

print('待迁移:', len(todo))
for t in todo:
    print('  ', t['good_id'], t['old'], '->', t['new'][1], t['name'])

DRY = os.environ.get('EXEC') != '1'
print('=== ' + ('DRY-RUN' if DRY else '执行') + ' ===')
ok = fail = 0
for t in todo:
    if DRY:
        ok += 1
        continue
    try:
        detail = (post('/good/detail', {'good_id': t['good_id']}).get('data') or {})
        body = build_body(detail, [[1, t['new'][0], t['new'][1]]])
        eres = post('/good/edit?good_id=' + str(t['good_id']), body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print('  x', t['good_id'], eres.get('msg'))
        time.sleep(0.1)
    except Exception as e:
        fail += 1
        print('  ERR', t['good_id'], e)
print('迁移完成: ok=' + str(ok) + ' fail=' + str(fail))

# 删除这 2 个二级
if not DRY:
    for cid, (c1, c1n, c2n) in targets.items():
        d = post('/goodsCate/del', {"cate_id": cid})
        print(f'  删 {c1n} > {c2n}: ' + ('✓' if d.get('code') == 0 else '✗ ' + str(d.get('msg'))))
        time.sleep(0.15)
