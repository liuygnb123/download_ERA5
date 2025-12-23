# ERA5-Land Automatic Data Downloader

A comprehensive and user-friendly tool for automatically downloading ERA5-Land hourly data with customizable time ranges, spatial extents, variable selection, and complete data validation.

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Data Validation](#data-validation)
- [Advanced Features](#advanced-features)
- [FAQ](#faq)
- [File Structure](#file-structure)

---

## ✨ Features

### Core Functions
- ✅ **Automatic Download**: Automatically download ERA5-Land data from Copernicus Climate Data Store (CDS)
- ✅ **Flexible Configuration**: Customize variables, time ranges, spatial extents, and output locations
- ✅ **Parallel Acceleration**: Multi-threaded parallel downloading for faster speeds
- ✅ **Smart Retry**: Automatic retry on failure with configurable attempts and delays
- ✅ **Resume Support**: Track download status to avoid re-downloading existing files
- ✅ **Progress Display**: Real-time progress bars and status updates

### Data Validation
- ✅ **Variable Validation**: Check if all requested variables exist and contain data
- ✅ **Time Validation**: Verify year, month, and timestep accuracy
- ✅ **Spatial Validation**: Verify latitude and longitude ranges
- ✅ **Automatic Logging**: All validation results automatically logged to file

### Convenience Features
- ✅ **Auto ZIP Extraction**: Automatically detect and extract ZIP files from CDS
- ✅ **Variable Mapping**: Automatic handling of CDS API vs NetCDF variable names
- ✅ **File Merging**: Optional merging of multiple files into single NetCDF
- ✅ **Error Handling**: Comprehensive exception handling with detailed error logs

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install cdsapi xarray netCDF4 pandas tqdm
```

### 2. Configure CDS API

#### Step 1: Register Account
Visit [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) and register.

#### Step 2: Get API Key
After login, visit [API Key page](https://cds.climate.copernicus.eu/api-how-to) and copy your UID and API Key.

#### Step 3: Create Configuration File

**Windows**:  
Create file at `C:\Users\<username>\.cdsapirc` (no extension)

**Linux/Mac**:  
Create file at `~/.cdsapirc`

File content:
```
url: https://cds.climate.copernicus.eu/api/v2
key: <your-UID>:<your-API-Key>
```

**Quick Setup** (optional):
```bash
python setup_cdsapi.py
```

### 3. Run Example

```bash
python quick_start_example.py
```

Select example 1 to download temperature and solar radiation data for China region in January 2014.

---

## 📖 Usage

### Basic Usage

```python
from download_ERA5_Land import ERA5LandDownloader

# Create downloader
downloader = ERA5LandDownloader(
    output_dir='./data',      # Output directory
    max_workers=3,            # Parallel threads
    retry_times=3,            # Retry attempts
    retry_delay=10            # Retry delay (seconds)
)

# Download data
files = downloader.download(
    variables=['2m_temperature', 'surface_solar_radiation_downwards'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=[60, 70, 10, 140],   # [North, West, South, East]
    time_hours=None,          # None = all 24 hours
    split_by='month'          # Split by month
)

print(f"Successfully downloaded {len(files)} files")
```

### Parameter Description

#### ERA5LandDownloader Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_dir` | str | `'./ERA5_Land_data'` | Output directory |
| `max_workers` | int | `4` | Parallel download threads |
| `retry_times` | int | `3` | Retry attempts on failure |
| `retry_delay` | int | `10` | Retry delay (seconds) |
| `variable_mapping` | dict | `None` | Custom variable name mapping |

#### download() Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `variables` | list | ✅ | List of variable names |
| `start_date` | str | ✅ | Start date 'YYYY-MM-DD' |
| `end_date` | str | ✅ | End date 'YYYY-MM-DD' |
| `area` | list | ❌ | Spatial extent [N, W, S, E] |
| `time_hours` | list | ❌ | Hour list, None = all hours |
| `split_by` | str | ❌ | Split method 'month'/'year' |
| `merge_files` | bool | ❌ | Whether to merge files |
| `final_output_name` | str | ❌ | Merged file name |

### Common Variables

| CDS API Variable | NetCDF Variable | Description |
|-----------------|----------------|-------------|
| `2m_temperature` | `t2m` | 2m temperature |
| `2m_dewpoint_temperature` | `d2m` | 2m dewpoint temperature |
| `surface_solar_radiation_downwards` | `ssrd` | Surface solar radiation downwards |
| `surface_thermal_radiation_downwards` | `strd` | Surface thermal radiation downwards |
| `10m_u_component_of_wind` | `u10` | 10m U wind component |
| `10m_v_component_of_wind` | `v10` | 10m V wind component |
| `total_precipitation` | `tp` | Total precipitation |
| `surface_pressure` | `sp` | Surface pressure |

For complete variable list, see [CDS Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land).

---

## 🔍 Data Validation

### Automatic Validation

Each downloaded file is automatically validated comprehensively:

#### 1. Variable Validation
- ✅ Check if all requested variables exist
- ✅ Automatic variable name mapping
- ✅ Verify variable data is not empty

#### 2. Time Range Validation
- ✅ Verify year is correct (strict)
- ✅ Verify month is correct (strict)
- ⚠️ Check timestep count is reasonable (±10% tolerance)

#### 3. Spatial Range Validation
- ⚠️ Verify latitude range (±0.5° tolerance)
- ⚠️ Verify longitude range (±0.5° tolerance)

#### 4. Data Integrity
- ✅ Count valid data points and calculate percentage

### Validation Log

All validation results are automatically logged to:
```
<output_dir>/logs/verification_log.txt
```

Log example:
```
[2025-12-23 12:46:22] ℹ️ [INFO] Starting file verification: ERA5_Land_xxx.nc
[2025-12-23 12:46:22] ✅ [SUCCESS] File opened successfully
[2025-12-23 12:46:22] ℹ️ [INFO] File size: 558.23 MB

[2025-12-23 12:46:22] ℹ️ [INFO] 【1/4】Variable Validation
[2025-12-23 12:46:22] ✅ [SUCCESS]   ✅ Variable exists: 2m_temperature (mapped to t2m)

[2025-12-23 12:46:22] ℹ️ [INFO] 【2/4】Data Integrity Validation
[2025-12-23 12:46:25] ✅ [SUCCESS]   ✅ 2m_temperature: 261,293,544 data points, 189,179,112 valid (72.4%)

[2025-12-23 12:46:28] ℹ️ [INFO] 【3/4】Time Range Validation
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ Year matches: 2014
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ Month matches: 1

[2025-12-23 12:46:28] ℹ️ [INFO] 【4/4】Spatial Range Validation
[2025-12-23 12:46:28] ✅ [SUCCESS]   ✅ Latitude range matches (error 0.00°)

[2025-12-23 12:46:28] ✅ [SUCCESS] ✅ File verification passed! All checks meet requirements
```

### View Validation Log

```bash
# Windows
notepad <output_dir>\logs\verification_log.txt

# Linux/Mac
cat <output_dir>/logs/verification_log.txt
```

---

## 🔧 Advanced Features

### 1. Using Configuration File

Create `download_config.json`:
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

Run:
```bash
python download_ERA5_Land_with_config.py download_config.json
```

### 2. Custom Variable Mapping

If you encounter variable name mismatch:

```python
custom_mapping = {
    'your_cds_variable_name': 'actual_netcdf_variable_name'
}

downloader = ERA5LandDownloader(
    variable_mapping=custom_mapping
)
```

### 3. Retry Failed Downloads

```python
downloader = ERA5LandDownloader(output_dir='./data')

# Retry all failed tasks
downloaded_files = downloader.retry_failed_downloads()
```

### 4. Merge Multiple Files

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

### 5. Download Management

```bash
# View download status
python manage_downloads.py status

# Retry failed downloads
python manage_downloads.py retry

# Clean temporary files
python manage_downloads.py clean
```

---

## 📂 Output File Structure

```
<output_dir>/
├── logs/
│   ├── download_status.json      # Download status record
│   └── verification_log.txt      # Verification log
├── temp/                          # Temporary files
└── ERA5_Land_<vars>_<time>.nc    # Downloaded data files
```

### download_status.json

Records download status for each task:
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

## ❓ FAQ

### Q1: How to get CDS API Key?

**A**: 
1. Visit https://cds.climate.copernicus.eu/
2. Register and login
3. Visit https://cds.climate.copernicus.eu/api-how-to
4. Copy UID and API Key

### Q2: Slow download speed?

**A**: 
- Increase parallel threads: `max_workers=8`
- CDS servers are in Europe, may be slow from other regions
- Avoid downloading during peak hours

### Q3: "File verification failed" error?

**A**: 
1. Check verification log: `<output_dir>/logs/verification_log.txt`
2. Verify variable names are correct
3. If variable mapping issue, add custom mapping
4. If time/spatial range issue, check download parameters

### Q4: How to download global data?

**A**: 
Set `area` parameter to `None`:
```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=None  # Global data
)
```

### Q5: Can I download specific hours?

**A**: 
Yes, use `time_hours` parameter:
```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    time_hours=['00:00', '06:00', '12:00', '18:00']  # Every 6 hours
)
```

### Q6: Downloaded file is ZIP format?

**A**: 
The tool automatically detects and extracts ZIP files, no manual handling needed.

### Q7: How to view download progress?

**A**: 
- Console shows real-time progress bar
- Check `download_status.json` for detailed status
- Check `verification_log.txt` for verification results

### Q8: Do I need to handle WARNINGs in validation log?

**A**: 
Usually not. WARNING indicates minor deviations (e.g., timestep difference <10%, spatial range deviation <0.5°) that don't affect data usage.

---

## 📁 File Structure

### Core Files

| File | Description |
|------|-------------|
| `download_ERA5_Land.py` | Core download module |
| `quick_start_example.py` | Quick start examples |
| `download_ERA5_Land_with_config.py` | Config file download |
| `manage_downloads.py` | Download management tool |
| `setup_cdsapi.py` | CDS API setup helper |
| `requirements.txt` | Python dependencies |
| `README.md` | This document (Chinese) |
| `README_EN.md` | This document (English) |

### Configuration Files

| File | Description |
|------|-------------|
| `download_config.json` | Download config example |
| `~/.cdsapirc` | CDS API config file |

### Output Files

| File/Directory | Description |
|----------------|-------------|
| `<output_dir>/logs/download_status.json` | Download status |
| `<output_dir>/logs/verification_log.txt` | Verification log |
| `<output_dir>/temp/` | Temporary files |
| `<output_dir>/*.nc` | Data files |

---

## 📊 Usage Examples

### Example 1: Download China Region Data

```python
from download_ERA5_Land import ERA5LandDownloader

downloader = ERA5LandDownloader(output_dir='./data/china_2014')

files = downloader.download(
    variables=['2m_temperature', 'total_precipitation'],
    start_date='2014-01-01',
    end_date='2014-12-31',
    area=[60, 70, 10, 140],  # China region
    split_by='month'
)
```

### Example 2: Download Specific Hours

```python
files = downloader.download(
    variables=['surface_solar_radiation_downwards'],
    start_date='2014-01-01',
    end_date='2014-01-31',
    area=[40, 100, 30, 120],
    time_hours=['12:00'],  # Noon only
    split_by='month'
)
```

### Example 3: Download and Merge Files

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

### Example 4: Batch Download Multi-Year Data

```python
downloader = ERA5LandDownloader(
    output_dir='./data/multi_year',
    max_workers=5
)

for year in range(2010, 2021):
    print(f"Downloading {year} data...")
    files = downloader.download(
        variables=['2m_temperature', 'total_precipitation'],
        start_date=f'{year}-01-01',
        end_date=f'{year}-12-31',
        area=[40, 100, 30, 120],
        split_by='month'
    )
    print(f"{year} completed: {len(files)} files")
```

---

## 📝 Notes

1. **CDS API Configuration**: Must configure CDS API before downloading
2. **Download Limits**: CDS has limits on single request data volume, recommend splitting by month
3. **Storage Space**: ERA5-Land data is large, ensure sufficient storage
4. **Network Stability**: Large file downloads require stable network connection
5. **Verification Log**: Regularly check validation log to ensure data quality

---

## 📚 Related Resources

- [ERA5-Land Dataset](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [CDS API Documentation](https://cds.climate.copernicus.eu/api-how-to)
- [xarray Documentation](https://docs.xarray.dev/)
- [NetCDF Format](https://www.unidata.ucar.edu/software/netcdf/)

---

## 📄 License

This project is for academic research use only.

---

## 👨‍💻 Support

For issues, please check:
1. FAQ section in this document
2. Verification log file
3. Download status file

---

**Version**: v2.1  
**Last Updated**: 2025-12-23

