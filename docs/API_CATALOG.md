# 保未宝商城后台 · API 完整清单

> 从前端 JS 提取的全部接口路径（共 448 个，73 个模块）。
> 状态说明：`code=0`=探测通过（参数可为空）；`1002`=需传参数；`SKIP`=写操作未探测（避免副作用）。

| 模块 | 数量 | 接口 |
|---|---|---|
| **Advert** | 7 | ✏️add · ✅config · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **AfterSale** | 4 | ✏️handle · ✅lists · ✏️refund · ✏️reject |
| **Cps** | 8 | ✏️add · ✅config · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists · ✅type_list |
| **FinanceAccount** | 4 | ✏️cashexport · ✅cashlog · ✏️export · ✅flow |
| **FreeQueue** | 3 | ✏️cancel · ❓config · ✅lists |
| **FreeQueueTwo** | 5 | ✏️cancel · ⚙️config · ✅lists · ✅logLists · ✅poolLists |
| **GasStation** | 4 | ❓lists · ✅redReceiveList · ✅redReceiveLog · ✏️setConfig |
| **Life** | 2 | ⚙️config · ✅lists |
| **LimitWithdraw** | 2 | ✅config · ✅lists |
| **Login** | 5 | ✏️adminLogin · ✏️autoLoginByAccount · ✏️captcha · ✏️getAccountsByPhone · ✏️yinfa |
| **Movie** | 3 | ✅SupplyBalance · ⚙️config · ✅lists |
| **OrderReview** | 2 | ⚙️check · ✅lists |
| **PK** | 2 | ✅config · ⚙️lists |
| **Scanorder** | 1 | ✅lists |
| **Statistics** | 2 | ⚙️teamPerformance · ✅userPerformance |
| **VideoSign** | 2 | ✅config · ✅lists |
| **Virtual** | 2 | ⚙️config · ✅lists |
| **activity** | 5 | ✏️add · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **addon** | 5 | ⚙️detail · ✏️install · ✅lists · ✏️payinfo · ✏️upgrade |
| **admin** | 14 | ✏️add · ✏️changeNicknamePhone · ✏️changePassword · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ⚙️getTicket · ✅lists · ✅menu · ✅rules · ✏️setDefaultPassword · ✏️setPayPassword · ✏️yinfa |
| **agent** | 9 | ✏️add · ⚙️check · ✅config · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ⚙️getAgentApplyUsers · ✅lists |
| **ancestralhall** | 7 | ✏️add · ✏️disable · ✏️edit · ✅getConfig · ✅lists · ✏️rank · ✏️setConfig |
| **article** | 12 | ✏️articleAdd · ✏️articleDel · ✏️articleDetail · ✏️articleDisable · ✏️articleEdit · ✏️articleLists · ✏️cateAdd · ✏️cateDel · ✏️cateDisable · ✏️cateEdit · ✏️cateLists · ⚙️config |
| **bonus** | 3 | ✅config · ✅lists · ✅logs |
| **card** | 20 | ✏️add · ✏️cardQrcodeExport · ⚙️config · ✏️del · ⚙️detail · ✏️disable · ✏️distribute · ✏️edit · ✏️export · ✏️freeze · ⚙️getUserIdsByCardId · ✅lists · ✅logs · ⚙️ppt · ✏️qrcodeDisable · ✏️qrcodeRechargeList · ✏️qrcodeSet · ✅qrcodeSetList · ✏️unfreeze · ✅usage |
| **catalogue** | 10 | ⚙️config · ✏️del · ✅lists · ✏️pptDel · ✏️pptLists · ✏️templateAdd · ✏️templateDel · ✏️templateDetail · ✏️templateEdit · ✏️templateLists |
| **contribution** | 3 | ✅getConfig · ✅lists · ✏️setConfig |
| **copartner** | 7 | ✏️add · ⚙️check · ✏️disable · ✏️edit · ✅getConfig · ✅lists · ✏️setConfig |
| **coupon** | 6 | ✏️add · ✏️couponUser · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **crowner** | 6 | ⚙️check · ✅config · ✏️del · ⚙️detail · ✏️edit · ✅lists |
| **digital** | 3 | ✅getConfig · ✅logLists · ✏️setConfig |
| **financeAccount** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **freight** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **giftbag** | 5 | ✏️add · ✏️disable · ✏️edit · ✅lists · ⚙️logs |
| **good** | 25 | ✏️add · ✏️asyncLife · ✏️asyncSupply · ✏️asyncUpstream · ✏️asyncVirtual · ✏️batchFakeSale · ✏️changePrice · ✏️changeProfit · ✏️changeSkuState · ✏️changeStock · ⚙️check · ✏️commend · ✏️del · ⚙️detail · ✏️discount · ✏️edit · ✏️export · ✏️import · ✅lists · ✏️paysetting · ✏️reward · ✏️setStockwarn · ✅skuLists · ✏️sort · ✏️state |
| **goodsCate** | 14 | ✏️add · ✏️del · ✏️delSupplyCateMap · ⚙️detail · ✏️disable · ✏️edit · ✅getAllTags · ✅lists · ✅mallCateTree · ✏️setSupplyCateMap · ✏️supplyCateMap · ✏️supplyCates · ✅tree · ✅virtualCateTree |
| **hotel** | 4 | ❓SupplyBalance · ❓getConfig · ❓lists · ✏️setConfig |
| **increaccount** | 2 | ❓getConfig · ✏️setConfig |
| **index** | 15 | ✅addons · ✅express · ✅financeStatic · ✅getRegions · ✅index · ✅logs · ✅mallStatic · ✅message · ✅orderStatic · ✅screen · ✅shopOrderStatic · ✏️taskCancel · ✅tasks · ✏️uploadFile · ✏️uploadImg |
| **live** | 1 | ⚙️getLink |
| **login** | 4 | ✏️lpy_register · ✏️lpy_send · ✏️reset · ✏️sms |
| **mall** | 7 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists · ⚙️pageDetail |
| **order** | 14 | ✏️cancel · ❓detail · ✏️export · ✏️leaseUpdate · ✅listCount · ✅lists · ✏️logistics · ✏️notice · ✏️print · ✏️purchaseSend · ⚙️send · ✏️writeoff · ✏️yinfa · ✏️yinfaExport |
| **page** | 5 | ✏️add · ✏️del · ✏️disable · ✏️edit · ✅lists |
| **partner** | 7 | ✏️add · ⚙️check · ✏️disable · ✏️edit · ✅getConfig · ✅lists · ✏️setConfig |
| **pointrefund** | 4 | ✅getConfig · ✏️logList · ✅refundList · ✏️setConfig |
| **poollottery** | 4 | ✅getConfig · ✅pools · ✏️setConfig · ✅users |
| **push31** | 4 | ✅getConfig · ✅lists · ✅parentlogs · ✏️setConfig |
| **pvbv** | 6 | ✏️changeParent · ✅cultivatePerform · ✅cultivateStats · ⚙️performLists · ✅performLog · ✅placeLists |
| **qht** | 3 | ✏️circulateList · ❓config · ✏️tradeList |
| **realname** | 3 | ⚙️check · ✅config · ✅lists |
| **reduce** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **rewardInvite** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **rewardOrder** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **rewardPlat** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **rewardProfile** | 2 | ✅getConfig · ✏️setConfig |
| **role** | 5 | ✏️add · ⚙️detail · ✏️edit · ✅groups · ✅rules |
| **salesroom** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **setting** | 28 | ✅alone · ⚙️baseinfo · ⚙️docs · ✅entry · ✏️fieldDel · ✏️fieldEdit · ✅fieldList · ⚙️fourth · ❓getSmbaoLeft · ✏️kuaidi · ✏️kuaidiSenderAdd · ✏️kuaidiSenderDel · ✏️kuaidiSenderEdit · ✅kuaidiSenderList · ✏️kuaidiSenderState · ✏️kuaidiTemplateAdd · ✏️kuaidiTemplateDel · ✏️kuaidiTemplateEdit · ✅kuaidiTemplateList · ✏️kuaidiTemplateState · ✅live · ✅pagestyle · ✅pay · ❓pvbv · ⚙️send · ✅subaccount · ⚙️supply · ✅third |
| **signin** | 2 | ⚙️config · ✅lists |
| **ssg** | 3 | ✅config · ⚙️detail · ✅lists |
| **statistics** | 10 | ✅conversion · ✅financeDay · ✅goodsCateSell · ✅goodsSell · ✅grossProfit · ✅orderGoodsStats · ✅orderStat · ✏️orderStatExport · ✅sourceFinance · ✅survey |
| **store** | 8 | ✏️add · ⚙️check · ✅config · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **system** | 3 | ✅address · ✅articles · ✅functions |
| **tabbar** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **trade** | 2 | ✅config · ✅lists |
| **tsg** | 4 | ✅config · ⚙️detail · ✅lists · ⚙️structure |
| **tuan** | 7 | ✏️cancel · ✏️choose · ✏️choosedel · ✅config · ✏️goodDesc · ✏️goods · ✅lists |
| **user** | 10 | ✏️changAccount · ✏️changLevel · ✏️customize · ✏️del · ✏️disable · ✏️export · ✏️import · ✅lists · ⚙️logLists · ✏️resetPassword |
| **userFinance** | 9 | ✏️add · ✏️commission · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✏️export · ✅flow · ✅lists |
| **userLevel** | 6 | ✏️add · ✏️del · ⚙️detail · ✏️disable · ✏️edit · ✅lists |
| **water** | 1 | ✏️package |
| **withdraw** | 5 | ✏️batchAgree · ✏️batchReject · ✏️export · ✅lists · ✏️transfer |

图例：✅ 探测通过 · ⚙️ 需参数 · ✏️ 写操作（未探测） · ❓ 其他

## 全部路径（可按 Ctrl+F 搜索）

```
/admin/Advert/add
/admin/Advert/config
/admin/Advert/del
/admin/Advert/detail
/admin/Advert/disable
/admin/Advert/edit
/admin/Advert/lists
/admin/AfterSale/handle
/admin/AfterSale/lists
/admin/AfterSale/refund
/admin/AfterSale/reject
/admin/Cps/add
/admin/Cps/config
/admin/Cps/del
/admin/Cps/detail
/admin/Cps/disable
/admin/Cps/edit
/admin/Cps/lists
/admin/Cps/type_list
/admin/FinanceAccount/cashexport
/admin/FinanceAccount/cashlog
/admin/FinanceAccount/export
/admin/FinanceAccount/flow
/admin/FreeQueue/cancel
/admin/FreeQueue/config
/admin/FreeQueue/lists
/admin/FreeQueueTwo/cancel
/admin/FreeQueueTwo/config
/admin/FreeQueueTwo/lists
/admin/FreeQueueTwo/logLists
/admin/FreeQueueTwo/poolLists
/admin/GasStation/lists
/admin/GasStation/redReceiveList
/admin/GasStation/redReceiveLog
/admin/GasStation/setConfig
/admin/Life/config
/admin/Life/lists
/admin/LimitWithdraw/config
/admin/LimitWithdraw/lists
/admin/Login/adminLogin
/admin/Login/autoLoginByAccount
/admin/Login/captcha
/admin/Login/getAccountsByPhone
/admin/Login/yinfa
/admin/Movie/SupplyBalance
/admin/Movie/config
/admin/Movie/lists
/admin/OrderReview/check
/admin/OrderReview/lists
/admin/PK/config
/admin/PK/lists
/admin/Scanorder/lists
/admin/Statistics/teamPerformance
/admin/Statistics/userPerformance
/admin/VideoSign/config
/admin/VideoSign/lists
/admin/Virtual/config
/admin/Virtual/lists
/admin/activity/add
/admin/activity/detail
/admin/activity/disable
/admin/activity/edit
/admin/activity/lists
/admin/addon/detail
/admin/addon/install
/admin/addon/lists
/admin/addon/payinfo
/admin/addon/upgrade
/admin/admin/add
/admin/admin/changeNicknamePhone
/admin/admin/changePassword
/admin/admin/del
/admin/admin/detail
/admin/admin/disable
/admin/admin/edit
/admin/admin/getTicket
/admin/admin/lists
/admin/admin/menu
/admin/admin/rules
/admin/admin/setDefaultPassword
/admin/admin/setPayPassword
/admin/admin/yinfa
/admin/agent/add
/admin/agent/check
/admin/agent/config
/admin/agent/del
/admin/agent/detail
/admin/agent/disable
/admin/agent/edit
/admin/agent/getAgentApplyUsers
/admin/agent/lists
/admin/ancestralhall/add
/admin/ancestralhall/disable
/admin/ancestralhall/edit
/admin/ancestralhall/getConfig
/admin/ancestralhall/lists
/admin/ancestralhall/rank
/admin/ancestralhall/setConfig
/admin/article/articleAdd
/admin/article/articleDel
/admin/article/articleDetail
/admin/article/articleDisable
/admin/article/articleEdit
/admin/article/articleLists
/admin/article/cateAdd
/admin/article/cateDel
/admin/article/cateDisable
/admin/article/cateEdit
/admin/article/cateLists
/admin/article/config
/admin/bonus/config
/admin/bonus/lists
/admin/bonus/logs
/admin/card/add
/admin/card/cardQrcodeExport
/admin/card/config
/admin/card/del
/admin/card/detail
/admin/card/disable
/admin/card/distribute
/admin/card/edit
/admin/card/export
/admin/card/freeze
/admin/card/getUserIdsByCardId
/admin/card/lists
/admin/card/logs
/admin/card/ppt
/admin/card/qrcodeDisable
/admin/card/qrcodeRechargeList
/admin/card/qrcodeSet
/admin/card/qrcodeSetList
/admin/card/unfreeze
/admin/card/usage
/admin/catalogue/config
/admin/catalogue/del
/admin/catalogue/lists
/admin/catalogue/pptDel
/admin/catalogue/pptLists
/admin/catalogue/templateAdd
/admin/catalogue/templateDel
/admin/catalogue/templateDetail
/admin/catalogue/templateEdit
/admin/catalogue/templateLists
/admin/contribution/getConfig
/admin/contribution/lists
/admin/contribution/setConfig
/admin/copartner/add
/admin/copartner/check
/admin/copartner/disable
/admin/copartner/edit
/admin/copartner/getConfig
/admin/copartner/lists
/admin/copartner/setConfig
/admin/coupon/add
/admin/coupon/couponUser
/admin/coupon/detail
/admin/coupon/disable
/admin/coupon/edit
/admin/coupon/lists
/admin/crowner/check
/admin/crowner/config
/admin/crowner/del
/admin/crowner/detail
/admin/crowner/edit
/admin/crowner/lists
/admin/digital/getConfig
/admin/digital/logLists
/admin/digital/setConfig
/admin/financeAccount/add
/admin/financeAccount/del
/admin/financeAccount/detail
/admin/financeAccount/disable
/admin/financeAccount/edit
/admin/financeAccount/lists
/admin/freight/add
/admin/freight/del
/admin/freight/detail
/admin/freight/disable
/admin/freight/edit
/admin/freight/lists
/admin/giftbag/add
/admin/giftbag/disable
/admin/giftbag/edit
/admin/giftbag/lists
/admin/giftbag/logs
/admin/good/add
/admin/good/asyncLife
/admin/good/asyncSupply
/admin/good/asyncUpstream
/admin/good/asyncVirtual
/admin/good/batchFakeSale
/admin/good/changePrice
/admin/good/changeProfit
/admin/good/changeSkuState
/admin/good/changeStock
/admin/good/check
/admin/good/commend
/admin/good/del
/admin/good/detail
/admin/good/discount
/admin/good/edit
/admin/good/export
/admin/good/import
/admin/good/lists
/admin/good/paysetting
/admin/good/reward
/admin/good/setStockwarn
/admin/good/skuLists
/admin/good/sort
/admin/good/state
/admin/goodsCate/add
/admin/goodsCate/del
/admin/goodsCate/delSupplyCateMap
/admin/goodsCate/detail
/admin/goodsCate/disable
/admin/goodsCate/edit
/admin/goodsCate/getAllTags
/admin/goodsCate/lists
/admin/goodsCate/mallCateTree
/admin/goodsCate/setSupplyCateMap
/admin/goodsCate/supplyCateMap
/admin/goodsCate/supplyCates
/admin/goodsCate/tree
/admin/goodsCate/virtualCateTree
/admin/hotel/SupplyBalance
/admin/hotel/getConfig
/admin/hotel/lists
/admin/hotel/setConfig
/admin/increaccount/getConfig
/admin/increaccount/setConfig
/admin/index/addons
/admin/index/express
/admin/index/financeStatic
/admin/index/getRegions
/admin/index/index
/admin/index/logs
/admin/index/mallStatic
/admin/index/message
/admin/index/orderStatic
/admin/index/screen
/admin/index/shopOrderStatic
/admin/index/taskCancel
/admin/index/tasks
/admin/index/uploadFile
/admin/index/uploadImg
/admin/live/getLink
/admin/login/lpy_register
/admin/login/lpy_send
/admin/login/reset
/admin/login/sms
/admin/mall/add
/admin/mall/del
/admin/mall/detail
/admin/mall/disable
/admin/mall/edit
/admin/mall/lists
/admin/mall/pageDetail
/admin/order/cancel
/admin/order/detail
/admin/order/export
/admin/order/leaseUpdate
/admin/order/listCount
/admin/order/lists
/admin/order/logistics
/admin/order/notice
/admin/order/print
/admin/order/purchaseSend
/admin/order/send
/admin/order/writeoff
/admin/order/yinfa
/admin/order/yinfaExport
/admin/page/add
/admin/page/del
/admin/page/disable
/admin/page/edit
/admin/page/lists
/admin/partner/add
/admin/partner/check
/admin/partner/disable
/admin/partner/edit
/admin/partner/getConfig
/admin/partner/lists
/admin/partner/setConfig
/admin/pointrefund/getConfig
/admin/pointrefund/logList
/admin/pointrefund/refundList
/admin/pointrefund/setConfig
/admin/poollottery/getConfig
/admin/poollottery/pools
/admin/poollottery/setConfig
/admin/poollottery/users
/admin/push31/getConfig
/admin/push31/lists
/admin/push31/parentlogs
/admin/push31/setConfig
/admin/pvbv/changeParent
/admin/pvbv/cultivatePerform
/admin/pvbv/cultivateStats
/admin/pvbv/performLists
/admin/pvbv/performLog
/admin/pvbv/placeLists
/admin/qht/circulateList
/admin/qht/config
/admin/qht/tradeList
/admin/realname/check
/admin/realname/config
/admin/realname/lists
/admin/reduce/add
/admin/reduce/del
/admin/reduce/detail
/admin/reduce/disable
/admin/reduce/edit
/admin/reduce/lists
/admin/rewardInvite/add
/admin/rewardInvite/del
/admin/rewardInvite/detail
/admin/rewardInvite/disable
/admin/rewardInvite/edit
/admin/rewardInvite/lists
/admin/rewardOrder/add
/admin/rewardOrder/del
/admin/rewardOrder/detail
/admin/rewardOrder/disable
/admin/rewardOrder/edit
/admin/rewardOrder/lists
/admin/rewardPlat/add
/admin/rewardPlat/del
/admin/rewardPlat/detail
/admin/rewardPlat/disable
/admin/rewardPlat/edit
/admin/rewardPlat/lists
/admin/rewardProfile/getConfig
/admin/rewardProfile/setConfig
/admin/role/add
/admin/role/detail
/admin/role/edit
/admin/role/groups
/admin/role/rules
/admin/salesroom/add
/admin/salesroom/del
/admin/salesroom/detail
/admin/salesroom/disable
/admin/salesroom/edit
/admin/salesroom/lists
/admin/setting/alone
/admin/setting/baseinfo
/admin/setting/docs
/admin/setting/entry
/admin/setting/fieldDel
/admin/setting/fieldEdit
/admin/setting/fieldList
/admin/setting/fourth
/admin/setting/getSmbaoLeft
/admin/setting/kuaidi
/admin/setting/kuaidiSenderAdd
/admin/setting/kuaidiSenderDel
/admin/setting/kuaidiSenderEdit
/admin/setting/kuaidiSenderList
/admin/setting/kuaidiSenderState
/admin/setting/kuaidiTemplateAdd
/admin/setting/kuaidiTemplateDel
/admin/setting/kuaidiTemplateEdit
/admin/setting/kuaidiTemplateList
/admin/setting/kuaidiTemplateState
/admin/setting/live
/admin/setting/pagestyle
/admin/setting/pay
/admin/setting/pvbv
/admin/setting/send
/admin/setting/subaccount
/admin/setting/supply
/admin/setting/third
/admin/signin/config
/admin/signin/lists
/admin/ssg/config
/admin/ssg/detail
/admin/ssg/lists
/admin/statistics/conversion
/admin/statistics/financeDay
/admin/statistics/goodsCateSell
/admin/statistics/goodsSell
/admin/statistics/grossProfit
/admin/statistics/orderGoodsStats
/admin/statistics/orderStat
/admin/statistics/orderStatExport
/admin/statistics/sourceFinance
/admin/statistics/survey
/admin/store/add
/admin/store/check
/admin/store/config
/admin/store/del
/admin/store/detail
/admin/store/disable
/admin/store/edit
/admin/store/lists
/admin/system/address
/admin/system/articles
/admin/system/functions
/admin/tabbar/add
/admin/tabbar/del
/admin/tabbar/detail
/admin/tabbar/disable
/admin/tabbar/edit
/admin/tabbar/lists
/admin/trade/config
/admin/trade/lists
/admin/tsg/config
/admin/tsg/detail
/admin/tsg/lists
/admin/tsg/structure
/admin/tuan/cancel
/admin/tuan/choose
/admin/tuan/choosedel
/admin/tuan/config
/admin/tuan/goodDesc
/admin/tuan/goods
/admin/tuan/lists
/admin/user/changAccount
/admin/user/changLevel
/admin/user/customize
/admin/user/del
/admin/user/disable
/admin/user/export
/admin/user/import
/admin/user/lists
/admin/user/logLists
/admin/user/resetPassword
/admin/userFinance/add
/admin/userFinance/commission
/admin/userFinance/del
/admin/userFinance/detail
/admin/userFinance/disable
/admin/userFinance/edit
/admin/userFinance/export
/admin/userFinance/flow
/admin/userFinance/lists
/admin/userLevel/add
/admin/userLevel/del
/admin/userLevel/detail
/admin/userLevel/disable
/admin/userLevel/edit
/admin/userLevel/lists
/admin/water/package
/admin/withdraw/batchAgree
/admin/withdraw/batchReject
/admin/withdraw/export
/admin/withdraw/lists
/admin/withdraw/transfer
```