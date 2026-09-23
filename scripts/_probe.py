"""探查 baovbao 后台真实状态（mimo 项目基础上的 9/23 更新）"""
import requests, json, sys, time

# 从 mimo 项目 auth.json 拿 token（9/21 的，可能失效）
with open(r"C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2\auth.json", encoding='utf-8') as f:
    auth = json.load(f)

BASE = "https://mall.baovbao.com/admin"
HEADERS = {
    "uid": str(auth["admin_id"]),
    "sid": str(auth["sid"]),
    "token": auth["token"],
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Origin": "https://mall.baovbao.com",
    "Referer": "https://mall.baovbao.com/admin/index.html",
}

def probe(path, payload, label):
    url = f"{BASE}{path}"
    print(f'\n=== {label} ===')
    print(f'POST {url}')
    try:
        r = requests.post(url, data=payload, headers=HEADERS, timeout=15)
        print(f'  status: {r.status_code}')
        try:
            d = r.json()
            # 只展示关键字段
            if 'data' in d:
                data = d['data']
                if isinstance(data, list):
                    print(f'  data: list, len={len(data)}')
                    if data:
                        print(f'    first: {json.dumps(data[0], ensure_ascii=False)[:300]}')
                elif isinstance(data, dict):
                    print(f'  data: dict, keys={list(data.keys())[:10]}')
                    for k in list(data.keys())[:5]:
                        v = data[k]
                        if isinstance(v, list):
                            print(f'    {k}: list len={len(v)}')
                            if v:
                                print(f'      sample: {json.dumps(v[0], ensure_ascii=False)[:200]}')
                        else:
                            print(f'    {k}: {str(v)[:100]}')
            else:
                print(f'  body: {r.text[:300]}')
        except:
            print(f'  body: {r.text[:300]}')
    except Exception as e:
        print(f'  err: {e}')

# 1. 拉 L1 分类（type=1，9 大类）
probe('/goodsCate/lists', {'cate_type': 1, 'page': 1, 'limit': 100}, 'L1 分类 (9 大类)')

# 2. 拉品牌（type=3）
probe('/goodsCate/lists', {'cate_type': 3, 'page': 1, 'limit': 500}, '品牌 (cate_type=3)')

# 3. 简单看是否登录态有效
probe('/Index/index', {}, 'Index/index (登录态测试)')

print('\n=== 探查完成 ===')
