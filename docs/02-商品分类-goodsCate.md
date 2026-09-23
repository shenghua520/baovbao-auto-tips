# 02 · 商品分类 goodsCate（14 个接口）

> **分类和品牌共用一张表**，靠 `cate_type` 区分：
> - `cate_type = 1` → 商品分类（大类 + 二级）
> - `cate_type = 3` → 品牌（每个品牌 = L1 + 同名 L2）

本模块是本次改造中**实战最多**的模块，所有字段均经实测验证。

---

## 接口总览

| 接口 | 方法 | 说明 | 探测状态 |
|---|---|---|---|
| `/admin/goodsCate/lists` | POST | 分类/品牌列表 | ✅ code=0 |
| `/admin/goodsCate/add` | POST | 新建 | ✏️ 写操作 |
| `/admin/goodsCate/edit` | POST | 修改 | ✏️ 写操作 |
| `/admin/goodsCate/del` | POST | 删除 | ✏️ 写操作 |
| `/admin/goodsCate/detail` | POST | 详情 | ⚙️ 需 `cate_id` |
| `/admin/goodsCate/tree` | POST | 分类树 | ✅ |
| `/admin/goodsCate/mallCateTree` | POST | 商城分类树 | ✅ |
| `/admin/goodsCate/virtualCateTree` | POST | 虚拟分类树 | ✅ |
| `/admin/goodsCate/getAllTags` | POST | 全部标签 | ✅ |
| `/admin/goodsCate/supplyCates` | POST | 供应链分类（42 个） | ✅ |
| `/admin/goodsCate/supplyCateMap` | POST | 供应链映射 | — |
| `/admin/goodsCate/setSupplyCateMap` | POST | 设置映射 | — |
| `/admin/goodsCate/delSupplyCateMap` | POST | 删除映射 | — |
| `/admin/goodsCate/disable` | POST | 停用 | — |

---

## 一、`lists` — 列表（最常用）

### 请求

```json
{
  "cate_type": 1,
  "page": 1,
  "limit": 500
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `cate_type` | int | ✅ | `1`=分类 / `3`=品牌 |
| `page` | int | | 默认 1 |
| `limit` | int | | 建议 500（一次拉全） |

### 响应

```json
{
  "code": 0,
  "data": [
    {
      "cate_id": 1604,
      "cate_type": 1,
      "cate_name": "学习文具",
      "cate_icon": "/upload/303/system/20260909/56e9006a69b93fbff45d6cc7170e8f48.jpg",
      "cate_pid": 0,
      "cate_path": "",
      "cate_level": 1,
      "shop_type": 1,
      "is_display": 1,
      "period": 72,
      "sort": 1,
      "state": 1,
      "state_text": "正常",
      "mall": "护稚佳品",
      "link": "/pages/classify/classify?cate_id=1604",
      "tags": [],
      "children": [
        {
          "cate_id": 2191, "cate_name": "铅笔", "cate_pid": 1604,
          "cate_level": 2, "sort": 100, "state": 1
        }
      ]
    }
  ]
}
```

### 返回字段说明

| 字段 | 说明 |
|---|---|
| `cate_id` | 分类 ID |
| `cate_type` | `1` 分类 / `3` 品牌 |
| `cate_name` | 名称（**≤6 字符**） |
| `cate_icon` | 图标 URL |
| `cate_pid` | 父 ID（`0`=一级） |
| `cate_level` | 层级（`1` 大类 / `2` 二级） |
| `sort` | 排序，**越小越靠前** |
| `state` | `1` 正常 |
| `children` | 子分类数组 |

### Python 示例

```python
def get_cates(cate_type=1):
    r = post("/admin/goodsCate/lists", {"cate_type": cate_type, "page": 1, "limit": 500})
    return r.get("data", [])

# 建立「二级名 → 父大类」映射
cats = get_cates(1)
sub2parent = {}
for c in cats:
    for ch in c.get("children", []):
        sub2parent[ch["cate_id"]] = c["cate_id"]
```

---

## 二、`add` — 新建分类 / 品牌

### 请求参数（⚠️ 三个铁律）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `cate_name` | string | ✅ | **最长 6 字符** |
| `cate_pid` | int | ✅ | 一级传 `0`；二级传父 `cate_id` |
| `cate_type` | int | ✅ | `1` / `3` |
| **`period`** | int | ✅ | **必须 `72`**（否则 1002） |
| `cate_icon` | string | | 图标 |
| `shop_type` | int | | 通常 `1` |
| `is_display` | int | | `1` 显示 |
| `sort` | int | | 排序 |
| `state` | int | | `1` 正常 |

### 🔴 铁律 1：名称 ≤ 6 字符

```
"谷物/早餐麦片"  → ✗ 报 "分类名称 最大长度为: 6位"
"早餐麦片"      → ✓
"消毒液/衣物除菌液" → ✗
"消毒除菌"        → ✓
```

**新建前务必检查**：

```python
if len(name) > 6:
    print(f"✗ {name} 超长({len(name)}字符)，需缩写")
```

### 🔴 铁律 2：`period` 必须带

漏了直接：

```json
{"code":1002,"msg":"上架的商城 必须为正整数~"}
```

### 🔴 铁律 3：品牌必须 L1 + L2 成对

品牌（`cate_type=3`）是 **cascader 结构**：

```
品牌L1（cate_pid=0）
  └─ 品牌L2（cate_pid=品牌L1的cate_id，同名）
```

商品关联时 `good_brand = [[L1_id, L2_id]]`，**缺一不可**。

### 新建品牌完整示例

```python
def create_brand(name, sort=10):
    # 1) 建 L1
    r1 = post("/admin/goodsCate/add", {
        "cate_name": name, "cate_pid": 0, "cate_type": 3,
        "cate_icon": "", "shop_type": 1, "is_display": 1,
        "period": 72, "sort": sort, "state": 1,
    })
    if r1.get("code") != 0:
        return None, r1.get("msg")

    # 2) 重新拉列表拿 L1 的 cate_id（add 不返回 id！）
    time.sleep(0.3)
    brands = post("/admin/goodsCate/lists", {"cate_type": 3, "page": 1, "limit": 600})["data"]
    l1_id = None
    for b in brands:
        if b.get("cate_pid") == 0 and b["cate_name"] == name:
            l1_id = b["cate_id"]
            break
    if not l1_id:
        return None, "add 后查不到 L1 id"

    # 3) 建同名 L2
    r2 = post("/admin/goodsCate/add", {
        "cate_name": name, "cate_pid": l1_id, "cate_type": 3,
        "cate_icon": "", "shop_type": 1, "is_display": 1,
        "period": 72, "sort": sort, "state": 1,
    })
    return (l1_id, r2.get("code")), r2.get("msg")
```

> ⚠️ **`add` 接口不返回新 ID**！必须重新 `lists` 反查。

---

## 三、`edit` — 修改

参数同 `add`，**额外必填 `cate_id`**。

```python
payload = {
    "cate_id": 2191,
    "cate_name": "铅笔",
    "cate_pid": 1604,
    "cate_type": 1,
    "cate_icon": "",
    "shop_type": 1,
    "is_display": 1,
    "period": 72,
    "sort": 100,
    "state": 1,
}
r = post("/admin/goodsCate/edit", payload)
```

### 典型用途：批量重排 sort

```python
# 按「购买链路」重排二级 sort
SUB_ORDER = ["铅笔", "卷笔刀", "橡皮擦", "修正带", "笔芯", "自动铅笔", "中性笔",
             "钢笔", "尺子", "美术用品", "固体胶", "学生剪刀", "作业本", "书皮", "笔袋"]

cats = post("/admin/goodsCate/lists", {"cate_type": 1, "page": 1, "limit": 500})["data"]
for c in cats:
    if c["cate_id"] != 1604:      # 学习文具
        continue
    for ch in c.get("children", []):
        if ch["cate_name"] in SUB_ORDER:
            new_sort = 100 + SUB_ORDER.index(ch["cate_name"]) * 10
            post("/admin/goodsCate/edit", {
                "cate_id": ch["cate_id"], "cate_name": ch["cate_name"],
                "cate_pid": 1604, "cate_type": 1, "cate_icon": "",
                "shop_type": 1, "is_display": 1, "period": 72,
                "sort": new_sort, "state": 1,
            })
            time.sleep(0.12)
```

---

## 四、`del` — 删除

```json
{"cate_id": 2150}
```

### 🔴 删除失败场景

```json
{"code":10501,"msg":"操作失败, 该分类下有上架中的商品"}
```

**正确顺序**：

```python
# 1) 先迁移商品
# 2) 确认无商品（必须扫 source 1 和 3！）
def count_in_cate(cate_id):
    n = 0
    for src in (1, 3):
        page = 1
        while True:
            r = post("/admin/good/lists", {"page": page, "limit": 100, "type": "all",
                     "good_source": src, "good_field": "good_name", "good_value": "",
                     "brand_id": [], "createtime": []})
            data = r.get("data") or []
            if not data: break
            for g in data:
                gc = g.get("good_cate") or []
                if gc and gc[0].get("cate_id2") == cate_id:
                    n += 1
            if len(data) < 100: break
            page += 1
    return n

# 3) 再删
if count_in_cate(2150) == 0:
    post("/admin/goodsCate/del", {"cate_id": 2150})
```

> 🔑 **关键**：`good/lists` 默认只查 source=1，**供应链商品（source=3）会被漏掉**，导致以为清空了其实没清。

---

## 五、`tree` / `mallCateTree` / `virtualCateTree` — 树结构

### `tree`

```python
r = post("/admin/goodsCate/tree", {"cate_type": 1})
# 返回 list，字段同 lists（含 children 嵌套）
```

实测返回 10 个节点（一级）。

### `mallCateTree`

```python
r = post("/admin/goodsCate/mallCateTree", {"mall_id": 1})
# 返回：cate_id / cate_name / mall_id / children
```

### `virtualCateTree`

```python
r = post("/admin/goodsCate/virtualCateTree", {})
# 返回：mall_id / cate_id / cate_name / children
```

---

## 六、`supplyCates` — 供应链分类

```python
r = post("/admin/goodsCate/supplyCates", {})
# 返回 42 个，字段：id / name / pid / children
```

---

## 七、`getAllTags` — 标签

```python
r = post("/admin/goodsCate/getAllTags", {})
# 实测返回空数组（本商城未配置标签）
```

---

## 八、完整实战：分类体系重塑

本次把后台分类从「9 大类 / 37 二级」改造为「9 大类 / 104 二级」：

```python
CAT_ORDER = ["学习文具", "体育用品", "少儿护理", "少儿穿戴",
             "少儿食品", "家庭日用", "读物潮玩", "米面油品", "家用电器"]
CAT_ID = {"学习文具":1604, "体育用品":1607, "少儿护理":1612, "少儿穿戴":1611,
          "少儿食品":1609, "家庭日用":1608, "读物潮玩":1610, "米面油品":1606,
          "家用电器":1605}

# Step 1: 大类重排 sort（1-9）
for i, cat in enumerate(CAT_ORDER, 1):
    c = next(x for x in cats if x["cate_id"] == CAT_ID[cat])
    post("/admin/goodsCate/edit", {
        "cate_id": CAT_ID[cat], "cate_name": cat, "cate_pid": 0, "cate_type": 1,
        "cate_icon": c.get("cate_icon", ""), "shop_type": 1, "is_display": 1,
        "period": 72, "sort": i, "state": 1,
    })
    time.sleep(0.15)

# Step 2: 按链路新建二级（见第三节）
# Step 3: 迁移商品（见 03 · 商品管理）
# Step 4: 删旧二级（见第四节）
```

### 排序设计原则

| 维度 | 依据 |
|---|---|
| 大类 sort | 业务方指定的顺序（1-9） |
| 二级 sort | **购买链路**（不是字典序） |
| 品牌 sort | 京东/天猫销量档位：头部 `10` / 强腰 `30` / 腰 `60` / 长尾 `200` / 无品牌 `999` |

**购买链路示例（学习文具）**：

```
铅笔 → 卷笔刀 → 橡皮擦 → 修正带 → 笔芯 → 自动铅笔 → 中性笔 → 钢笔
    → 尺子 → 美术用品 → 固体胶 → 学生剪刀 → 作业本 → 书皮 → 笔袋
```

> 逻辑：先有笔 → 能削 → 能擦 → 能改 → 耗材 → 进阶笔 → 作图 → 绘画 → 手工 → 写在哪 → 包起来 → 收起来。
