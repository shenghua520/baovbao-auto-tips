# -*- coding: utf-8 -*-
"""分析剩余商品（还在旧二级的）+ 旧→新二级映射迁移"""
import requests, json, os, time
from collections import Counter, defaultdict

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}

def strip_url(u):
    if not u: return ""
    s = str(u)
    if s.startswith("http://") or s.startswith("https://"):
        rest = s.split("//", 1)[-1]; slash = rest.find("/")
        return rest[slash:] if slash >= 0 else ""
    return s

def build_body(detail, good_cate):
    skus = []; seen = set()
    for s in detail.get("skus") or []:
        key = (s.get("spec_val1"), s.get("spec_val2"), s.get("spec_val3"))
        if key in seen: continue
        seen.add(key)
        o = dict(s); o["cover_img"] = strip_url(o.get("cover_img"))
        if not o.get("pay_setting"): o["pay_setting"] = [{"checked":0,"account_id":"","money":0}]
        if not o.get("spec_val1"):
            sd = o.get("spec_data") or []
            o["spec_val1"] = (sd[0].get("val") if sd else "默认") or "默认"
        skus.append(o)
    if not skus:
        skus = [{"cover_img":"","spec_val1":"默认","spec_val2":"","unit_quatity":1,
                 "cost_price":detail.get("cost_price") or 0,"sale_price":detail.get("sale_price") or 0,
                 "crossed_price":detail.get("crossed_price") or 0,"stock":0,"state":1,
                 "pay_setting":[{"checked":0,"account_id":"","money":0}]}]
    raw = detail.get("good_brand") or []; mapped = []
    for b in raw:
        if isinstance(b, dict): mapped.append([b.get("brand_id1") or "", b.get("brand_id2") or ""])
        elif isinstance(b, (list, tuple)): mapped.append([b[0] if b else "", b[1] if len(b)>1 else ""])
    return {
        "good_name": detail.get("good_name") or "", "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"), "good_type": detail.get("good_type"),
        "good_brand": mapped or [["",""]], "good_cate": good_cate,
        "tag_ids": detail.get("tag_ids") or [], "fake_sale": detail.get("fake_sale") or 0,
        "good_desc": detail.get("good_desc") or "", "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0, "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0, "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": strip_url(detail.get("cover_img")),
        "wheel_img": [strip_url(x) for x in (detail.get("wheel_img") or [])],
        "wheel_img_arr": [{"name":"","url":strip_url(x)} for x in (detail.get("wheel_img") or [])],
        "video_type": detail.get("video_type") or 1, "video_url": strip_url(detail.get("video_url") or ""),
        "video_url_upload": detail.get("video_url_upload") or "", "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": [strip_url(x) for x in (detail.get("detail_img") or [])],
        "detail_img_arr": [{"name":"","url":strip_url(x)} for x in (detail.get("detail_img") or [])],
        "content": detail.get("content") or "", "recommend": detail.get("recommend") or "",
        "sort": detail.get("sort") if detail.get("sort") is not None else 100,
        "unit": detail.get("unit") or "", "buy_min": detail.get("buy_min") or 1,
        "buy_max": detail.get("buy_max") or 1000, "spec_name1": detail.get("spec_name1") or "规格",
        "spec_name2": detail.get("spec_name2") or "", "spec_name3": detail.get("spec_name3") or "",
        "spec_name4": detail.get("spec_name4") or "", "skus": skus,
        "stock_warn": detail.get("stock_warn") or 0,
    }


def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()

# 新 103 个二级的 id（按名字）
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
new_subs = {}   # (cid1, name) -> cid
old_subs = {}   # (cid1, name) -> cid
OLD_NAMES = {'书写工具','纸品本册','文件管理','修正与粘贴','测量与裁剪','美术画材','财务办公',
             '运动鞋服','球类运动','健身训练','户外运动','运动配件',
             '洗发护发','身体清洁','口腔护理','面部护理',
             '童鞋','童装','书包配饰','儿童零食','乳品饮料','营养辅食',
             '清洁工具','收纳整理','厨房用品','居家织品','日用百货',
             '儿童读物','教辅工具','益智玩具','潮流玩具',
             '食用油','米面杂粮','调味干货','个护电器','厨房电器','生活电器'}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        for ch in c.get('children', []):
            key = (c['cate_id'], ch['cate_name'])
            if ch['cate_name'] in OLD_NAMES:
                old_subs[key] = ch['cate_id']
            else:
                new_subs[key] = ch['cate_id']
print(f'新二级: {len(new_subs)}, 旧二级: {len(old_subs)}')

# 旧二级 → 新二级 默认映射
OLD2NEW = {
    (1604,'书写工具'): (1604,'中性笔'), (1604,'纸品本册'): (1604,'作业本'),
    (1604,'文件管理'): (1604,'作业本'), (1604,'修正与粘贴'): (1604,'修正带'),
    (1604,'测量与裁剪'): (1604,'尺子'), (1604,'美术画材'): (1604,'美术用品'),
    (1604,'财务办公'): (1604,'作业本'),
    (1607,'运动鞋服'): (1611,'儿童运动鞋'), (1607,'球类运动'): (1607,'篮球'),
    (1607,'健身训练'): (1607,'其他体育用品'), (1607,'户外运动'): (1607,'其他体育用品'),
    (1607,'运动配件'): (1607,'其他体育用品'),
    (1612,'洗发护发'): (1612,'儿童洗发水'), (1612,'身体清洁'): (1612,'儿童沐浴露'),
    (1612,'口腔护理'): (1612,'儿童牙膏'), (1612,'面部护理'): (1612,'儿童面霜'),
    (1611,'童鞋'): (1611,'儿童运动鞋'), (1611,'童装'): (1611,'校服内搭'),
    (1611,'书包配饰'): (1611,'书包'),
    (1609,'儿童零食'): (1609,'健康零食'), (1609,'乳品饮料'): (1609,'牛奶/奶制品'),
    (1609,'营养辅食'): (1609,'营养补充'),
    (1608,'清洁工具'): (1608,'厨房湿巾'), (1608,'收纳整理'): (1608,'垃圾袋'),
    (1608,'厨房用品'): (1608,'洗洁精'), (1608,'居家织品'): (1608,'毛巾'),
    (1608,'日用百货'): (1608,'抽纸/面巾纸'),
    (1610,'儿童读物'): (1610,'课外阅读'), (1610,'教辅工具'): (1610,'同步练习'),
    (1610,'益智玩具'): (1610,'益智拼图'), (1610,'潮流玩具'): (1610,'盲盒/卡牌'),
    (1606,'食用油'): (1606,'大豆油'), (1606,'米面杂粮'): (1606,'长粒香米'),
    (1606,'调味干货'): (1606,'儿童调味品'),
    (1605,'个护电器'): (1605,'电吹风'), (1605,'厨房电器'): (1605,'电饭煲'),
    (1605,'生活电器'): (1605,'加湿器'),
}

# 拉商品
all_g = []
page = 1
while True:
    d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": 1,
                              "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
    data = d.get('data') or []
    if not data: break
    all_g.extend(data)
    if len(data) < 100 or page > 40: break
    page += 1; time.sleep(0.1)

# 找还在旧二级的商品
stay = []
for g in all_g:
    gc = g.get('good_cate') or []
    if not gc: continue
    c1, c2 = gc[0].get('cate_id1'), gc[0].get('cate_id2')
    c1n, c2n = gc[0].get('cate1'), gc[0].get('cate2')
    if (c1, c2n) in old_subs:
        tgt = OLD2NEW.get((c1, c2n))
        if tgt:
            nc1, nc2 = tgt
            nid2 = new_subs.get((nc1, nc2))
            if nid2:
                stay.append({'good_id': g['good_id'], 'name': (g.get('good_name') or '')[:50],
                             'old': [c1, c2n], 'new': [nc1, nid2], 'new_name': nc2})

print(f'\n还在旧二级的商品: {len(stay)}')
cnt = Counter((s['old'][0], s['old'][1]) for s in stay)
for k, n in cnt.most_common():
    tgt = OLD2NEW.get(k)
    print(f'  {k[1]}: {n} → {tgt[1] if tgt else "?"}')
json.dump(stay, open(os.path.join(P, '_stay_changes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('保存 _stay_changes.json')


# ============ 执行迁移 ============
DRY = os.environ.get('EXEC') != '1'
print(f'
=== {"DRY-RUN" if DRY else "执行"} ===')
ok = fail = 0
for i, s in enumerate(stay, 1):
    if DRY:
        ok += 1; continue
    gid = s['good_id']
    try:
        dres = post('/good/detail', {'good_id': gid})
        detail = dres.get('data') or {}
        body = build_body(detail, [[1, s['new'][0], s['new'][1]]])
        eres = post(f'/good/edit?good_id={gid}', body)
        if eres.get('code') == 0: ok += 1
        else:
            fail += 1; print(f"  ✗ {gid}: {eres.get('msg')}")
        time.sleep(0.08)
    except Exception as e:
        fail += 1; print(f'  ERR {gid}: {e}')
    if i % 100 == 0:
        print(f'  进度 {i}/{len(stay)} ok={ok} fail={fail}', flush=True)
print(f'
完成: ok={ok} fail={fail}')
