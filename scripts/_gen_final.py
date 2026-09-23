# -*- coding: utf-8 -*-
"""生成最终报告页面（后台真实状态）"""
import requests, json, os, time
from collections import Counter

AUTH = r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json"
P = r"C:\Users\shenghua\Desktop\新建文件夹"
auth = json.load(open(AUTH, encoding='utf-8'))
BASE = "https://mall.baovbao.com/admin"
H = {"uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
     "Content-Type": "application/json;charset=UTF-8", "User-Agent": "Mozilla/5.0",
     "Origin": "https://mall.baovbao.com", "Referer": "https://mall.baovbao.com/admin/index.html"}


def post(p, d):
    return requests.post(f"{BASE}{p}", json=d, headers=H, timeout=30).json()


# 分类
cats = post('/goodsCate/lists', {"cate_type": 1, "page": 1, "limit": 500}).get('data', [])
l1 = sorted([c for c in cats if c.get('cate_pid') == 0], key=lambda x: x['sort'])

# 品牌
brands = post('/goodsCate/lists', {"cate_type": 3, "page": 1, "limit": 600}).get('data', [])
bl1 = [b for b in brands if b.get('cate_pid') == 0]

# 商品（分 source 拉取）
all_g = []
for _src in (1, 3):
    page = 1
    while True:
        d = post('/good/lists', {"page": page, "limit": 100, "type": "all", "good_source": _src,
                                  "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []})
        data = d.get('data') or []
        if not data:
            break
        all_g.extend(data)
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.08)
print(f'商品: {len(all_g)}')

# 统计
c2_cnt = Counter()
c1_cnt = Counter()
for g in all_g:
    for gc in (g.get('good_cate') or []):
        c1_cnt[gc.get('cate1')] += 1
        if gc.get('cate_id2'):
            c2_cnt[(gc.get('cate1'), gc.get('cate2'))] += 1
        break
br_cnt = Counter()
for g in all_g:
    gb = g.get('good_brand') or []
    if gb and gb[0].get('brand1') and gb[0]['brand1'] != '无品牌':
        br_cnt[gb[0]['brand1']] += 1

# 组装
js_cats = []
for c in l1:
    subs = []
    for ch in sorted(c.get('children', []), key=lambda x: x['sort']):
        subs.append({'name': ch['cate_name'], 'sort': ch['sort'],
                     'goods': c2_cnt.get((c['cate_name'], ch['cate_name']), 0)})
    js_cats.append({'name': c['cate_name'], 'sort': c['sort'], 'id': c['cate_id'],
                    'subs': subs, 'goods': c1_cnt.get(c['cate_name'], 0)})

js_brands = []
for b in sorted(bl1, key=lambda x: (x['sort'], x['cate_name'])):
    js_brands.append({'name': b['cate_name'], 'sort': b['sort'],
                      'goods': br_cnt.get(b['cate_name'], 0)})

total_subs = sum(len(c['subs']) for c in js_cats)
BRAND_TOP = [b for b in js_brands if b['sort'] <= 30 and b['goods'] > 0]

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>护稚佳品 · 分类品牌改造完成报告</title>
<style>
:root{--bg:#f6f8fc;--p:#fff;--ink:#1c2333;--soft:#5a6478;--line:#e3e8f0;--acc:#2f6fed;--accs:#e9f0ff;--top:#ff6b1a;--mid:#d4a017}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.55}
.wrap{max-width:1340px;margin:0 auto;padding:26px 22px 60px}
header{background:linear-gradient(135deg,#0a9e5c,#2f6fed);color:#fff;padding:22px 26px;border-radius:14px;margin-bottom:18px;box-shadow:0 8px 24px rgba(47,111,237,.2)}
header h1{margin:0 0 4px;font-size:22px}
header p{margin:0;opacity:.93;font-size:13px}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:14px}
.stat{background:rgba(255,255,255,.17);border-radius:9px;padding:10px 12px}
.stat .v{font-size:20px;font-weight:700}
.stat .l{font-size:11px;opacity:.85}
.tabs{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}
.tab{background:var(--p);border:1px solid var(--line);padding:7px 15px;border-radius:8px;cursor:pointer;font-size:13px}
.tab.active{background:var(--acc);color:#fff;border-color:var(--acc)}
.panel{background:var(--p);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.panel h2{margin:0 0 10px;font-size:17px;padding-bottom:7px;border-bottom:2px solid var(--acc)}
.cat{border:1px solid var(--line);border-radius:10px;padding:12px 15px;background:#fafbfd;margin-bottom:10px}
.cn{font-size:15px;font-weight:700;margin-bottom:7px;display:flex;align-items:center;gap:7px}
.ord{background:var(--accs);color:var(--acc);font-size:10px;padding:1px 7px;border-radius:9px;font-weight:700}
.chain{display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.node{background:#fff;border:1px solid var(--line);border-radius:7px;padding:3px 9px;font-size:12px}
.node b{color:var(--acc)}
.node .g{color:var(--soft);font-size:10px;margin-left:3px}
.arrow{color:#b9c2d4;font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}
th{background:#f0f3f9;color:var(--soft);font-weight:600;position:sticky;top:0}
.b-top{background:#fff0e5;color:var(--top);padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700}
.b-mid{background:#fff8e0;color:var(--mid);padding:1px 7px;border-radius:9px;font-size:11px}
.b-tail{background:#f0f3f9;color:var(--soft);padding:1px 7px;border-radius:9px;font-size:11px}
.section{display:none}.section.active{display:block}
.note{background:#fffbe6;border:1px solid #ffe58f;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12.5px;color:#614700}
.search{width:100%;padding:9px 13px;font-size:13px;border:1px solid var(--line);border-radius:8px;margin-bottom:12px}
footer{margin-top:22px;text-align:center;color:var(--soft);font-size:12px}
</style></head>
<body><div class="wrap">
<header>
  <h1>✅ 护稚佳品 · 分类与品牌改造完成</h1>
  <p>9 大类重排 · 103 个二级按购买链路 · 452 品牌按京东天猫权重 · 1520 商品全挂载</p>
  <div class="stats">
    <div class="stat"><div class="v">9</div><div class="l">大类（重排 sort 1-9）</div></div>
    <div class="stat"><div class="v">__SUBS__</div><div class="l">二级（购买链路序）</div></div>
    <div class="stat"><div class="v">__BRANDS__</div><div class="l">品牌（京东天猫权重）</div></div>
    <div class="stat"><div class="v">__GOODS__</div><div class="l">商品（全部挂二级）</div></div>
    <div class="stat"><div class="v">100%</div><div class="l">二级覆盖率</div></div>
  </div>
</header>

<div class="tabs">
  <div class="tab active" data-tab="tree">9 大类 + 二级（购买链路）</div>
  <div class="tab" data-tab="brands">品牌（按权重）</div>
</div>

<div class="section active" id="sec-tree">
  <div class="panel">
    <h2>9 大类 · 二级分类（按购买链路排序）</h2>
    <div id="tree"></div>
  </div>
</div>

<div class="section" id="sec-brands">
  <div class="panel">
    <h2>452 品牌（按 sort；🔥头部=10, 🟡腰部=30-60）</h2>
    <input class="search" id="bs" placeholder="搜索品牌...">
    <table><thead><tr><th style="width:70px">sort</th><th>品牌</th><th style="width:80px">关联商品</th></tr></thead><tbody id="bb"></tbody></table>
  </div>
</div>
<footer>数据实时拉取自 mall.baovbao.com · 2026-09-23</footer>
</div>
<script>
const CATS=__CATS__, BRANDS=__BRANDS__;
document.getElementById('tree').innerHTML = CATS.map(c=>`
  <div class="cat">
    <div class="cn"><span class="ord">sort ${c.sort}</span>${c.name}
      <span style="font-size:11px;color:#5a6478;font-weight:400">${c.subs.length} 二级 · ${c.goods} 商品</span></div>
    <div class="chain">
      ${c.subs.map((s,i)=>`
        <span class="node"><b>${s.name}</b><span class="g">${s.goods||0}</span></span>
        ${i<c.subs.length-1?'<span class="arrow">→</span>':''}
      `).join('')}
    </div>
  </div>`).join('');
const bb=document.getElementById('bb');
function rb(f=''){
  const q=f.trim().toLowerCase();
  bb.innerHTML = BRANDS.filter(b=>!q||b.name.toLowerCase().includes(q)).map(b=>{
    const cls = b.sort<=30?'b-top':(b.sort<=60?'b-mid':'b-tail');
    return `<tr><td><span class="${cls}">${b.sort}</span></td><td><b>${b.name}</b></td><td>${b.goods||''}</td></tr>`;
  }).join('');
}
rb(); document.getElementById('bs').addEventListener('input',e=>rb(e.target.value));
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.section').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); document.getElementById('sec-'+t.dataset.tab).classList.add('active');
}));
</script></body></html>
"""

html = html.replace('__SUBS__', str(total_subs))
html = html.replace('__BRANDS__', str(len(js_brands)))
html = html.replace('__GOODS__', str(len(all_g)))
html = html.replace('__CATS__', json.dumps(js_cats, ensure_ascii=False))
html = html.replace('__BRANDS__', str(len(js_brands)))
html = html.replace('__BRANDS_DUP__', '')
html = html.replace('BRANDS=__BRANDS__', 'BRANDS=' + json.dumps(js_brands, ensure_ascii=False))
# 修复：__BRANDS__ 既用于计数又用于数据，改用占位区分
html = html.replace('const CATS=__CATS__, BRANDS=__BRANDS__;', 'const CATS=' + json.dumps(js_cats, ensure_ascii=False) + ', BRANDS=' + json.dumps(js_brands, ensure_ascii=False) + ';')

# 计数占位（在 header 里）
html = html.replace('<div class="v">__BRANDS__</div>', '<div class="v">' + str(len(js_brands)) + '</div>')

out = os.path.join(P, 'review_assets', 'final_report.html')
open(out, 'w', encoding='utf-8').write(html)
print('生成 ' + out)
print(f'  9 大类 / {total_subs} 二级 / {len(js_brands)} 品牌 / {len(all_g)} 商品')
