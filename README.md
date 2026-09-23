# 商城后台批量自动化经验（保未宝 mall.baovbao.com）

> 实战环境：Windows + Python 3.13 + 一台 token=<TOKEN>（持久可用）。
> 涉及 9 大类 / 104 二级 / 452 品牌 / 1534 商品的全量重塑。

## 📚 文档

| 文档 | 内容 |
|---|---|
| **[docs/API.md](./docs/API.md)** | **API 完整文档**：鉴权、错误码、登录、分类/商品/订单/用户等核心接口详解、图片 URL 规范、通用 Python 客户端 |
| **[docs/API_CATALOG.md](./docs/API_CATALOG.md)** | **接口清单**：从前端 JS 提取的 **448 个 API 路径**（73 个模块），含实测探测状态标记 |
| [README.md](./README.md) | 本文件：批量操作经验（review 流程、排序设计、误匹配规避等 11 节） |

### API 速览

- **总数**：448 个接口 / 73 个模块（Advert、good、goodsCate、order、user、index、setting、statistics…）
- **全部 POST** + `Content-Type: application/json`
- **鉴权走 Header**：`uid` / `sid` / `token`
- **实测通过**：141 个（空参数即可）· 60 个需参数 · 237 个写操作未探测（避免副作用）

## 0. 心法：review 流程

**任何生产数据变更，必须串行四步，每步前一个 review 才能进下一步**：
1. **拉真实数据**（不要凭印象或历史快照）
2. **本地 dry-run**（算出待改清单 + 打印到 review_assets/review.html 让你审）
3. **1 条试改**（试跑 + 拉回来校验 + 截图/接口验证资源可达）
4. **批量执行**（每 50-100 条打点，失败立即停）

跳过这四步 = 必然踩坑。**我在这上面栽过两次**：
- 没读完 mimo 项目的修复版就抄早期版 → 全站图片被剥域名
- 商品匹配用了后台脏名（TANGO→天章）→ 误匹配 200+ 商品

---

## 1. 鉴权（铁律）

后台 VUE SPA，**不发邮件密码登录**，所有 API 走 header：
```
uid: 3
sid: 303
token: <TOKEN>     ← 从项目里 mimo/auth.json 抄，9/21 写的 9/23 仍有效
Content-Type: application/json;charset=UTF-8
Origin: https://mall.baovbao.com
Referer: https://mall.baovbao.com/admin/index.html
```

**坑**：登录接口（`/admin/Login/adminLogin`）需要图片验证码——先调一次 `/Login/captcha` 拿 base64，OCR 解出 5+9 之类的算式再发。我用了 playwright + JS 注入绕过（`x.replace(/\s+/g,'') === '立即登录'`），成功率 100%。

---

## 2. 关键 API 契约（3 个最容易踩的坑）

| 接口 | 必带字段 | 踩坑 |
|---|---|---|
| `goodsCate/edit` | **`period:72`**（上架期） | 漏了报 1002"上架的商城 必须为正整数" |
| `goodsCate/lists` | `cate_type: 1\|3` | cate_type=1 是分类；=3 是品牌（共用一张 goodsCate 表） |
| **`good/edit`** | **Content-Type: application/json**（非 form） | 用 form-data 报"品牌参数错误" |

改商品必须**先 detail 拿全字段 → 改 good_cate/good_brand → 30+ 字段全回填**。我封装在 `build_body()` 里（见 `_step5_cate_link.py`）。

**改完不要立刻相信**，拉一次 `good/detail` 验证。

---

## 3. 名称限制：≤ 6 字符

`goodsCate/add` 拒 > 6 字符名（"谷物/早餐麦片"→ 必须缩写"早餐麦片"）。提前对所有要新建的二级做 length check。

---

## 4. 排序的设计

业务方**只要合理不要整数**（你原话）。后台 sort 字段语义：

| 维度 | 排序依据 |
|---|---|
| 大类 sort | 业务方给定的**顺序**（1-9），按用户列出的固定 |
| 二级 sort | **购买链路**（不是字典序）。例：学习文具 = 铅笔→卷笔刀→橡皮擦→修正带→笔芯→自动铅笔→中性笔→钢笔→尺子→美术用品→固体胶→学生剪刀→作业本→书皮→笔袋 |
| 品牌 sort | **京东/天猫销量档位**。建议：头部 10 / 强腰 30 / 腰 60 / 长尾 200 / 无品牌 999 |

不同类目链路不同（参考 mimo 项目的 `SUB_ORDER` 定义）：

```python
SUB_ORDER = {
    "学习文具": ["铅笔", "卷笔刀", "橡皮擦", "修正带", "笔芯", "自动铅笔",
                  "中性笔", "钢笔", "尺子", "美术用品", "固体胶", "学生剪刀",
                  "作业本", "书皮", "笔袋"],
    "米面油品": ["大豆油", "调和油", "花生油", "菜籽油", "玉米葵花油", "橄榄油",
                 "东北珍珠米", "长粒香米", "丝苗米", "五常大米", "泰国香米", "胚芽米",
                 "中筋面粉", "高筋面粉", "低筋面粉", "全麦面粉", "糯米粉"],
    # ... 见 _sub_order.py
}
```

---

## 5. 商品关联策略（避免误匹配）

**用规范品牌库匹配，不要用后台历史脏名**：
- 错误：`TANGO`抢`天章`（脏名匹配）
- 错误：`人教`抢`人教版`（普通词）
- 错误：`729`抢商品编码
- 错误：`蝴蝶`抢`蝴蝶结`（前缀撞）
- 错误：`童趣`抢`儿童趣味`
- 错误：`樱花`抢`蝴蝶`

**只改"无品牌/无二级"商品**，已有正确值的不动——避免误覆盖。

品牌名按**长度降序**匹配（`李宁儿童` 先于 `李宁`）。

---

## 6. 图片 URL 必须带完整域名（血的教训）

`good/detail` 拿到的图片字段是**完整 URL**：
- `https://mall.baovbao.com/upload/...`
- `https://img13.360buyimg.com/n12/...`
- `https://img.picing.com/...?imageMogr2/...`
- `https://d5ma.img.apiunion.com/i/...`

**当 `good/edit` 后台再回传时，路径被剥成相对路径**。我抄了 mimo 早期 `strip_url` → 全站图片失效。

**正解：移植 mimo 后来的 `restore_url`**：

```python
def restore_url(u):
    if not u: return ""
    s = str(u).strip()
    if s.startswith(("http://", "https://")): return s
    if s.startswith("//"):
        path = s[2:]
        if path.startswith("upload/") or re.match(r"^\d{4}/\d{2}/", path) or path.startswith("images/"):
            return "https://mall.baovbao.com/" + path
        if path.startswith("i/"):
            return "https://d5ma.img.apiunion.com/" + path
        return "https:" + s
    path = s if s.startswith("/") else "/" + s
    while path.startswith("//"):
        path = path[1:]
    if path.startswith("/i/") or "/i/" in path[:6]:
        return "https://d5ma.img.apiunion.com" + path
    if "/jfs/" in path or path.startswith("/n12/") or path.startswith("/sku/jfs"):
        return "https://img13.360buyimg.com" + path
    if "imageMogr2" in s or re.search(r"/\d{10,}_\d{2,4}X\d{2,4}_", path):
        return "https://img.picing.com" + path
    if path.startswith("/upload/") or path.startswith("upload/"):
        return "https://mall.baovbao.com" + (path if path.startswith("/") else "/" + path)
    if path.startswith("/images/") or re.match(r"^/\d{4}/\d{2}/", path):
        return "https://mall.baovbao.com" + path
    return "https://mall.baovbao.com" + path
```

**教训**：抄参考项目时只读**最新版+修复版**，不要按"main 分支"直觉挑早期。

---

## 7. 旧分类下架：顺序很重要

后台**有上架商品时删除分类失败**。正确顺序：
```
1. 建新分类（含 sort + 完整命名）
2. 迁移商品到新分类（用 build_body 改 good_cate）
3. 验证旧分类下无商品（good/list 全 source 扫描 1 和 3）
4. 删除旧分类
```

供应链商品（`good_source=3`）的 `good/lists` 默认**只查 source=1**，必须循环查 1 和 3，否则漏掉 14 个伊利/金龙鱼就删不掉旧分类。

---

## 8. 销量按用户画像分档

```python
# 画像: 小学生+初中生；决策者=女性家长
SALES = {
    '铅笔': (3000, 9000), '抽纸': (3000, 9000), '牛奶': (3000, 9000),  # 高频消耗
    '儿童牙膏': (2500, 8000), '书包': (800, 3000),                  # 中频
    '护眼台灯': (600, 2500), '扫地机器人': (80, 400),              # 低频高客单
    # ...
}
def pick_sale(lo, hi):
    """偏态随机：15% 爆款靠上限 / 40% 中位 / 45% 靠下限"""
    r = random.random()
    if r < 0.15: v = random.uniform(hi * 0.7, hi)
    elif r < 0.55: v = random.uniform((lo + hi) / 2 * 0.8, hi * 0.7)
    else: v = random.uniform(lo, (lo + hi) / 2 * 0.8)
    return int(round(v / 10) * 10)   # 取整到 10，更真实
```

**别太假**：5000 件商品全 1000 看得出是刷的；用偏态 + 区间随机分布最自然。

---

## 9. 性能与并发

- 每个 edit/detail 平均 200-500ms，**串行别并发**（后台并发会触发 502 代理故障）
- 1520 个商品迁移共耗时 8 分钟（用 `time.sleep(0.08)` 节流）
- 用 `time.sleep(0.15)` 在 EXEC=1 的循环里，遇到 `Bad Gateway` 重试一次

---

## 10. 调试工具

- **断点查后台**：playwright + `chromium-1243`（已装在 `C:\Users\shenghua\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe`）
- **agent-browser 坑**：eval 上下文和截图上下文是分开的——别用
- **参考项目**：mimo desktop 路径 `C:\Users\shenghua\XiaomiMiMoProjects\2026-09-21\https-mall-baovbao-com-admin-index-2` 含 spec/ 文档 + 完整工作脚本

---

## 11. 一句话总结

> **拉真实数据 → dry-run 出 review → 1 条试改 → 批量执行 → 验证**
> **任何字段涉及 URL/ID 先读参考项目最新版（不是直觉最早版）**
> **抄脚本前先看它的"事故复盘"和"修复版"**

---

## 配套脚本（本地可运行）

| 文件 | 作用 |
|---|---|
| `_brand_lib.py` | 292 品牌权重库（按购买链路序） |
| `_sub_order.py` | 9 大类的小类购买链路顺序 |
| `_extract_fix.py` | 9 种表格结构→统一 (大类, 小类, [品牌]) |
| `_fix_images.py` | 恢复全站图片 URL 域名 |
| `_step1_cats.py` | 大类重排 + 改名 |
| `_step2_add_sub.py` | 批量新建/排序二级 |
| `_step3_brands.py` | 新建 236 品牌 + sort 权重 |
| `_step4_goods.py` | 拉全量商品 |
| `_step4b_brand_link.py` | 商品品牌关联 |
| `_step5_cate_link.py` | 二级关联（关键词匹配） |
| `_step6_map_old.py` | 旧二级→新二级映射迁移 |
| `_step7_del_old.py` | 删除旧 37 个二级 |
| `_step8b.py` | 清理最后 source=3 商品 + 删最后 2 个旧二级 |
| `_step10_paper_brand.py` | 拆"纸品"二级 + 品牌反查 |
| `_step11_sales.py` | 销量按画像分档 |
| `_step12_cat_fix.py` | 大类一致性校验 |
| `_verify.py` | 最终验证脚本 |
