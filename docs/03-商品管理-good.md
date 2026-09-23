# 03 · 商品管理 good（25 个接口）

> 本模块是**批量改造的核心**。`good/edit` 是全站最复杂的接口——必须全量回填 30+ 字段。

---

## 接口总览

| 接口 | 说明 | 状态 |
|---|---|---|
| `good/lists` | 商品列表 | ✅ |
| `good/detail` | 商品详情（改商品必先调） | ⚙️ 需 `good_id` |
| `good/edit?good_id=` | **修改商品**（最复杂） | ✏️ |
| `good/add` | 新建商品 | ✏️ |
| `good/del` | 删除 | ✏️ |
| `good/state` | 上下架 | ✏️ |
| `good/sort` | 排序 | ✏️ |
| `good/commend` | 推荐 | ✏️ |
| `good/check` | 审核 | ⚙️ |
| `good/export` / `good/import` | 导出 / 导入 | ✏️ |
| `good/skuLists` | SKU 列表 | ✅ |
| `good/changePrice` | 改价 | ✏️ |
| `good/changeStock` | 改库存 | ✏️ |
| `good/changeSkuState` | 改 SKU 状态 | ✏️ |
| `good/changeProfit` | 改利润 | ✏️ |
| **`good/batchFakeSale`** | **批量改销量** | ✏️ |
| `good/setStockwarn` | 库存预警 | ✏️ |
| `good/discount` | 折扣 | ✏️ |
| `good/paysetting` | 支付设置 | ✏️ |
| `good/reward` | 奖励 | ✏️ |
| `good/asyncSupply` | 同步供应链 | ✏️ |
| `good/asyncUpstream` | 同步上游 | ✏️ |
| `good/asyncVirtual` | 同步虚拟 | ✏️ |
| `good/asyncLife` | 同步生活 | ✏️ |

---

## 一、`lists` — 商品列表

### 请求

```json
{
  "page": 1,
  "limit": 100,
  "type": "all",
  "good_source": 1,
  "good_field": "good_name",
  "good_value": "",
  "brand_id": [],
  "createtime": []
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `page` / `limit` | int | 分页 |
| `type` | string | `"all"` |
| **`good_source`** | int | 🔴 **`1`=自营，`3`=供应链。传 `"all"` 拉不到！** |
| `good_field` | string | 搜索字段（`good_name`） |
| `good_value` | string | 搜索关键词 |
| `brand_id` | array | 品牌筛选 |
| `createtime` | array | 时间范围 `[start, end]` |

### 🔴 关键：`good_source` 必须分别查

```python
# ❌ 错误：传 "all" 返回空
post("/admin/good/lists", {"good_source": "all"})   # 拉不到数据！

# ✅ 正确：循环 1 和 3
all_goods = []
for src in (1, 3):
    page = 1
    while True:
        r = post("/admin/good/lists", {
            "page": page, "limit": 100, "type": "all", "good_source": src,
            "good_field": "good_name", "good_value": "", "brand_id": [], "createtime": []
        })
        data = r.get("data") or []
        if not data:
            break
        all_goods.extend(data)
        if len(data) < 100 or page > 40:
            break
        page += 1
        time.sleep(0.08)
```

> 本商城：自营 1520 + 供应链 14 = **1534**。漏查 source=3 会少 14 个商品（导致删分类时失败）。

### 响应字段（节选）

```json
{
  "code": 0,
  "data": [
    {
      "good_id": 2645,
      "good_name": "伊利0蔗糖八连杯-伊利0蔗糖八连杯1*16*90g-16-16",
      "good_source": 1,
      "state": 1,
      "good_cate": [
        {"good_id":2645,"mall_id":1,"cate_id1":1609,"cate_id2":2232,
         "store_id":0,"mall":"护稚佳品","cate1":"少儿食品","cate2":"牛奶/奶制品"}
      ],
      "good_brand": [
        {"good_id":2645,"brand_id1":2147,"brand_id2":2148,
         "brand1":"伊利","brand2":"伊利"}
      ]
    }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `good_id` | 商品 ID |
| `good_name` | 商品名称 |
| `good_source` | `1` 自营 / `3` 供应链 |
| `state` | `1` 上架 |
| `good_cate[]` | 分类（三层：`mall_id` / `cate_id1` / `cate_id2`） |
| `good_brand[]` | 品牌（`brand_id1` / `brand_id2`） |

---

## 二、`detail` — 商品详情（改商品前必调）

### 请求

```json
{"good_id": 2645}
```

### 返回字段（100+ 个，完整清单）

| 分类 | 字段 |
|---|---|
| **基础** | `good_id`, `good_name`, `good_desc`, `good_alias`, `good_source`, `good_type`, `upstream_good_id`, `source_id`, `source_goods_id` |
| **分类品牌** | `good_cate[]`, `good_brand[]`, `tag_ids[]` |
| **图片** | `cover_img`, `wheel_img[]`, `wheel_img_arr[]`, `detail_img[]`, `detail_img_arr[]` |
| **内容** | `content`, `recommend`, `good_desc`, `promise[]` |
| **规格 SKU** | `skus[]`, `spec_name1`, `spec_name2`, `spec_name3`, `spec_name4` |
| **价格库存** | `cost_price`, `sale_price`, `crossed_price`, `stock`, `stock_warn`, `fake_sale` |
| **购买限制** | `buy_min`, `buy_max`, `unit`, `sort` |
| **视频** | `video_type`, `video_url`, `video_url_upload`, `video_buyed` |
| **开关** | `install_open`, `lease_open`, `purchase_open`, `store_id` |

### SKU 结构

```json
{
  "sku_id": 12345,
  "good_id": 2645,
  "spec_val1": "默认",
  "spec_val2": "",
  "spec_val3": "",
  "cover_img": "/upload/0/supply/9/2413039_606223684.jpeg",
  "cost_price": 20.5,
  "sale_price": 29.9,
  "crossed_price": 39.9,
  "stock": 100,
  "state": 1,
  "pay_setting": [{"checked":0,"account_id":"","money":0}]
}
```

---

## 三、`edit?good_id=` — 修改商品（🔴 最复杂）

### 请求方式

```
POST /admin/good/edit?good_id=2645
Content-Type: application/json
Body: { ...全量字段... }
```

> 🔴 **`good_id` 放 URL query**，其余字段放 JSON body。
> 🔴 **必须用 JSON**，form-data 会报 `品牌参数错误`。

### 关键字段格式

| 字段 | 格式 | 示例 |
|---|---|---|
| `good_cate` | `[[mall_id, cate_id1, cate_id2]]` | `[[1, 1609, 2232]]` |
| `good_brand` | `[[brand_id1, brand_id2]]` | `[[2147, 2148]]` |
| `cover_img` | 完整 URL 字符串 | `https://mall.baovbao.com/upload/...` |
| `wheel_img` | URL 数组 | `["https://...", ...]` |
| `skus` | SKU 对象数组 | 见下 |
| `fake_sale` | int | 展示销量 |

### 🔴 铁律：必须全量回填

**只传要改的字段 = 丢数据**。正确做法：

```python
detail = post("/admin/good/detail", {"good_id": gid})["data"]
body = build_body(detail, new_good_cate)     # 从 detail 回填全部字段
post(f"/admin/good/edit?good_id={gid}", body)
```

### 完整 `build_body` 模板（可直接复用）

```python
def restore_url(u):
    """见 08 · 图片与文件规范"""
    ...  # 完整实现见文档 08

def build_body(detail, good_cate):
    """从 detail 全量回填，只改 good_cate"""
    # ---- SKU 处理（去重 + 图片修复）----
    skus, seen = [], set()
    for s in detail.get("skus") or []:
        key = (s.get("spec_val1"), s.get("spec_val2"), s.get("spec_val3"))
        if key in seen:
            continue                      # 🔴 去重：规格重复会导致整单 edit 失败
        seen.add(key)
        o = dict(s)
        if o.get("cover_img"):
            o["cover_img"] = restore_url(o["cover_img"])
        if o.get("wheel_img"):
            o["wheel_img"] = [restore_url(x) for x in o["wheel_img"]]
        if o.get("detail_img"):
            o["detail_img"] = [restore_url(x) for x in o["detail_img"]]
        if not o.get("pay_setting"):
            o["pay_setting"] = [{"checked": 0, "account_id": "", "money": 0}]
        if not o.get("spec_val1"):
            sd = o.get("spec_data") or []
            o["spec_val1"] = (sd[0].get("val") if sd else "默认") or "默认"
        skus.append(o)
    if not skus:
        skus = [{
            "cover_img": "", "spec_val1": "默认", "spec_val2": "",
            "unit_quatity": 1,
            "cost_price": detail.get("cost_price") or 0,
            "sale_price": detail.get("sale_price") or 0,
            "crossed_price": detail.get("crossed_price") or 0,
            "stock": 0, "state": 1,
            "pay_setting": [{"checked": 0, "account_id": "", "money": 0}],
        }]

    # ---- 品牌 ----
    mapped = []
    for b in detail.get("good_brand") or []:
        if isinstance(b, dict):
            mapped.append([b.get("brand_id1") or "", b.get("brand_id2") or ""])
        elif isinstance(b, (list, tuple)):
            mapped.append([b[0] if b else "", b[1] if len(b) > 1 else ""])
    wheel = [restore_url(x) for x in (detail.get("wheel_img") or [])]
    dimgs = [restore_url(x) for x in (detail.get("detail_img") or [])]

    return {
        "good_name": detail.get("good_name") or "",
        "good_alias": detail.get("good_alias") or "",
        "good_source": detail.get("good_source"),
        "good_type": detail.get("good_type"),
        "good_brand": mapped or [["", ""]],
        "good_cate": good_cate,                       # [[1, cate1, cate2]]
        "tag_ids": detail.get("tag_ids") or [],
        "fake_sale": detail.get("fake_sale") or 0,
        "good_desc": detail.get("good_desc") or "",
        "promise": detail.get("promise") or [],
        "store_id": detail.get("store_id") or 0,
        "install_open": detail.get("install_open") or 0,
        "lease_open": detail.get("lease_open") or 0,
        "purchase_open": detail.get("purchase_open") or 0,
        "cover_img": restore_url(detail.get("cover_img")),
        "wheel_img": wheel,
        "wheel_img_arr": [{"name": "", "url": x} for x in wheel],
        "video_type": detail.get("video_type") or 1,
        "video_url": detail.get("video_url") or "",
        "video_url_upload": detail.get("video_url_upload") or "",
        "video_buyed": detail.get("video_buyed") or 0,
        "detail_img": dimgs,
        "detail_img_arr": [{"name": "", "url": x} for x in dimgs],
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
        "skus": skus,
        "stock_warn": detail.get("stock_warn") or 0,
    }
```

### 批量修改商品分类（实战）

```python
def batch_change_cate(changes):
    """changes: [{'good_id': 2645, 'new_c1_id': 1609, 'new_c2_id': 2232}]"""
    ok = fail = 0
    for i, c in enumerate(changes, 1):
        try:
            detail = post("/admin/good/detail", {"good_id": c["good_id"]}).get("data") or {}
            body = build_body(detail, [[1, c["new_c1_id"], c["new_c2_id"]]])
            r = post(f"/admin/good/edit?good_id={c['good_id']}", body)
            if r.get("code") == 0:
                ok += 1
            else:
                fail += 1
                print(f"✗ {c['good_id']}: {r.get('msg')}")
            time.sleep(0.12)                       # 🔴 节流，别并发
        except Exception as e:
            fail += 1
            print(f"ERR {c['good_id']}: {e}")
        if i % 100 == 0:
            print(f"进度 {i}/{len(changes)} ok={ok} fail={fail}", flush=True)
    return ok, fail
```

> ⏱ **性能**：1534 个商品约 **8~12 分钟**（串行 + 0.12s 节流）。并发会触发 502。

---

## 四、`skuLists` — SKU 列表

```python
r = post("/admin/good/skuLists", {"good_id": 2645})
# 返回：sku_id / good_id / good_source / store_id / good_name / unit / ...
```

---

## 五、销量设置（用户画像）

### 方式 A：`batchFakeSale`（批量接口）

### 方式 B：逐商品 `edit` 改 `fake_sale`（推荐，可控）

```python
# 按用户画像分档（小学生+初中生，决策者=女性家长）
SALES = {
    '铅笔': (3000, 9000), '抽纸/面巾纸': (3000, 9000), '牛奶/奶制品': (3000, 9000),  # 高频
    '儿童牙膏': (2500, 8000), '书包': (800, 3000),                              # 中频
    '护眼台灯': (600, 2500), '扫地机器人': (80, 400),                            # 低频高客单
}

def pick_sale(lo, hi):
    """偏态随机：15% 爆款靠上限 / 40% 中位 / 45% 靠下限"""
    r = random.random()
    if r < 0.15:   v = random.uniform(hi * 0.7, hi)
    elif r < 0.55: v = random.uniform((lo + hi) / 2 * 0.8, hi * 0.7)
    else:          v = random.uniform(lo, (lo + hi) / 2 * 0.8)
    return int(round(v / 10) * 10)        # 取整到 10，更真实
```

**实测分布**（1534 商品）：

| 区间 | 数量 |
|---|---|
| 5000-9999 | 102 |
| 2000-4999 | 763 |
| 500-1999 | 651 |
| <500 | 18 |

> 💡 **别太假**：全 1000 一眼假。用偏态 + 区间随机最自然。

---

## 六、`add` — 新建商品

字段同 `edit`，但**不需要 `good_id`**（也是走 query 或不带）。因实战中未使用，建议用 `edit` 改现有商品，或参考前端 JS 调用。

---

## 七、常见错误

| 错误 | 原因 | 解决 |
|---|---|---|
| `品牌参数错误` | form-data 传参 | 改 JSON body |
| `good_id` 无效 | URL 没带 `good_id` | `?good_id=xxx` |
| SKU 规格重复导致 edit 失败 | 同一 `(spec_val1,2,3)` 出现两次 | 去重（见 `build_body`） |
| 图片丢失 | URL 被剥域名 | 见 **08 · 图片与文件规范** |
| 502 Bad Gateway | 请求过快/并发 | 加 `time.sleep(0.1~0.15)` |
