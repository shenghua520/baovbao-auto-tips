# -*- coding: utf-8 -*-
"""紧急修复：恢复所有商品图片的完整 URL
根因：之前 edit 用了 strip_url 去掉域名 → 图片失效
方案：移植 mimo 的 restore_url，按路径特征补回正确域名
"""
import requests, json, os, re, time, sys
from collections import Counter

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}

APIUNION = "https://d5ma.img.apiunion.com"
JD = "https://img13.360buyimg.com"
PICING = "https://img.picing.com"
MALL = "https://mall.baovbao.com"


def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()


def restore_url(u):
    """返回 (完整URL, 类型)"""
    if not u:
        return "", "empty"
    s = str(u).strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s, "keep_abs"
    if s.startswith("//"):
        path = s[2:]
        if path.startswith("upload/") or re.match(r"^\d{4}/\d{2}/", path) or path.startswith("images/"):
            return "https://mall.baovbao.com/" + path, "proto_rel_local"
        if path.startswith("i/"):
            return APIUNION + "/" + path, "proto_rel_apiunion"
        return "https:" + s, "proto_rel_other"
    path = s if s.startswith("/") else "/" + s
    while path.startswith("//"):
        path = path[1:]
    if path.startswith("/i/") or "/i/" in path[:6]:
        return APIUNION + path, "apiunion"
    if "/jfs/" in path or path.startswith("/n12/") or path.startswith("/sku/jfs"):
        return JD + path, "jd"
    if "imageMogr2" in s or re.search(r"/\d{10,}_\d{2,4}X\d{2,4}_", path):
        return PICING + path, "picing"
    if path.startswith("/upload/") or path.startswith("upload/"):
        if not path.startswith("/"):
            path = "/" + path
        return MALL + path, "mall_upload"
    if path.startswith("/images/") or re.match(r"^/\d{4}/\d{2}/", path):
        return MALL + path, "mall_guess"
    return MALL + path, "fallback_mall"


def build_body_fixed(detail, good_cate):
    """图片字段用 restore_url 恢复完整域名"""
    skus = []
    seen = set()
    for s in detail.get("skus") or []:
        key = (s.get("spec_val1"), s.get("spec_val2"), s.get("spec_val3"))
        if key in seen:
            continue
        seen.add(key)
        o = dict(s)
        o["cover_img"] = restore_url(o.get("cover_img"))[0] if o.get("cover_img") else ""
        # sku 里的 wheel_img / detail_img
        if o.get("wheel_img"):
            o["wheel_img"] = [restore_url(x)[0] for x in o["wheel_img"]]
        if o.get("detail_img"):
            o["detail_img"] = [restore_url(x)[0] for x in o["detail_img"]]
        if not o.get("pay_setting"):
            o["pay_setting"] = [{"checked": 0, "account_id": "", "money": 0}]
        if not o.get("spec_val1"):
            sd = o.get("spec_data") or []
            o["spec_val1"] = (sd[0].get("val") if sd else "默认") or "默认"
        skus.append(o)
    if not skus:
        skus = [{"cover_img": "", "spec_val1": "默认", "spec_val2": "", "unit_quatity": 1,
                 "cost_price": detail.get("cost_price") or 0, "sale_price": detail.get("sale_price") or 0,
                 "crossed_price": detail.get("crossed_price") or 0, "stock": 0, "state": 1,
                 "pay_setting": [{"checked": 0, "account_id": "", "money": 0}]}]
    raw = detail.get("good_brand") or []
    mapped = []
    for b in raw:
        if isinstance(b, dict):
            mapped.append([b.get("brand_id1") or "", b.get("brand_id2") or ""])
        elif isinstance(b, (list, tuple)):
            mapped.append([b[0] if b else "", b[1] if len(b) > 1 else ""])
    wheel = [restore_url(x)[0] for x in (detail.get("wheel_img") or [])]
    detailimgs = [restore_url(x)[0] for x in (detail.get("detail_img") or [])]
    return {
        "good_name": detail.get("good_name") or "", "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"), "good_type": detail.get("good_type"),
        "good_brand": mapped or [["", ""]], "good_cate": good_cate,
        "tag_ids": detail.get("tag_ids") or [], "fake_sale": detail.get("fake_sale") or 0,
        "good_desc": detail.get("good_desc") or "", "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0, "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0, "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": restore_url(detail.get("cover_img"))[0],
        "wheel_img": wheel,
        "wheel_img_arr": [{"name": "", "url": x} for x in wheel],
        "video_type": detail.get("video_type") or 1, "video_url": detail.get("video_url") or "",
        "video_url_upload": detail.get("video_url_upload") or "", "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": detailimgs,
        "detail_img_arr": [{"name": "", "url": x} for x in detailimgs],
        "content": detail.get("content") or "", "recommend": detail.get("recommend") or "",
        "sort": detail.get("sort") if detail.get("sort") is not None else 100,
        "unit": detail.get("unit") or "", "buy_min": detail.get("buy_min") or 1,
        "buy_max": detail.get("buy_max") or 1000, "spec_name1": detail.get("spec_name1") or "规格",
        "spec_name2": detail.get("spec_name2") or "", "spec_name3": detail.get("spec_name3") or "",
        "spec_name4": detail.get("spec_name4") or "", "skus": skus,
        "stock_warn": detail.get("stock_warn") or 0,
    }


# 拉全部商品（source 1 和 3）
all_g = []
for src in (1, 3):
    page = 1
    while True:
        d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": src,
                                  "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
        data = d.get('data') or []
        if not data:
            break
        all_g.extend(data)
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.08)
print('商品总数: ' + str(len(all_g)))

DRY = os.environ.get('EXEC') != '1'
ok = fail = 0
kinds = Counter()
for i, g in enumerate(all_g, 1):
    gid = g['good_id']
    try:
        detail = (post('/good/detail', {'good_id': gid}).get('data') or {})
        # 检测是否需要恢复
        ci = detail.get('cover_img') or ''
        fixed, kind = restore_url(ci)
        kinds[kind] += 1
        if DRY:
            if i <= 5:
                print(f"  {gid}: {ci[:60]} -> {fixed[:70]} [{kind}]")
            ok += 1
            continue
        # 保留原大类/二级
        gc = detail.get('good_cate') or []
        cate = [[1, gc[0].get('cate_id1'), gc[0].get('cate_id2')]] if gc else [[1, 0, 0]]
        body = build_body_fixed(detail, cate)
        eres = post('/good/edit?good_id=' + str(gid), body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print('  x ' + str(gid) + ': ' + str(eres.get('msg')))
        time.sleep(0.08)
    except Exception as e:
        fail += 1
        print('  ERR ' + str(gid) + ': ' + str(e))
    if i % 100 == 0:
        print('  progress ' + str(i) + '/' + str(len(all_g)) + ' ok=' + str(ok) + ' fail=' + str(fail), flush=True)

print('图片类型分布: ' + str(dict(kinds)))
print(('DRY-RUN ' if DRY else '') + '完成: ok=' + str(ok) + ' fail=' + str(fail))
