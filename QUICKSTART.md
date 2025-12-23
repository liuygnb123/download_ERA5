# 快速开始指南

5分钟快速上手 ERA5-Land 数据下载工具。

## 🚀 三步开始

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 配置 CDS API

运行配置助手：
```bash
python setup_cdsapi.py
```

按提示输入您的 CDS API UID 和 Key（从 https://cds.climate.copernicus.eu/api-how-to 获取）。

### 步骤 3: 运行示例

```bash
python quick_start_example.py
```

选择示例1，开始下载！

---

## 📝 最简单的代码示例

```python
from download_ERA5_Land import ERA5LandDownloader

# 创建下载器
downloader = ERA5LandDownloader(output_dir='./my_data')

# 下载数据
files = downloader.download(
    variables=['2m_temperature'],           # 2米温度
    start_date='2014-01-01',                # 开始日期
    end_date='2014-01-31',                  # 结束日期
    area=[60, 70, 10, 140]                  # [北, 西, 南, 东]
)

print(f"✅ 成功下载 {len(files)} 个文件")
```

---

## 🎯 常用场景

### 场景1: 下载中国区域数据

```python
downloader = ERA5LandDownloader(output_dir='./data/china')

files = downloader.download(
    variables=['2m_temperature', 'total_precipitation'],
    start_date='2020-01-01',
    end_date='2020-12-31',
    area=[60, 70, 10, 140],  # 中国区域
    split_by='month'
)
```

### 场景2: 下载特定小时数据

```python
files = downloader.download(
    variables=['surface_solar_radiation_downwards'],
    start_date='2020-01-01',
    end_date='2020-01-31',
    area=[40, 100, 30, 120],
    time_hours=['00:00', '06:00', '12:00', '18:00']  # 每6小时
)
```

### 场景3: 下载并合并文件

```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2020-01-01',
    end_date='2020-03-31',
    split_by='month',
    merge_files=True,                        # 合并文件
    final_output_name='ERA5_2020_Q1.nc'
)
```

---

## 📊 查看结果

### 下载的文件

```
./my_data/
├── ERA5_Land_2m_temperature_202001.nc
├── ERA5_Land_2m_temperature_202002.nc
└── logs/
    ├── download_status.json      # 下载状态
    └── verification_log.txt      # 验证日志
```

### 查看验证日志

```bash
# Windows
notepad my_data\logs\verification_log.txt

# Linux/Mac
cat my_data/logs/verification_log.txt
```

---

## 🔍 数据验证

每个文件会自动验证：
- ✅ 变量是否存在
- ✅ 时间范围是否正确
- ✅ 空间范围是否正确
- ✅ 数据是否完整

验证结果保存在 `logs/verification_log.txt`。

---

## ❓ 遇到问题？

### 问题1: pip install 失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: CDS API 配置错误

检查 `~/.cdsapirc` 文件（Windows: `C:\Users\<用户名>\.cdsapirc`）：
```
url: https://cds.climate.copernicus.eu/api/v2
key: <你的UID>:<你的API-Key>
```

### 问题3: 下载失败

1. 检查网络连接
2. 查看错误日志：`logs/verification_log.txt`
3. 重试失败的下载：
```python
downloader.retry_failed_downloads()
```

---

## 📚 更多信息

- 完整文档：`README.md`
- 示例代码：`quick_start_example.py`
- 配置文件示例：`download_config.json`

---

**祝您使用愉快！** 🎉

