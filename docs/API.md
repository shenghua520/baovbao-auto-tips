# 保未宝商城后台 API 文档

> 站点：<https://mall.baovbao.com>（后台 SPA，入口 `/admin/index.html#/...`）
> 商城名：`护稚佳品`
> 接口总数：**448 个**（73 个模块）— 从前端 JS 提取 + 实测探测
> 文档生成：2026-09-24（接口清单 2026-09-23 实测）

---

## 1. 通用约定

### 1.1 请求

| 项 | 值 |
|---|---|
| **Base URL** | `https://mall.baovbao.com` |
| **方法** | 全部 `POST` |
| **Content-Type** | **`application/json;charset=UTF-8`**（必须） |
| **鉴权** | 走 Header（不是 body） |

### 1.2 鉴权 Header

```
uid: <管理员ID>
sid: <会话ID>
token: <令牌>
Origin: https://mall.baovbao.com
Referer: https://mall.baovbao.com/admin/index.html
User-Agent: Mozilla/5.0
```

> ⚠️ **`good/edit` 等含嵌套数组的接口必须用 JSON body**。用 `application/x-www-form-urlencoded` 会报 `品牌参数错误`。

### 1.3 成功响应

```json
{
  "code": 0,
  "msg": "请求成功, 操作成功",
  "data": [],
  "time": "2026-09-23 12:13:57",
  "duration": 0.0367
}
```

### 1.4 错误码

| code | 含义 | 常见原因 / 解决 |
|---|---|---|
| `0` | 成功 | — |
| `1` | 通用错误 | 看 `msg` |
| `1002` | 参数错误 | 缺必填字段。分类/品牌接口通常是**漏了 `period`** |
| `1003` | — | 见 msg |
| `1004` | — | 见 msg |
| `1014` | 权限不足 | `账号权限不足,请联系客服人员`，该模块当前账号无权限 |
| `10501` | 业务限制 | 见 msg（例：分类下有上架商品不能删） |

**分类/品牌接口 1002 报错示例**：

```json
{"code":1002,"msg":"上架的商城 必须为正整数~"}
```

→ **必须带 `period: 72`**（上架期，正整数）。

---

## 2. 登录

### 2.1 `POST /admin/Login/captcha` — 获取验证码

**请求**：`{}`（空）

**返回**：

```json
{
  "code": 0,
  "data": { "captcha": "data:image/png;base64,iVBORw0KGgo..." }
}
```

> 验证码是 **base64 PNG 图片**（不是文字）。需要 OCR 解出算式（如 `5+9` → 填 `14`）。

**Python 示例**：

```python
r = requests.post(BASE + '/admin/Login/captcha', json={}, headers=HH)
b64 = r.json()['data']['captcha'].split(',')[1]
open('captcha.png','wb').write(base64.b64decode(b64))
# → OCR 识别后得到答案
```

### 2.2 `POST /admin/Login/adminLogin` — 账号登录

**请求**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `account` | string | 账号 |
| `password` | string | 密码 |
| `captcha` | string | 验证码答案（纯数字，如 `"14"`） |

**返回（失败）**：

```json
{"code":1000,"msg":"请求错误, 验证码错误~"}
```

**返回（成功）**：

```json
{"code":0,"data":{"sid":303,"admin_id":3,"nick_name":"...","token":"..."}}
```

> 登录后拿到 `uid`(=admin_id) / `sid` / `token`，后续请求放 Header。

### 2.3 其他登录接口

| 路径 | 说明 |
|---|---|
| `/admin/Login/autoLoginByAccount` | 按账号自动登录 |
| `/admin/Login/getAccountsByPhone` | 按手机号取账号列表 |
| `/admin/Login/yinfa` | — |
| `/admin/login/lpy_register` `/admin/login/lpy_send` `/admin/login/reset` `/admin/login/sms` | 另一套登录/短信 |

---

## 3. 商品分类 `goodsCate`（14 个接口）

> 分类和品牌**共用一张表**，靠 `cate_type` 区分：`1`=商品分类，`3`=品牌。

### 3.1 `POST /admin/goodsCate/lists` — 分类/品牌列表

**请求**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `cate_type` | int | ✅ | `1`=分类 / `3`=品牌 |
| `page` | int | | 默认 1 |
| `limit` | int | | 建议 500（一次拉全） |

**返回**：分类数组，每项含 `children`（二级）。

```json
{
  "code": 0,
  "data": [
    {
      "cate_id": 1604, "cate_type": 1, "cate_name": "学习文具",
      "cate_pid": 0, "cate_level": 1, "sort": 1, "state": 1,
      "mall": "护稚佳品",
      "children": [
        {"cate_id": 2191, "cate_name": "铅笔", "cate_pid": 1604, "sort": 100}
      ]
    }
  ]
}
```

### 3.2 `POST /admin/goodsCate/add` — 新建分类/品牌

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `cate_name` | string | ✅ | **最长 6 字符**（超过报 `分类名称 最大长度为: 6位`） |
| `cate_pid` | int | ✅ | 父 ID。一级传 `0`，二级传父 `cate_id` |
| `cate_type` | int | ✅ | `1`/`3` |
| `cate_icon` | string | | 图标 URL |
| `shop_type` | int | | 通常 `1` |
| `is_display` | int | | `1` 显示 |
| **`period`** | int | ✅ | **必须 `72`**，否则 1002 |
| `sort` | int | | 排序，越小越靠前 |
| `state` | int | | `1` 正常 |

```python
payload = {
    "cate_name": "铅笔", "cate_pid": 1604, "cate_type": 1,
    "cate_icon": "", "shop_type": 1, "is_display": 1,
    "period": 72, "sort": 100, "state": 1
}
requests.post(BASE + '/admin/goodsCate/add', json=payload, headers=HH)
```

### 3.3 `POST /admin/goodsCate/edit` — 修改

字段同 `add`，**额外必填 `cate_id`**。

### 3.4 `POST /admin/goodsCate/del` — 删除

```json
{"cate_id": 2150}
```

> ⚠️ **分类下有上架商品时删除失败**（`10501`）。必须先迁移商品再删。

### 3.5 分类模块其他接口

| 路径 | 说明 | 参数 |
|---|---|---|
| `/admin/goodsCate/detail` | 详情 | `{cate_id}` |
| `/admin/goodsCate/tree` | 分类树 | `{cate_type}` |
| `/admin/goodsCate/mallCateTree` | 商城分类树 | `{mall_id}` |
| `/admin/goodsCate/virtualCateTree` | 虚拟分类树 | — |
| `/admin/goodsCate/getAllTags` | 全部标签 | — |
| `/admin/goodsCate/supplyCates` | 供应链分类 | — |
| `/admin/goodsCate/supplyCateMap` | 供应链映射 | — |
| `/admin/goodsCate/setSupplyCateMap` | 设置映射 | — |
| `/admin/goodsCate/delSupplyCateMap` | 删除映射 | — |
| `/admin/goodsCate/disable` | 停用 | — |

---

## 4. 商品 `good`（25 个接口）

### 4.1 `POST /admin/good/lists` — 商品列表

| 字段 | 类型 | 说明 |
|---|---|---|
| `page` / `limit` | int | 分页 |
| `type` | string | `"all"` |
| **`good_source`** | int | **`1`=自营，`3`=供应链。必须分别查，传 `"all"` 拉不到！** |
| `good_field` | string | 搜索字段，如 `good_name` |
| `good_value` | string | 搜索值 |
| `brand_id` | array | 品牌筛选 |
| `createtime` | array | 时间范围 |

```python
# ✅ 正确做法：循环查 source 1 和 3
for src in (1, 3):
    r = post('/admin/good/lists', {"page":1,"limit":100,"type":"all","good_source":src,
             "good_field":"good_name","good_value":"","brand_id":[],"createtime":[]})
```

**返回字段**（节选）：`good_id`, `good_name`, `good_cate[]`, `good_brand[]`, `good_source`, `state`, `fake_sale`

### 4.2 `POST /admin/good/detail` — 商品详情

```json
{"good_id": 2645}
```

返回**全部字段**（改商品时要用它做回填）：

```
good_id, good_name, good_desc, good_alias, good_source, upstream_good_id,
source_id, source_goods_id, good_type, good_brand[], good_cate[],
cover_img, wheel_img[], detail_img[], content, skus[],
sort, unit, buy_min, buy_max, fake_sale, stock_warn,
spec_name1..4, tag_ids[], promise[], store_id, video_*, install_open, lease_open, purchase_open
```

### 4.3 `POST /admin/good/edit?good_id=<id>` — 修改商品（**最复杂**）

> ⚠️ **必须 `POST` + JSON body + 把 `detail` 拿到的 30+ 字段全量回填**，否则会丢数据。

**关键字段**：

| 字段 | 格式 | 说明 |
|---|---|---|
| `good_cate` | `[[mall_id, cate_id1, cate_id2]]` | 三层数组 |
| `good_brand` | `[[brand_id1, brand_id2]]` | 品牌 L1+L2 成对 |
| `cover_img` | string | **完整 URL**（见 §7 图片域名） |
| `wheel_img` / `detail_img` | array | 完整 URL |
| `skus[]` | array | 每个 sku 也要 `cover_img` 完整 URL |
| `fake_sale` | int | 展示销量 |

**最小可用 body 模板**（务必从 `detail` 回填，不要手搓）：

```python
def build_body(detail, good_cate):
    return {
        "good_name": detail.get("good_name") or "",
        "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"),
        "good_type": detail.get("good_type"),
        "good_brand": [[b["brand_id1"], b["brand_id2"]] for b in (detail.get("good_brand") or [])],
        "good_cate": good_cate,                      # [[1, cate1, cate2]]
        "tag_ids": detail.get("tag_ids") or [],
        "fake_sale": detail.get("fake_sale") or 0,
        "good_desc": detail.get("good_desc") or "",
        "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0,
        "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0,
        "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": restore_url(detail.get("cover_img")),
        "wheel_img": [restore_url(x) for x in (detail.get("wheel_img") or [])],
        "wheel_img_arr": [{"name": "", "url": restore_url(x)} for x in (detail.get("wheel_img") or [])],
        "video_type": detail.get("video_type") or 1,
        "video_url": detail.get("video_url") or "",
        "video_url_upload": detail.get("video_url_upload") or "",
        "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": [restore_url(x) for x in (detail.get("detail_img") or [])],
        "detail_img_arr": [{"name": "", "url": restore_url(x)} for x in (detail.get("detail_img") or [])],
        "content": detail.get("content") or "",
        "recommend": detail.get("recommend") or "",
        "sort": detail.get("sort") if detail.get("sort") is not None else 100,
        "unit": detail.get("unit") or "",
        "buy_min": detail.get("buy_min") or 1,
        "buy_max": detail.get("buy_max") or 1000,
        "spec_name1": detail.get("spec_name1") or "规格",
        "spec_name2": detail.get("spec_name2") or "",
        "spec_name3": detail.get("spec_name3") or "",
        "spec_name4": detail.get("spec_name4") or "",
        "skus": build_skus(detail),                   # 去重 + restore_url
        "stock_warn": detail.get("stock_warn") or 0,
    }
```

### 4.4 商品模块其他接口（25 个）

```
good/add            新建商品
good/del            删除
good/state          上下架
good/sort           排序
good/commend        推荐
good/check          审核
good/export         导出
good/import         导入
good/skuLists       SKU 列表      {good_id}
good/changePrice    改价
good/changeStock    改库存
good/changeSkuState 改 SKU 状态
good/changeProfit   改利润
good/batchFakeSale  批量改销量
good/setStockwarn   库存预警
good/discount       折扣
good/paysetting     支付设置
good/reward         奖励
good/asyncSupply    同步供应链
good/asyncUpstream  同步上游
good/asyncVirtual   同步虚拟
good/asyncLife      同步生活
```

---

## 5. 后台首页 `index`（15 个接口）

| 路径 | 返回 | 说明 |
|---|---|---|
| `/admin/index/index` | `{statistics}` | 首页统计 |
| `/admin/index/mallStatic` | `{end_time, static}` | 商城统计 |
| `/admin/index/orderStatic` | `{end_time, static}` | 订单统计 |
| `/admin/index/financeStatic` | `{end_time, static}` | 财务统计 |
| `/admin/index/shopOrderStatic` | — | 店铺订单统计 |
| `/admin/index/screen` | `{project_name, user_count, user_register, user_month_active, user_day_active, good_detail_count, active_line_date, active_line_value}` | 大屏数据 |
| `/admin/index/getRegions` | `list[35]` | 省市区（`region_id/region_name/region_pid/region_level/children`） |
| `/admin/index/express` | `list[1114]` | 快递公司（`express_id/express_name/express_sn`） |
| `/admin/index/logs` | `list` | 操作日志（`log_id/admin_id/api_url/request_ip/request_method/request_param`） |
| `/admin/index/tasks` | `list[10]` | 任务队列 |
| `/admin/index/message` | `{slideshow, articles}` | 公告/轮播 |
| `/admin/index/addons` | `list` | 已装插件 |
| `/admin/index/uploadImg` | — | **需 `category` 参数**（缺了报 1002） |
| `/admin/index/uploadFile` | — | 上传文件 |
| `/admin/index/taskCancel` | — | 取消任务 |

---

## 6. 其他常用模块

### 订单 `order`（14）

`lists` / `listCount` / `detail` / `send` / `cancel` / `logistics` / `print` / `notice` / `export` / `purchaseSend` / `writeoff` / `leaseUpdate` / `yinfa` / `yinfaExport`

- `/admin/order/lists` → `{page, limit}`，返回 `order_id/order_cids/order_no/order_from/all_source/source_order_no`
- `/admin/order/listCount` → `{countInfo, payMap, payTotal}`

### 用户 `user`（10）

`lists` / `detail` / `export` / `import` / `del` / `disable` / `logLists` / `resetPassword` / `changAccount` / `changLevel` / `customize`

- `/admin/user/lists` → `{page, limit}`，返回 `user_id/user_pid/user_name/phone/password/pay_password`

### 商城 `mall`（7）

`lists` / `detail` / `add` / `edit` / `del` / `disable` / `pageDetail`

- `/admin/mall/lists` → `mall_id/mall_name/mall_link/mall_desc/sort/state`

### 管理员 `admin`（14）

`lists` / `menu` / `rules` / `detail` / `add` / `edit` / `del` / `disable` / `changePassword` / `changeNicknamePhone` / `setDefaultPassword` / `setPayPassword` / `getTicket` / `yinfa`

### 角色 `role`（5）

`groups` / `rules` / `add` / `detail` / `edit`

### 设置 `setting`（28，最多）

`baseinfo` / `pay` / `send` / `third` / `fourth` / `alone` / `entry` / `live` / `pagestyle` / `supply` / `subaccount` / `docs` / `fieldList` / `fieldEdit` / `fieldDel` / `kuaidi*` / `getSmbaoLeft`

### 统计 `statistics`（10）

`conversion` / `financeDay` / `goodsSell` / `goodsCateSell` / `grossProfit` / `orderStat` / `orderStatExport` / `orderGoodsStats` / `sourceFinance` / `survey`

### 财务 `FinanceAccount` / `financeAccount` / `userFinance` / `withdraw`

- `/admin/FinanceAccount/flow` / `cashlog` → 资金流水
- `/admin/withdraw/lists` / `batchAgree` / `batchReject` / `export` / `transfer`

### 营销

- `coupon`（6）优惠券
- `activity`（5）活动
- `reduce`（6）满减
- `bonus`（3）红包
- `card`（20）卡券
- `giftbag`（5）礼包
- `cps`（8）推广
- `tuan`（7）团购

---

## 7. ⚠️ 图片 URL 规范（必读）

商品图片字段（`cover_img` / `wheel_img` / `detail_img` / `sku.cover_img`）**必须存完整带域名的 URL**。

`good/detail` 返回的可能是相对路径，**回写前必须补全域名**：

```python
def restore_url(u):
    if not u: return ""
    s = str(u).strip()
    if s.startswith(("http://", "https://")): return s        # 已是完整 URL
    if s.startswith("//"):                                     # 协议相对
        path = s[2:]
        if path.startswith("upload/") or path.startswith("images/") or re.match(r"^\d{4}/\d{2}/", path):
            return "https://mall.baovbao.com/" + path
        if path.startswith("i/"): return "https://d5ma.img.apiunion.com/" + path
        return "https:" + s
    path = s if s.startswith("/") else "/" + s
    while path.startswith("//"): path = path[1:]
    if path.startswith("/i/") or "/i/" in path[:6]:
        return "https://d5ma.img.apiunion.com" + path          # apiunion
    if "/jfs/" in path or path.startswith("/n12/") or path.startswith("/sku/jfs"):
        return "https://img13.360buyimg.com" + path            # 京东图
    if "imageMogr2" in s or re.search(r"/\d{10,}_\d{2,4}X\d{2,4}_", path):
        return "https://img.picing.com" + path                 # picing
    if path.startswith("/upload/") or path.startswith("upload/"):
        return "https://mall.baovbao.com" + (path if path.startswith("/") else "/" + path)
    if path.startswith("/images/") or re.match(r"^/\d{4}/\d{2}/", path):
        return "https://mall.baovbao.com" + path
    return "https://mall.baovbao.com" + path                   # 兜底
```

| 路径特征 | 域名 |
|---|---|
| `/upload/...`、`/images/...`、`/YYYY/MM/...` | `https://mall.baovbao.com` |
| `/i/...` | `https://d5ma.img.apiunion.com` |
| `/n12/...`、`/sku/jfs/...`、含 `/jfs/` | `https://img13.360buyimg.com` |
| 含 `imageMogr2` 或 `数字_宽X高_` | `https://img.picing.com` |

> 🔴 **血的教训**：早期脚本用 `strip_url()` 把域名剥掉 → 全站商品图片失效。
> 修复方式就是用上面的 `restore_url()` 全量回写一遍。

---

## 8. 批量操作最佳实践

1. **先备份**：拉一次 `goodsCate/lists` 存 JSON
2. **dry-run**：算出变更清单打印出来 review
3. **1 条试改**：`detail` → 改 → 回读校验
4. **批量执行**：`time.sleep(0.08~0.15)` 节流，每 100 条打进度
5. **验证**：重新拉列表统计覆盖率

**性能**：1520 个商品迁移约 **8~12 分钟**（串行，后台并发会触发 502）。

---

## 9. 完整接口清单

见 [API_CATALOG.md](./API_CATALOG.md)（448 个路径，按 73 个模块分组，含探测状态标记）。

---

## 10. 附：Python 通用客户端

```python
import requests, json

BASE = "https://mall.baovbao.com"
auth = json.load(open("auth.json"))          # {admin_id, sid, token}
HH = {
    "uid": str(auth["admin_id"]), "sid": str(auth["sid"]), "token": auth["token"],
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0",
    "Origin": BASE, "Referer": BASE + "/admin/index.html",
}

def post(path, payload=None):
    """所有接口统一走 POST + JSON"""
    return requests.post(BASE + path, json=payload or {}, headers=HH, timeout=30).json()

# 例：拉分类树
r = post("/admin/goodsCate/lists", {"cate_type": 1, "page": 1, "limit": 500})
print(r["code"], len(r["data"]))
```
