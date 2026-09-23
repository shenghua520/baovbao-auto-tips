# 04 · 订单管理 order（14 个接口）

## 接口总览

| 接口 | 说明 | 状态 |
|---|---|---|
| `order/lists` | 订单列表 | ✅ |
| `order/listCount` | 订单统计计数 | ✅ |
| `order/detail` | 订单详情（**100 字段**） | ⚙️ 需 `order_id` |
| `order/send` | 发货 | ⚙️ |
| `order/cancel` | 取消 | ✏️ |
| `order/logistics` | 物流 | ✏️ |
| `order/print` | 打印 | ✏️ |
| `order/notice` | 通知 | ✏️ |
| `order/export` | 导出 | ✏️ |
| `order/purchaseSend` | 采购发货 | ✏️ |
| `order/writeoff` | 核销 | ✏️ |
| `order/leaseUpdate` | 租赁更新 | ✏️ |
| `order/yinfa` / `order/yinfaExport` | 银发相关 | ✏️ |

---

## 一、`lists` — 订单列表（62 个字段）

### 请求

```json
{"page": 1, "limit": 20}
```

### 返回字段完整清单（实测 62 个）

| 分类 | 字段 |
|---|---|
| **标识** | `order_id`, `order_cids`, `order_no`, `order_from`, `all_source`, `source_order_no`, `good_source`, `transaction_id` |
| **关联** | `user_id`, `mall_id`, `store_id`, `live_id`, `live_title`, `salesroom_id`, `salesroom` |
| **金额** | `total_price`, `total_express_fee`, `total_amount`, `logistics_amount`, `install_price` |
| **支付** | `pay_info`, `pay_time`, `pay_cart`, `pay_info_text`, `pay_info_arr`, `write_off_time`, `is_first_order` |
| **收货** | `receive_name`, `receive_phone`, `receive_province`, `receive_city`, `receive_area`, `receive_street`, `receive_address` |
| **状态** | `state`, `state_desc`, `state_text`, `tuan_log_state_text`, `deliver_type`, `deliver_type_text`, `good_type`, `good_type_text`, `order_ilk`, `order_ilk_name`, `err_msg`, `can_cancel`, `can_after_sale`, `can_write_off`, `can_receive` |
| **时间** | `created_time` |
| **扩展** | `extend_json`, `movie_info_json`, `purchase_open`, `purchase_type`, `purchase_json`, `contract`, `logistics_cart`, `good_count`, `user`, `child`, `mall_name`, `bill_switch` |

### 示例响应

```json
{
  "code": 0,
  "data": [
    {
      "order_id": 12345,
      "order_no": "2026092312345678",
      "order_from": 1,
      "user_id": 1001,
      "mall_id": 1,
      "total_price": "99.00",
      "total_express_fee": "0.00",
      "total_amount": "99.00",
      "pay_info": 1,
      "pay_time": "2026-09-23 12:00:00",
      "receive_name": "张三",
      "receive_phone": "138****0000",
      "receive_province": "广东省",
      "receive_city": "深圳市",
      "receive_area": "南山区",
      "receive_address": "xxx路xxx号",
      "state": 2,
      "state_text": "待发货",
      "created_time": "2026-09-23 11:59:00",
      "good_count": 2,
      "user": {...},
      "child": [...]
    }
  ]
}
```

---

## 二、`listCount` — 统计计数

### 请求

```json
{}
```

### 响应

```json
{
  "code": 0,
  "data": {
    "countInfo": {...},
    "payMap": {...},
    "payTotal": {...}
  }
}
```

| 字段 | 说明 |
|---|---|
| `countInfo` | 各状态订单数 |
| `payMap` | 支付方式分布 |
| `payTotal` | 支付金额汇总 |

---

## 三、`detail` — 订单详情（100 字段）

### 请求

```json
{"order_id": 12345}
```

### 返回

`dict`，100 个字段。在 `lists` 的 62 个字段基础上，额外包含：

- 商品明细（`child` 展开）
- 支付流水详情
- 物流轨迹
- 售后记录
- 用户完整信息

> 💡 **改订单状态前先调 `detail`**，和 `good` 一样需要全量回填思路。

---

## 四、状态字段对照

| `state` | `state_text` | 含义 |
|---|---|---|
| 0 | 待支付 | 未付款 |
| 1 | 已支付 | — |
| 2 | 待发货 | 已付款待发 |
| 3 | 已发货 | — |
| 4 | 已完成 | — |
| 5 | 已取消 | — |
| 6 | 退款中 | — |

> ⚠️ 实际值以后端返回为准，不同 `order_ilk`（订单类型）可能不同。

### 操作权限字段（很有用）

| 字段 | 说明 |
|---|---|
| `can_cancel` | 能否取消 |
| `can_after_sale` | 能否售后 |
| `can_write_off` | 能否核销 |
| `can_receive` | 能否收货 |

```python
# 只处理"可发货"的订单
orders = post("/admin/order/lists", {"page":1,"limit":100})["data"]
sendable = [o for o in orders if o.get("state") == 2]
```

---

## 五、其他模块关联

| 模块 | 接口 | 说明 |
|---|---|---|
| 售后 | `/admin/AfterSale/lists` | 售后列表 |
| 售后 | `/admin/AfterSale/handle` / `refund` / `reject` | 处理/退款/拒绝 |
| 审核 | `/admin/OrderReview/lists` / `check` | 订单审核 |
| 扫码 | `/admin/Scanorder/lists` | 扫码订单 |
| 团购 | `/admin/tuan/lists` | 团购订单 |

---

## 六、实战示例：拉全部待发货订单

```python
def get_pending_orders():
    result, page = [], 1
    while True:
        r = post("/admin/order/lists", {"page": page, "limit": 100})
        data = r.get("data") or []
        if not data:
            break
        result.extend([o for o in data if o.get("state") == 2])
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.08)
    return result
```
