# Quick Start Guide

Get started with ERA5-Land Data Downloader in 5 minutes.

## 🚀 Three Steps to Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure CDS API

Run the configuration helper:
```bash
python setup_cdsapi.py
```

Enter your CDS API UID and Key when prompted (get them from https://cds.climate.copernicus.eu/api-how-to).

### Step 3: Run Example

```bash
python quick_start_example.py
```

Select example 1 to start downloading!

---

## 📝 Simplest Code Example

```python
from download_ERA5_Land import ERA5LandDownloader

# Create downloader
downloader = ERA5LandDownloader(output_dir='./my_data')

# Download data
files = downloader.download(
    variables=['2m_temperature'],           # 2m temperature
    start_date='2014-01-01',                # Start date
    end_date='2014-01-31',                  # End date
    area=[60, 70, 10, 140]                  # [North, West, South, East]
)

print(f"✅ Successfully downloaded {len(files)} files")
```

---

## 🎯 Common Scenarios

### Scenario 1: Download China Region Data

```python
downloader = ERA5LandDownloader(output_dir='./data/china')

files = downloader.download(
    variables=['2m_temperature', 'total_precipitation'],
    start_date='2020-01-01',
    end_date='2020-12-31',
    area=[60, 70, 10, 140],  # China region
    split_by='month'
)
```

### Scenario 2: Download Specific Hours

```python
files = downloader.download(
    variables=['surface_solar_radiation_downwards'],
    start_date='2020-01-01',
    end_date='2020-01-31',
    area=[40, 100, 30, 120],
    time_hours=['00:00', '06:00', '12:00', '18:00']  # Every 6 hours
)
```

### Scenario 3: Download and Merge Files

```python
files = downloader.download(
    variables=['2m_temperature'],
    start_date='2020-01-01',
    end_date='2020-03-31',
    split_by='month',
    merge_files=True,                        # Merge files
    final_output_name='ERA5_2020_Q1.nc'
)
```

---

## 📊 View Results

### Downloaded Files

```
./my_data/
├── ERA5_Land_2m_temperature_202001.nc
├── ERA5_Land_2m_temperature_202002.nc
└── logs/
    ├── download_status.json      # Download status
    └── verification_log.txt      # Verification log
```

### View Verification Log

```bash
# Windows
notepad my_data\logs\verification_log.txt

# Linux/Mac
cat my_data/logs/verification_log.txt
```

---

## 🔍 Data Validation

Each file is automatically validated:
- ✅ Variables exist
- ✅ Time range is correct
- ✅ Spatial range is correct
- ✅ Data is complete

Validation results are saved in `logs/verification_log.txt`.

---

## ❓ Troubleshooting

### Issue 1: pip install fails

```bash
# Use mirror (for China users)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Issue 2: CDS API configuration error

Check `~/.cdsapirc` file (Windows: `C:\Users\<username>\.cdsapirc`):
```
url: https://cds.climate.copernicus.eu/api/v2
key: <your-UID>:<your-API-Key>
```

### Issue 3: Download fails

1. Check network connection
2. View error log: `logs/verification_log.txt`
3. Retry failed downloads:
```python
downloader.retry_failed_downloads()
```

---

## 📚 More Information

- Full Documentation: `README.md` (Chinese) or `README_EN.md` (English)
- Example Code: `quick_start_example.py`
- Config File Example: `download_config.json`

---

**Happy Downloading!** 🎉

