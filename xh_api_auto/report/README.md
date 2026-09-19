# Allure 报告目录

本目录用于存放 Allure 报告相关产物：

- `allure-results/`：运行 `pytest` 后生成的原始 Allure 结果文件（由 `--alluredir` 参数指定）。
- `allure-report/`：执行 `allure generate` 后生成的可直接在浏览器打开的 HTML 报告目录。
- `logs/`：每次运行生成的 `.log` 日志文件。
- `screenshots/`（可选）：其他附件或截图。

## 生成 Allure HTML 报告

```cmd
REM 1. 先安装 Allure 命令行（需先安装 JDK 8+，或下载 Allure zip 并将 bin 加入 PATH）
REM    下载地址: https://github.com/allure-framework/allure2/releases

REM 2. 运行用例（会自动输出到 report/allure-results）
pytest

REM 3. 生成 HTML 报告
allure generate report/allure-results -o report/allure-report --clean

REM 4. 本地打开预览（会启动一个本地 HTTP 服务）
allure open report/allure-report
```

## 目录说明
```
report/
├── allure-results/   ← pytest + allure-pytest 输出
├── allure-report/    ← allure generate 生成的最终报告
├── logs/             ← 运行日志
└── screenshots/      ← 其他附件
```
