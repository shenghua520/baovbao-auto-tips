# -*- coding: utf-8 -*-
"""Step 5: 二级分类关联（商品名 → 101 新二级）
关键词按长度降序匹配；匹配不到则保持原二级。
"""
import requests, json, os, time, re

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {
    "uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html",
}

def post(path, payload):
    r = requests.post(f"{BASE}{path}", json=payload, headers=H, timeout=30)
    try:
        return r.json()
    except Exception:
        return {"code": -1, "msg": r.text[:300]}



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

# ============ 二级分类关键词库（大类 → [(二级名, [关键词...])]）============
KW = {
"学习文具": [
    ("自动铅笔", ["自动铅笔", "活动铅笔", "自动铅"]),
    ("铅笔", ["铅笔", "HB", "2B", "素描铅"]),
    ("笔芯", ["笔芯", "替芯", "铅芯", "墨囊", "墨水"]),
    ("中性笔", ["中性笔", "签字笔", "圆珠笔", "宝珠笔", "走珠笔", "水笔", "碳素笔"]),
    ("钢笔", ["钢笔", "墨水笔", "美工笔"]),
    ("橡皮擦", ["橡皮"]),
    ("卷笔刀", ["卷笔刀", "削笔", "转笔刀", "削笔机"]),
    ("修正带", ["修正带", "修正液", "改正带", "涂改", "消字"]),
    ("尺子", ["尺子", "直尺", "三角尺", "套尺", "量角器", "圆规", "钢尺"]),
    ("学生剪刀", ["剪刀", "美工刀", "裁纸刀", "刻刀", "手工刀"]),
    ("固体胶", ["固体胶", "胶棒", "胶水", "双面胶", "胶带", "透明胶"]),
    ("美术用品", ["水彩笔", "油画棒", "蜡笔", "颜料", "画笔", "画纸", "彩铅", "马克笔", "水粉", "素描"]),
    ("书皮", ["书皮", "书套", "包书"]),
    ("笔袋", ["笔袋", "文具盒", "铅笔盒", "笔盒", "笔筒"]),
    ("作业本", ["作业本", "笔记本", "本子", "抄本", "日记本", "手账", "便签", "便利贴", "错题", "练习本", "记事本", "课文本"]),
],
"体育用品": [
    ("羽毛球", ["羽毛球", "球拍"]),
    ("乒乓球", ["乒乓球"]),
    ("篮球", ["篮球"]),
    ("足球", ["足球"]),
    ("排球", ["排球"]),
    ("跳绳", ["跳绳"]),
    ("其他体育用品", ["毽子", "沙包", "呼啦圈", "哑铃", "瑜伽", "护具", "护膝", "护腕", "发带"]),
],
"少儿护理": [
    ("儿童牙膏", ["牙膏"]),
    ("儿童牙刷", ["牙刷"]),
    ("儿童洗发水", ["洗发"]),
    ("儿童沐浴露", ["沐浴"]),
    ("儿童洗面奶", ["洗面"]),
    ("儿童面霜", ["面霜", "润肤", "护肤霜"]),
    ("儿童润唇膏", ["润唇", "唇膏"]),
    ("儿童洗手液", ["洗手液", "洗手皂"]),
    ("儿童防晒", ["防晒"]),
    ("儿童护臀膏", ["护臀", "爽身"]),
    ("儿童洗衣液", ["洗衣液", "洗衣皂"]),
],
"少儿穿戴": [
    ("儿童运动鞋", ["运动鞋", "跑步鞋", "篮球鞋", "板鞋", "休闲鞋", "机能鞋", "学步鞋"]),
    ("袜子", ["袜子", "船袜", "中筒袜"]),
    ("内裤", ["内裤", "平角裤", "三角裤"]),
    ("喝水杯", ["水杯", "保温杯", "水壶", "吸管杯", "饮水"]),
    ("拖鞋", ["拖鞋", "洞洞鞋", "凉拖"]),
    ("帽子", ["帽子", "遮阳帽", "防晒帽", "毛线帽"]),
    ("毛巾", ["毛巾", "汗巾", "浴巾"]),
    ("校服内搭", ["秋衣", "秋裤", "内衣", "家居服", "长袖T恤", "打底"]),
    ("书包", ["书包", "背包", "双肩包"]),
    ("雨衣雨鞋", ["雨衣", "雨鞋", "雨披", "雨靴"]),
],
"读物潮玩": [
    ("同步练习", ["同步练习", "天天练", "小状元", "教材全解", "口算", "阅读理解", "课堂作业", "默写"]),
    ("课外阅读", ["名著", "童话", "神话", "十万个为什么", "西游记", "三国演义", "红楼梦", "水浒传", "课外阅读", "快乐读书吧"]),
    ("工具书", ["字典", "词典", "新华字典", "现代汉语"]),
    ("思维训练", ["逻辑思维", "专注力", "数独", "迷宫", "找不同", "脑筋急转弯"]),
    ("科普/百科", ["百科全书", "科普", "神奇校车", "DK"]),
    ("绘本/图画书", ["绘本", "图画书", "大卫", "猜猜我有多爱你", "毛毛虫", "逃家小兔"]),
    ("盲盒/卡牌", ["盲盒", "卡牌", "集卡"]),
    ("减压玩具", ["捏捏", "减压面团", "指压"]),
    ("手办/摆件", ["手办", "摆件", "公仔"]),
    ("解压玩具", ["指尖陀螺", "魔方", "巴克球", "推牌", "解压"]),
    ("益智拼图", ["拼图", "积木", "桌游", "益智"]),
],
"少儿食品": [
    ("牛奶/奶制品", ["牛奶", "酸奶", "奶酪", "奶棒", "成长奶", "纯奶"]),
    ("坚果/果干", ["坚果", "巴旦木", "核桃", "红枣", "葡萄干", "腰果", "开心果"]),
    ("健康零食", ["饼干", "海苔", "鳕鱼肠", "果蔬干", "水果条", "米饼", "零食"]),
    ("天然饮品", ["果汁", "椰子水", "杏仁露", "核桃乳", "气泡水", "饮料"]),
    ("早餐麦片", ["麦片", "燕麦", "谷物圈", "脆谷乐"]),
    ("营养补充", ["钙", "DHA", "维生素", "益生菌", "营养", "软糖"]),
    ("儿童调味品", ["酱油", "芝麻酱", "调味"]),
],
"家庭日用": [
    ("抽纸/面巾纸", ["抽纸", "面巾纸", "纸巾", "餐巾纸"]),
    ("卷纸/卫生纸", ["卷纸", "卫生纸"]),
    ("衣物柔顺剂", ["柔顺剂", "护理剂", "金纺"]),
    ("洗衣液", ["洗衣液", "洗衣粉", "洗衣皂", "皂粉"]),
    ("洗发水", ["洗发水", "洗发露", "洗发"]),
    ("沐浴露", ["沐浴露", "沐浴"]),
    ("洗面奶", ["洗面奶", "洁面"]),
    ("牙膏/牙刷", ["牙膏", "牙刷"]),
    ("洗洁精", ["洗洁精", "洗碗"]),
    ("保鲜用品", ["保鲜袋", "保鲜膜", "保鲜盒", "密封袋"]),
    ("垃圾袋", ["垃圾袋", "垃圾"]),
    ("洗手液", ["洗手液"]),
    ("消毒除菌", ["消毒液", "除菌", "消毒"]),
    ("厨房湿巾", ["厨房湿巾", "厨湿巾"]),
    ("洁厕灵", ["洁厕", "马桶"]),
    ("地板清洁剂", ["地板", "地砖"]),
    ("电蚊香液", ["电蚊香", "蚊香液", "蚊香"]),
    ("驱蚊水", ["驱蚊", "花露水", "防蚊"]),
],
"米面油品": [
    ("大豆油", ["大豆油", "豆油"]),
    ("调和油", ["调和油"]),
    ("花生油", ["花生油"]),
    ("菜籽油", ["菜籽油"]),
    ("玉米葵花油", ["玉米油", "葵花籽油", "葵花油"]),
    ("橄榄油", ["橄榄油"]),
    ("东北珍珠米", ["珍珠米", "东北大米"]),
    ("长粒香米", ["长粒香"]),
    ("丝苗米", ["丝苗米", "籼米", "猫牙米"]),
    ("五常大米", ["五常", "稻花香"]),
    ("胚芽米", ["胚芽米", "有机米", "糙米"]),
    ("泰国香米", ["泰国香", "茉莉香", "香纳兰"]),
    ("中筋面粉", ["中筋", "饺子粉", "通用粉", "麦芯"]),
    ("高筋面粉", ["高筋", "面包粉"]),
    ("低筋面粉", ["低筋", "蛋糕粉", "糕点粉"]),
    ("全麦面粉", ["全麦", "黑麦"]),
    ("糯米粉", ["糯米粉", "粘米粉"]),
],
"家用电器": [
    ("护眼台灯", ["台灯", "护眼灯", "学习灯"]),
    ("加湿器", ["加湿"]),
    ("电饭煲", ["电饭", "电压力锅", "压力锅"]),
    ("破壁机", ["破壁机", "榨汁机", "豆浆机", "料理机"]),
    ("扫地机器人", ["扫地机器人", "扫地机", "拖地机器人"]),
    ("电吹风", ["电吹风", "吹风机"]),
    ("净水器", ["净水器", "净水机", "饮水机"]),
],
}

# 二级名 → cate_id
r = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500})
sub_id = {}   # (cate1_id, sub_name) -> cate_id
pid2name = {}
for c in r.get('data', []):
    if c.get('cate_pid') == 0:
        pid2name[c['cate_id']] = c['cate_name']
        for ch in c.get('children', []):
            sub_id[(c['cate_id'], ch['cate_name'])] = ch['cate_id']

CAT_ID = {"学习文具":1604,"体育用品":1607,"少儿护理":1612,"少儿穿戴":1611,"少儿食品":1609,
          "家庭日用":1608,"读物潮玩":1610,"米面油品":1606,"家用电器":1605}

# 构建匹配表（关键词长度降序）
flat = []
for cat, items in KW.items():
    cid1 = CAT_ID[cat]
    for sub, kws in items:
        scid = sub_id.get((cid1, sub))
        if not scid:
            print(f'⚠️ 二级不存在: {cat} > {sub}')
            continue
        for kw in kws:
            flat.append((kw, cid1, scid, sub))
flat.sort(key=lambda x: -len(x[0]))
print(f'关键词表: {len(flat)} 条')

# 匹配商品
goods = json.load(open(os.path.join(P, '_goods_all.json'), encoding='utf-8'))
changes = []
for g in goods:
    name = g.get('good_name') or ''
    gc = g.get('good_cate') or []
    cur1 = gc[0].get('cate_id1') if gc else None
    cur2 = gc[0].get('cate_id2') if gc else None
    for kw, cid1, scid, sub in flat:
        if kw in name:
            if cid1 != cur1 or scid != cur2:
                changes.append({'good_id': g['good_id'], 'name': name[:55],
                                'old': [cur1, cur2], 'new': [cid1, scid], 'sub': sub, 'kw': kw})
            break

print(f'需改二级: {len(changes)} / {len(goods)}')
from collections import Counter
cnt = Counter(c['sub'] for c in changes)
for s, n in cnt.most_common(20):
    print(f'  {s}: {n}')

json.dump(changes, open(os.path.join(P, '_cate_changes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('保存 _cate_changes.json')

# ============ 执行 ============
DRY = os.environ.get('EXEC') != '1'
print(f'\n=== {"DRY-RUN" if DRY else "执行"} ===')
ok = fail = 0
for i, c in enumerate(changes, 1):
    if DRY:
        ok += 1
        continue
    gid = c['good_id']
    try:
        dres = post('/good/detail', {'good_id': gid})
        detail = dres.get('data') or {}
        body = build_body(detail, [[1, c['new'][0], c['new'][1]]])
        eres = post(f'/good/edit?good_id={gid}', body)
        if eres.get('code') == 0:
            ok += 1
        else:
            fail += 1
            print(f"  ✗ {gid}: {eres.get('msg')}")
        time.sleep(0.08)
    except Exception as e:
        fail += 1
        print(f"  ERR {gid}: {e}")
    if i % 100 == 0:
        print(f'  进度 {i}/{len(changes)} ok={ok} fail={fail}', flush=True)
print(f'\n完成: ok={ok} fail={fail}')
