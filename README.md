# Soulmask NPC 天赋 OCR 助手

> 悬停 NPC 弹出天赋面板 → 快捷键扫描 → OCR 识别 → 语音播报

---

## 常用命令

### 一键启动（推荐）

双击 `启动.bat`，首次自动装环境，之后秒开。

### 手动启动（CMD）

```cmd
D:
cd D:\path\to\soulmask_ocr
venv\Scripts\activate
python main.py
```

### 从 GitHub 下载

```cmd
git clone git@github.com:zsca848081006-del/soulmask_ocr.git
cd soulmask_ocr
双击 启动.bat
```

### 更新到最新版

```cmd
cd soulmask_ocr
git pull
双击 启动.bat
```

---

## 快捷键

| 热键 | 功能 |
|------|------|
| `Ctrl+Shift+Q` | **监视扫描** —— 比对 watchlist，命中才播报 |
| `Ctrl+Shift+F` | **全量查询** —— 全部天赋效果语音播报 |
| `Ctrl+Shift+R` | **热重载** —— 重新加载 config.json 和 watchlist.json |
| `Ctrl+Shift+E` | **退出** |

---

## 控制台输出说明

| 标签 | 含义 |
|------|------|
| `[=]` | 精确匹配 |
| `[~85%]` | 模糊匹配，相似度 85% |
| `[Lv1]` / `[Lv2]` / `[Lv3]` | 等级检测结果 |
| `[--]` | 未检出等级，自动取最高级 |

示例：
```
[20:15:32] [FULL] 扫描中...
  [=] [Lv3] 步伐迅捷: 移动速度提升9%
  [=] [--] 渴望鲜血: 对鲜血无尽渴求，攻击5米内的目标时自...
  共匹配 8 个天赋
```

---

## 当前功能（v1.1）

| 功能 | 说明 |
|------|------|
| **ROI 截图** | mss 库截屏，2K 分辨率下截取左侧 1/3 屏幕 |
| **OCR 识别** | RapidOCR onnx 引擎，OTSU 二值化 + 2x 超分预处理 |
| **天赋库** | 560 个天赋 × 1310 条等级数据，rapidfuzz 模糊匹配 |
| **等级检测** | 白线垂直投影计数，自动识别 I / II / III 级 |
| **分级播报** | OCR 名称 + 等级 → 精确匹配对应等级的技能效果 |
| **监视清单** | 编辑 `data/watchlist.json` 指定盯梢天赋，命中才语音提醒 |
| **语音播报** | pyttsx3 本地 TTS，队列消费模式，不阻塞扫描 |
| **扫描日志** | 每次扫描写入 `logs/session_日期.jsonl`，可追溯 |
| **热重载** | 改配置不用重启 |

---

## 配置说明

### `data/config.json`

```json
{
  "roi": { "x": 0, "y": 0, "width": 853, "height": 1440 },
  "layout": {
    "row_height": 68,
    "icon_x": 28,
    "icon_width": 72,
    "text_x": 100,
    "level_line_y_offset": 40,
    "level_window_height": 20,
    "level_white_threshold": 220
  },
  "fuzzy_match": { "min_score": 75 }
}
```

| 参数 | 作用 | 调参建议 |
|------|------|---------|
| `roi` | 截图区域 | 面板在屏幕左边就不用动 |
| `row_height` | 每行天赋高度 | 游戏 UI 没改就不用动 |
| `level_white_threshold` | 白线判定阈值 | 等级检测不准可降低到 200 |
| `min_score` | 模糊匹配灵敏度 | 匹配太严格可降到 60 |

### `data/watchlist.json`

```json
{
  "active": ["渴望鲜血", "步伐迅捷", "攻势凌厉"]
}
```

直接编辑天赋名，保存后 `Ctrl+Shift+R` 热重载。

---

## 目录结构

```
soulmask_ocr/
├── main.py              # 主入口
├── config.py            # 配置读写
├── capture.py           # 截图
├── ocr_engine.py        # OCR 引擎
├── talent_db.py         # 天赋库查询
├── watchlist.py         # 监视清单
├── detect_icons.py      # 行切分
├── detect_level.py      # 等级检测
├── parse_csv.py         # CSV 解析（开发用）
├── output/tts.py        # 语音播报
├── 启动.bat             # Windows 一键启动
├── data/
│   ├── talents.json     # 天赋数据
│   ├── config.json      # 全局配置
│   └── watchlist.json   # 监视清单
└── logs/                # 扫描日志
```
