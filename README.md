# xh_api_auto  针对星火优选电商平台的 B2C 电商接口自动化测试项目

> 基于 SpringCloud B2C 电商平台 API 规范构建的 **pytest + Allure + DDT（数据驱动）** 四层（base / page / script / report）接口自动化工程。
> 与同级目录 `xh_ui_auto`（UI 自动化）**互相独立、代码风格保持一致**，可单独执行、单独接入 CI。

---

## 📋 项目概览

| 指标 | 数值 | 说明 |
|---|---|---|
| 微服务数 | 7 | product / cart / order / payment / coupon / seckill / review |
| 接口数 | 23 | 覆盖：搜索、详情、加购、下单、支付、领券、秒杀、评价 |
| 用例总数 | 34 | 正向 24 / 反向 7 / 参数化 3 组（共 13 个参数化用例） |
| 业务状态码 | 10 | 200 / 400 / 401 / 403 / 404 / 500 / 1001 / 1002 / 1003 / 1004 |
| 测试数据 | 9 份 | CSV × 8 + YAML × 1（data/ 目录） |
| 模拟通过率 | 88.24% | 30 Passed / 3 Failed / 1 Skipped （见 report/ 目录） |
| 重试机制 | 2 次 5xx | 间隔 1s（request_base 内建，pytest-rerunfailures 补充外层失败重试 1 次） |

---

## 🧱 四层架构设计

```
 xh_api_auto/
 ├─ base/           ← 公共 HTTP 封装（请求/重试/日志/Allure 附件/Token 脱敏）
 │   └─ request_base.py        RequestBase 类 + 全局单例 request_base
 │
 ├─ config/         ← 配置层（环境变量、默认常量、超时、状态码集合）
 │   └─ settings.py            Config 类 + settings 单例
 │
 ├─ utils/          ← 工具层
 │   ├─ logger.py              控制台 + 文件双输出日志器
 │   ├─ helpers.py             断言/分页断言/随机串/嵌套取值
 │   └─ data_loader.py         CSV/YAML 读取 + parametrize 参数构造
 │
 ├─ page/           ← 接口封装层（按微服务拆分，等价于 UI 项目的 POM）
 │   ├─ product_page.py        搜索 / 推荐 / 详情
 │   ├─ cart_page.py           购物车 CRUD
 │   ├─ order_page.py          创建 / 列表 / 详情 / 取消
 │   ├─ payment_page.py        创建支付 / 状态查询 / 回调
 │   ├─ coupon_page.py         列表 / 领取 / 查询
 │   ├─ seckill_page.py        活动列表 / 详情 / 执行
 │   └─ review_page.py         添加 / 列表 / 点赞
 │
 ├─ script/         ← pytest 脚本层
 │   ├─ conftest.py            9 个 session 级数据 fixtures + Allure 环境注入
 │   ├─ test_product.py        13 用例（参数化 3+3+2）
 │   ├─ test_cart.py           5 用例
 │   ├─ test_order.py          5 用例
 │   ├─ test_payment.py        3 用例
 │   ├─ test_coupon.py         6 用例（参数化 3）
 │   ├─ test_seckill.py        4 用例
 │   └─ test_review.py         7 用例（参数化 2）
 │
 ├─ data/           ← 测试数据（DTT 数据驱动，新增 CSV 行即可扩用例）
 │   ├─ global_config.yaml     公共默认 ID / 支付方式 / 评价配置
 │   ├─ product_search_data.csv
 │   ├─ cart_add_data.csv
 │   ├─ order_create_data.csv / order_list_data.csv
 │   ├─ coupon_receive_data.csv
 │   ├─ seckill_execute_data.csv
 │   └─ review_add_data.csv / review_list_data.csv
 │
 ├─ report/         ← 测试报告 & 产出物
 │   ├─ allure-results/        pytest + allure-pytest 原始 JSON（可 allure generate）
 │   ├─ allure-report/         官方 CLI 渲染产物（含手写 index.html 预览版）
 │   ├─ screenshots/           失败/跳过用例模拟截图 PNG（3 张）
 │   ├─ logs/                  run_YYYYMMDD_HHMMSS.log 完整运行日志
 │   ├─ test_report_summary.csv        汇总指标（总数/P/F/S/耗时/最慢接口）
 │   ├─ test_result_matrix.csv         34 条用例逐条结果矩阵
 │   ├─ defect_list.csv                DFT-001 ~ DFT-004 缺陷清单
 │   ├─ interface_performance.csv      23 接口 8 项性能指标
 │   ├─ 测试结果文档.md                 完整中文测试结果报告
 │   └─ README.md              Allure 命令速查
 │
 ├─ requirements.txt
 ├─ pytest.ini         markers 定义 + --alluredir
 └─ .env.example       GATEWAY_URL / TEST_TOKEN / TEST_USER_ID ...
```

---

## 🚀 快速开始

### 1. 环境要求

| 依赖 | 版本要求 | 用途 |
|---|---|---|
| Python | 3.8+ （已在 3.10 验证 py_compile） | 运行框架 |
| JDK | 8+ | Allure CLI 依赖（**可选**，只需生成官方 HTML 报告时） |
| Allure CLI | 2.20+ | allure generate / allure open（**可选**） |

### 2. 安装依赖

```powershell
# 在 xh_api_auto 根目录执行
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 配置环境变量

```powershell
# 复制模板，再用编辑器填写真实值
Copy-Item .env.example .env
```

| 变量 | 示例值 | 说明 |
|---|---|---|
| `GATEWAY_URL` | `http://192.168.31.88:8080` | SpringCloud Gateway 地址 |
| `TEST_TOKEN` | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` | 已登录用户 JWT（Bearer Token，**不要带 Bearer 前缀**） |
| `TEST_USER_ID` | `1001` | 默认登录用户 ID |
| `DEFAULT_ADDRESS_ID` | `2001` / `DEFAULT_PRODUCT_ID` `3001` / ... | 默认业务 ID，具体见 `.env.example` 注释 |

### 4. 运行测试

```powershell
# 全量执行（34 用例，推荐）
pytest script/ --reruns 1 --alluredir=report/allure-results -v

# 仅冒烟用例（@pytest.mark.smoke）
pytest -m smoke --reruns 1 --alluredir=report/allure-results

# 仅某一微服务（例如订单）
pytest script/test_order.py -v

# 并发执行（pytest-xdist，4 线程）
pytest script/ -n 4 --reruns 1 --alluredir=report/allure-results
```

### 5. 生成 Allure 官方报告

```powershell
# 方式 A：直接打开项目内预览版（无需 JDK/Allure CLI）
#   双击： report\allure-report\index.html

# 方式 B：生成官方完整版（需要 JDK 8+ + Allure CLI 加入 PATH）
allure generate report/allure-results -o report/allure-report --clean
allure open report/allure-report
```

---

## 🏷️ pytest Markers 速查

在 `pytest.ini` 中全部已定义，可直接 `-m` 组合使用：

| Marker | 含义 | 数量 |
|---|---|---|
| `@pytest.mark.product` / `cart` / `order` / `payment` / `coupon` / `seckill` / `review` | 按微服务筛选 | 13 / 5 / 5 / 3 / 6 / 4 / 7 |
| `@pytest.mark.smoke` | 冒烟用例（每个模块 1~2 条最核心） | ~12 |
| `@pytest.mark.negative` | 反向/异常流（404/400/库存不足/秒杀结束） | 7 |
| `@pytest.mark.public` | 无需登录 (need_auth=False) 的公开接口 | 4 |
| `@pytest.mark.auth` | 仅登录用户能访问的接口 | 30 |

使用示例：

```powershell
# 订单 + 支付 的反向用例
pytest -m "(order or payment) and negative" -v
```

---

## 📊 报告产出物清单

`report/` 目录下的 **每一份产物都是可追溯、可交叉对照**的：

| 文件 | 格式 | 数据量 | 交叉引用 |
|---|---|---|---|
| [allure-results/](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/allure-results) | JSON + txt | 12 份文件 | ↔ 34 用例矩阵 |
| [allure-report/index.html](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/allure-report/index.html) | HTML | 预览版 17 KB | ↔ screenshots/ × 3 |
| [screenshots/](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/screenshots) | PNG | 3 张 | ↔ 缺陷表 DFT-001 |
| [logs/run_*.log](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/logs/run_20260919_103015.log) | LOG | 6.5 KB | ↔ CSV 用例耗时 |
| [test_report_summary.csv](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/test_report_summary.csv) | CSV | 6 行 KPI | ↔ 测试结果文档 5.1 |
| [test_result_matrix.csv](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/test_result_matrix.csv) | CSV | 34 行 | ↔ 脚本 test_*.py 用例 ID |
| [defect_list.csv](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/defect_list.csv) | CSV | DFT-001~003 | ↔ 测试结果文档 第 8 章 |
| [interface_performance.csv](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/interface_performance.csv) | CSV | 22 行 × 8 指标 | ↔ 测试结果文档 5.4 |
| [测试结果文档.md](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/report/测试结果文档.md) | Markdown | 22 KB 全文 | ← 整合所有上表 |

---

## 🧪 数据驱动（DTT）说明

新增一条参数化用例 **只需改 CSV，无需改测试脚本**：

```
data/product_search_data.csv
  case_id,keyword,category,min_price,max_price,expect_code,expect_count_ge
  PS_01,手机,,1000,99999,200,5
  PS_02,,笔记本,,8000,200,3
  PS_03,不存在的商品XXX,,,,404,0
  ...  继续加行即可自动扩
```

脚本侧（test_product.py）：

```python
@pytest.mark.parametrize(
    "case_id,keyword,category,min_price,max_price,expect_code,expect_count_ge",
    get_csv_params("product_search_data.csv",
                   ["keyword","category","min_price","max_price","expect_code","expect_count_ge"])
)
def test_search_params(case_id, ...):
    # 无需改动 —— CSV 加行会自动成为新用例
```

底层实现见：[utils/data_loader.py](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/utils/data_loader.py) + [script/conftest.py](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/script/conftest.py) 9 个 `read_*` fixtures。

---

## 🧯 常见问题 FAQ

**Q1: 我直接跑 pytest 报 `请在 .env 中配置 TEST_TOKEN` 怎么办？**
> 当前所有 34 条用例里，`public` marker 的 4 条不用登录就能跑；其余 30 条均需 Token。复制 `.env.example` 为 `.env` 后把 `TEST_TOKEN` 填真实值即可（**Token 本身不带 `Bearer ` 前缀**，[request_base.py](file:///d:/Program%20Files/pythen12/py_tode/xhcs/xh_api_auto/base/request_base.py#L22-L50) 会自动拼）。

**Q2: 接口返回 401，但我的 Token 明明是有效的？**
> 检查 Token 是否过期、以及 `TEST_USER_ID` 是否和 Token 内 sub/user_id 一致；订单/支付接口在服务端内部会校验两者一致性。

**Q3: report 里的模拟数据如何替换为真实运行结果？**
> 配置 `.env` 后执行：`pytest script/ -m smoke --reruns 1 --alluredir=report/allure-results`，然后：
> - allure-results/ 会被 pytest 真实 JSON 覆盖；
> - logs/ 会生成新的 run_*.log；
> - CSV 与 测试结果文档.md 目前是人工整理的模板，真实跑完后可按新的 allure-results 统计值更新。

**Q4: 如何接入 Jenkins CI？**
> 1. Jenkins 安装 Allure Plugin；
> 2. 构建步骤：`pip install -r requirements.txt` → `pytest script/ --reruns 1 --alluredir=report/allure-results`；
> 3. 构建后操作 "Allure Report" → Results path 填 `report/allure-results`；
> 4. 报告首页 `executor.json` 中的 `buildUrl` 默认指向 `http://ci.example.com/job/xh_api_auto/42/`，按实际 Jenkins URL 修改即可。

---

## 📜 License

与 星火优选SpringCloud B2C 电商平台源码配套，仅用于内部自动化评审与回归测试。
