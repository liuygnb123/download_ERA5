# ERA5-Land 数据自动下载工具

一个功能完整、易于使用的 ERA5-Land 小时数据自动下载工具，支持自定义时间范围、空间范围、变量选择，并提供完整的数据验证功能。

## 📋 目录

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [安装配置](#安装配置)
- [使用方法](#使用方法)
- [数据验证](#数据验证)
- [高级功能](#高级功能)
- [常见问题](#常见问题)
- [文件说明](#文件说明)

---

## ✨ 功能特点

### 核心功能
- ✅ **自动下载**: 自动从 Copernicus Climate Data Store (CDS) 下载 ERA5-Land 数据
- ✅ **灵活配置**: 支持自定义变量、时间范围、经纬度范围、保存位置
- ✅ **并行加速**: 支持多线程并行下载，大幅提升下载速度
- ✅ **智能重试**: 下载失败时自动重试，可配置重试次数和延迟
- ✅ **断点续传**: 记录下载状态，已下载的文件不会重复下载
- ✅ **进度显示**: 实时显示下载进度和状态

### 数据验证
- ✅ **变量验证**: 检查所有请求的变量是否存在且数据完整
- ✅ **时间验证**: 验证年份、月份和时间步数是否正确
- ✅ **空间验证**: 验证纬度、经度范围是否匹配
- ✅ **自动日志**: 所有验证结果自动记录到日志文件

### 便捷功能
- ✅ **ZIP自动解压**: 自动检测并解压CDS返回的ZIP文件
- ✅ **变量名映射**: 自动处理CDS API变量名与NetCDF变量名的映射
- ✅ **文件合并**: 可选择将多个文件合并为单个NetCDF文件
- ✅ **错误处理**: 完善的异常处理机制，提供详细的错误日志

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install cdsapi xarray netCDF4 pandas tqdm
```

### 2. 配置 CDS API

#### 步骤 1: 注册账号
访问 [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) 并注册账号。

#### 步骤 2: 获取 API Key
登录后访问 [API Key 页面](https://cds.climate.copernicus.eu/api-how-to)，复制您的 UID 和 API Key。

#### 步骤 3: 创建配置文件

**Windows 系统**:  
在 `C:\Users\<你的用户名>\.cdsapirc` 创建文件（注意没有扩展名）

**Linux/Mac 系统**:  
在 `~/.cdsapirc` 创建文件

文件内容：
```
url: https://cds.climate.copernicus.eu/api/v2
key: <你的UID>:<你的API-Key>
```

**快速配置**（可选）:
```bash
python setup_cdsapi.py
```

### 3. 运行示例

```bash
python quick_start_example.py
```

选择示例1，下载中国区域2014年1月的温度和太阳辐射数据。

---

## 📖 使用方法

### 基本用法

```python
from download_ERA5_Land import ERA5LandDownloader

# 创建下载器
downloader = ERA5LandDownloader(
    output_dir='./data',      # 输出目录
    max_workers=3,            # 并行线程数
    retry_times=3,            # 重试次数
    retry_delay=10            # 重试延迟（秒）
)

# 下载数据
files = downloader.download(
    variables=['2m_temperature', 'surface_solar_radiation_downwards'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=[60, 70, 10, 140],   # [北, 西, 南, 东]
    time_hours=None,          # None表示所有24小时
    split_by='month'          # 按月分割
)

print(f"成功下载 {len(files)} 个文件")
```

### 参数说明

#### ERA5LandDownloader 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | str | `'./ERA5_Land_data'` | 输出目录 |
| `max_workers` | int | `4` | 并行下载线程数 |
| `retry_times` | int | `3` | 失败重试次数 |
| `retry_delay` | int | `10` | 重试延迟（秒） |
| `variable_mapping` | dict | `None` | 自定义变量名映射 |

#### download() 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `variables` | list | ✅ | 变量名列表 |
| `start_date` | str | ✅ | 开始日期 'YYYY-MM-DD' |
| `end_date` | str | ✅ | 结束日期 'YYYY-MM-DD' |
| `area` | list | ❌ | 区域范围 [N, W, S, E] |
| `time_hours` | list | ❌ | 小时列表，None表示全部 |
| `split_by` | str | ❌ | 分割方式 'month'/'year' |
| `merge_files` | bool | ❌ | 是否合并文件 |
| `final_output_name` | str | ❌ | 合并后的文件名 |

### 常用变量名

| CDS API 变量名 | NetCDF 变量名 | 说明 |
|---------------|--------------|------|
| `2m_temperature` | `t2m` | 2米温度 |
| `2m_dewpoint_temperature` | `d2m` | 2米露点温度 |
| `surface_solar_radiation_downwards` | `ssrd` | 地表向下短波辐射 |
| `surface_thermal_radiation_downwards` | `strd` | 地表向下长波辐射 |
| `10m_u_component_of_wind` | `u10` | 10米U风速 |
| `10m_v_component_of_wind` | `v10` | 10米V风速 |
| `total_precipitation` | `tp` | 总降水量 |
| `surface_pressure` | `sp` | 地表气压 |

完整变量列表请参考 [CDS 文档](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)。

---

## 🔍 数据验证

### 自动验证

下载的每个文件都会自动进行全面验证，包括：

#### 1. 变量验证
- ✅ 检查所有请求的变量是否存在
- ✅ 自动处理变量名映射
- ✅ 验证变量数据非空

#### 2. 时间范围验证
- ✅ 验证年份是否正确（严格）
- ✅ 验证月份是否正确（严格）
- ⚠️ 检查时间步数是否合理（允许±10%误差）

#### 3. 空间范围验证
- ⚠️ 验证纬度范围（允许±0.5°误差）
- ⚠️ 验证经度范围（允许±0.5°误差）

#### 4. 数据完整性
- ✅ 统计有效数据点数量和比例

### 验证日志

所有验证结果自动记录到日志文件：
```
<output_dir>/logs/verification_log.txt
```

日志示例：
```
[2025-12-23 12:46:22] ℹ️ [INFO] 开始验证文件: ERA5_Land_xxx.nc
[2025-12-23 12:46:22] ✅ [SUCCESS] 文件打开成功
[2025-12-23 12:46:22] ℹ️ [INFO] 文件大小: 558.23 MB

[2025-12-23 12:46:22] ℹ️ [INFO] 【1/4】变量验证
[2025-12-23 12:46:22] ✅ [SUCCESS]   ✅ 变量存在: 2m_temperature (映射为 t2m)

[2025-12-23 12:46:22] ℹ️ [INFO] 【2/4】数据完整性验证
[2025-12-23 12:46:25] ✅ [SUCCESS]   ✅ 2m_temperature: 261,293,544 数据点, 189,179,112 有效 (72.4%)

[2025-12-23 12:46:28] ℹ️ [INFO] 【3/4】时间范围验证
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ 年份匹配: 2014
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ 月份匹配: 1

[2025-12-23 12:46:28] ℹ️ [INFO] 【4/4】空间范围验证
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ 纬度范围匹配 (误差 0.00°)

[2025-12-23 12:46:28] ✅ [SUCCESS] ✅ 文件验证通过！所有检查项均符合要求
```

### 查看验证日志

```bash
# Windows
notepad <output_dir>\logs\verification_log.txt

# Linux/Mac
cat <output_dir>/logs/verification_log.txt
```

---

## 🔧 高级功能

### 1. 使用配置文件

创建 `download_config.json`:
```json
{
  "output_dir": "./data/china_2014",
  "max_workers": 5,
  "retry_times": 3,
  "variables": ["2m_temperature", "total_precipitation"],
  "start_date": "2014-01-01",
  "end_date": "2014-12-31",
  "area": [60, 70, 10, 140],
  "split_by": "month"
}
```

运行：
```bash
python download_ERA5_Land_with_config.py download_config.json
```

### 2. 自定义变量名映射

如果遇到变量名不匹配的问题：

```python
custom_mapping = {
    'your_cds_variable_name': 'actual_netcdf_variable_name'
}

downloader = ERA5LandDownloader(
    variable_mapping=custom_mapping
)
```

### 3. 重试失败的下载

```python
downloader = ERA5LandDownloader(output_dir='./data')

# 重试所有失败的任务
downloaded_files = downloader.retry_failed_downloads()
```

### 4. 合并多个文件

```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-12-31',
    split_by='month',
    merge_files=True,
    final_output_name='ERA5_Land_2014.nc'
)
```

### 5. 下载管理

```bash
# 查看下载状态
python manage_downloads.py status

# 重试失败的下载
python manage_downloads.py retry

# 清理临时文件
python manage_downloads.py clean
```

---

## 📂 输出文件结构

```
<output_dir>/
├── logs/
│   ├── download_status.json      # 下载状态记录
│   └── verification_log.txt      # 验证日志
├── temp/                          # 临时文件目录
└── ERA5_Land_<变量>_<时间>.nc    # 下载的数据文件
```

### download_status.json

记录每个任务的下载状态：
```json
{
  "201401": {
    "status": "completed",
    "file": "ERA5_Land_xxx_201401.nc",
    "timestamp": "2025-12-23T12:00:00",
    "variables": ["2m_temperature"],
    "task": {...}
  }
}
```

---

## ❓ 常见问题

### Q1: 如何获取 CDS API Key？

**A**: 
1. 访问 https://cds.climate.copernicus.eu/
2. 注册并登录
3. 访问 https://cds.climate.copernicus.eu/api-how-to
4. 复制 UID 和 API Key

### Q2: 下载速度慢怎么办？

**A**: 
- 增加并行线程数：`max_workers=8`
- CDS服务器在欧洲，国内访问可能较慢
- 避免在高峰时段下载

### Q3: 出现 "文件验证失败" 错误？

**A**: 
1. 查看验证日志：`<output_dir>/logs/verification_log.txt`
2. 检查变量名是否正确
3. 如果是变量名映射问题，添加自定义映射
4. 如果是时间/空间范围问题，检查下载参数

### Q4: 如何下载全球数据？

**A**: 
将 `area` 参数设为 `None`:
```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=None  # 全球数据
)
```

### Q5: 可以下载特定小时的数据吗？

**A**: 
可以，使用 `time_hours` 参数：
```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    time_hours=['00:00', '06:00', '12:00', '18:00']  # 每6小时
)
```

### Q6: 下载的文件是ZIP格式怎么办？

**A**: 
工具会自动检测并解压ZIP文件，无需手动处理。

### Q7: 如何查看下载进度？

**A**: 
- 控制台会实时显示进度条
- 查看 `download_status.json` 了解详细状态
- 查看 `verification_log.txt` 了解验证结果

### Q8: 验证日志中的WARNING需要处理吗？

**A**: 
通常不需要。WARNING表示轻微偏差（如时间步数差异<10%，空间范围偏差<0.5°），不影响数据使用。

---

## 📁 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `download_ERA5_Land.py` | 核心下载模块 |
| `quick_start_example.py` | 快速开始示例 |
| `download_ERA5_Land_with_config.py` | 配置文件下载 |
| `manage_downloads.py` | 下载管理工具 |
| `setup_cdsapi.py` | CDS API 配置助手 |
| `requirements.txt` | Python依赖列表 |
| `README.md` | 本文档 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `download_config.json` | 下载配置示例 |
| `~/.cdsapirc` | CDS API 配置文件 |

### 输出文件

| 文件/目录 | 说明 |
|----------|------|
| `<output_dir>/logs/download_status.json` | 下载状态 |
| `<output_dir>/logs/verification_log.txt` | 验证日志 |
| `<output_dir>/temp/` | 临时文件 |
| `<output_dir>/*.nc` | 数据文件 |

---

## 📊 使用示例

### 示例1: 下载中国区域数据

```python
from download_ERA5_Land import ERA5LandDownloader

downloader = ERA5LandDownloader(output_dir='./data/china_2014')

files = downloader.download(
    variables=['2m_temperature', 'total_precipitation'],
    start_date='2014-01-01',
    end_date='2014-12-31',
    area=[60, 70, 10, 140],  # 中国区域
    split_by='month'
)
```

### 示例2: 下载特定小时数据

```python
files = downloader.download(
    variables=['surface_solar_radiation_downwards'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=[40, 100, 30, 120],
    time_hours=['12:00'],  # 仅正午数据
    split_by='month'
)
```

### 示例3: 下载并合并文件

```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-03-31',
    area=[40, 100, 30, 120],
    split_by='month',
    merge_files=True,
    final_output_name='ERA5_Land_2014_Q1.nc'
)
```

### 示例4: 批量下载多年数据

```python
downloader = ERA5LandDownloader(
    output_dir='./data/multi_year',
    max_workers=5
)

for year in range(2010, 2021):
    print(f"下载 {year} 年数据...")
    files = downloader.download(
        variables=['2m_temperature', 'total_precipitation'],
        start_date=f'{year}-01-01',
        end_date=f'{year}-12-31',
        area=[40, 100, 30, 120],
        split_by='month'
    )
    print(f"{year} 年完成: {len(files)} 个文件")
```

---

## 📝 注意事项

1. **CDS API配置**: 必须先配置CDS API才能下载数据
2. **下载限制**: CDS对单次请求的数据量有限制，建议按月分割
3. **存储空间**: ERA5-Land数据量较大，确保有足够的存储空间
4. **网络稳定**: 下载大文件需要稳定的网络连接
5. **验证日志**: 定期查看验证日志，确保数据质量

---

## 📚 相关资源

- [ERA5-Land 数据集](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [CDS API 文档](https://cds.climate.copernicus.eu/api-how-to)
- [xarray 文档](https://docs.xarray.dev/)
- [NetCDF 格式说明](https://www.unidata.ucar.edu/software/netcdf/)

---

## 📄 许可证

本项目仅供学术研究使用。

---

## 👨‍💻 技术支持

如有问题，请查看：
1. 本文档的常见问题部分
2. 验证日志文件
3. 下载状态文件

---

**版本**: v2.1  
**更新日期**: 2025-12-23

