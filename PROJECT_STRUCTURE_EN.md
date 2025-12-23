# Project Structure

Project structure and file descriptions for ERA5-Land Automatic Data Downloader.

## 📁 Project Directory Structure

```
ERA5-Land-Downloader/
│
├── 📄 README.md                              # Main documentation (Chinese)
├── 📄 README_EN.md                           # Main documentation (English)
├── 📄 QUICKSTART.md                          # Quick start guide (Chinese)
├── 📄 QUICKSTART_EN.md                       # Quick start guide (English)
├── 📄 VARIABLES.md                           # Variable reference (Chinese)
├── 📄 VARIABLES_EN.md                        # Variable reference (English)
├── 📄 PROJECT_STRUCTURE.md                   # This file (Chinese)
├── 📄 PROJECT_STRUCTURE_EN.md                # This file (English)
├── 📄 requirements.txt                       # Python dependencies
│
├── 🐍 download_ERA5_Land.py                  # Core download module
├── 🐍 quick_start_example.py                # Quick start examples
├── 🐍 download_ERA5_Land_with_config.py     # Config file download
├── 🐍 manage_downloads.py                   # Download management tool
├── 🐍 setup_cdsapi.py                       # CDS API setup helper
│
└── 📋 download_config.json                   # Config file example
```

## 📄 Documentation Files

### README.md / README_EN.md
**Main Documentation** - Complete usage guide and reference

Contents:
- Feature highlights
- Installation and configuration
- Detailed usage instructions
- Data validation explanation
- Advanced features
- FAQ
- Complete examples

Target audience: All users, especially those needing detailed feature information

### QUICKSTART.md / QUICKSTART_EN.md
**Quick Start Guide** - Get started in 5 minutes

Contents:
- Three-step quick start
- Simplest code example
- Common scenario examples
- Quick troubleshooting

Target audience: New users who want to start quickly

### VARIABLES.md / VARIABLES_EN.md
**Variable Reference** - List of available ERA5-Land variables

Contents:
- Complete variable list
- Variable name mapping
- Variable units and descriptions
- Variable usage examples

Target audience: Users who need to look up specific variables

### PROJECT_STRUCTURE.md / PROJECT_STRUCTURE_EN.md
**Project Structure** - This file

Contents:
- Project directory structure
- File function descriptions
- Usage workflow diagrams

Target audience: Users who want to understand project structure, developers

## 🐍 Python Files

### download_ERA5_Land.py
**Core Download Module** - Main functionality implementation

Features:
- `ERA5LandDownloader` class: Core downloader
- Automatic download, validation, retry
- Parallel download support
- Complete data validation
- Logging

Usage:
```python
from download_ERA5_Land import ERA5LandDownloader
downloader = ERA5LandDownloader()
```

### quick_start_example.py
**Quick Start Examples** - Interactive example program

Features:
- 6 preset example scenarios
- Interactive menu selection
- Complete example code
- Data reading and processing examples

Usage:
```bash
python quick_start_example.py
```

### download_ERA5_Land_with_config.py
**Config File Download** - Download using JSON config file

Features:
- Read configuration from JSON file
- Batch download support
- Suitable for automated tasks

Usage:
```bash
python download_ERA5_Land_with_config.py download_config.json
```

### manage_downloads.py
**Download Management Tool** - Manage download tasks

Features:
- View download status
- Retry failed downloads
- Clean temporary files
- View verification logs

Usage:
```bash
python manage_downloads.py status    # View status
python manage_downloads.py retry     # Retry failed
python manage_downloads.py clean     # Clean temp files
```

### setup_cdsapi.py
**CDS API Setup Helper** - Interactive CDS API configuration

Features:
- Interactive input for UID and API Key
- Automatic config file creation
- Verify configuration is correct

Usage:
```bash
python setup_cdsapi.py
```

## 📋 Configuration Files

### requirements.txt
**Python Dependencies**

Contents:
```
cdsapi>=0.5.1
xarray>=2023.1.0
netCDF4>=1.6.0
pandas>=2.0.0
tqdm>=4.65.0
```

Usage:
```bash
pip install -r requirements.txt
```

### download_config.json
**Config File Example**

Purpose:
- Example for config file download
- Can be copied and modified for use

Example content:
```json
{
  "output_dir": "./data/china_2014",
  "max_workers": 5,
  "variables": ["2m_temperature"],
  "start_date": "2014-01-01",
  "end_date": "2014-12-31",
  "area": [60, 70, 10, 140]
}
```

## 🗂️ Runtime Generated Files

### Output Directory Structure

```
<output_dir>/
├── logs/
│   ├── download_status.json      # Download status record
│   └── verification_log.txt      # Verification log
├── temp/                          # Temporary files
└── ERA5_Land_*.nc                # Downloaded data files
```

### download_status.json
**Download Status Record**

Contents:
- Download status for each task
- File paths
- Timestamps
- Error messages (if failed)

### verification_log.txt
**Verification Log**

Contents:
- Detailed file verification process
- Variable check results
- Time and spatial range validation
- Data integrity statistics

## 🔄 Usage Workflows

### Workflow 1: First-time Use

```
Install Dependencies → Configure CDS API → Run Example → View Results
```

1. `pip install -r requirements.txt`
2. `python setup_cdsapi.py`
3. `python quick_start_example.py`
4. Check output directory and logs

### Workflow 2: Regular Use

```
Write Script → Run Download → Auto Validation → Check Logs → Use Data or Retry
```

### Workflow 3: Batch Download

```
Prepare Config → Run Config Download → Auto Download & Validate → Check Summary Log
```

1. Edit `download_config.json`
2. `python download_ERA5_Land_with_config.py download_config.json`
3. Check `logs/verification_log.txt`

## 📊 Core Classes and Methods

### ERA5LandDownloader Class

```python
class ERA5LandDownloader:
    def __init__(self, output_dir, max_workers, retry_times, 
                 retry_delay, variable_mapping)
    
    def download(self, variables, start_date, end_date, 
                 area, time_hours, split_by, merge_files)
    
    def retry_failed_downloads(self)
    
    def merge_netcdf_files(self, file_list, output_name)
    
    # Internal methods
    def _verify_file(self, file_path, expected_variables, task)
    def _log_verification(self, message, level)
```

### Main Method Descriptions

| Method | Function | Return Value |
|--------|----------|--------------|
| `download()` | Download data | List of file paths |
| `retry_failed_downloads()` | Retry failed downloads | List of successfully downloaded files |
| `merge_netcdf_files()` | Merge multiple NetCDF files | Path to merged file |

## 🎯 Recommended Usage Paths

### New Users
1. Read `QUICKSTART.md` or `QUICKSTART_EN.md`
2. Run `python setup_cdsapi.py`
3. Run `python quick_start_example.py`
4. Check generated data and logs

### Advanced Users
1. Read `README.md` or `README_EN.md` complete documentation
2. Refer to `VARIABLES.md` or `VARIABLES_EN.md` to select variables
3. Write your own download scripts
4. Use `manage_downloads.py` to manage downloads

### Batch Download
1. Prepare `download_config.json`
2. Run `python download_ERA5_Land_with_config.py`
3. Use `manage_downloads.py` to check status

## 📝 Notes

1. **Don't modify core files**: `download_ERA5_Land.py` is the core module, don't modify unless necessary
2. **Keep log files**: `verification_log.txt` records important validation information
3. **Regular cleanup**: Use `manage_downloads.py clean` to clean temporary files
4. **Backup config**: If you modify `download_config.json`, recommend backing it up

## 🔧 Developer Information

### Extending Features

To extend features, mainly modify these files:
- `download_ERA5_Land.py`: Core functionality
- `quick_start_example.py`: Add new examples
- `manage_downloads.py`: Add management features

### Adding New Variable Mapping

Add to `DEFAULT_VARIABLE_MAPPING` dictionary in `download_ERA5_Land.py`:
```python
DEFAULT_VARIABLE_MAPPING = {
    'your_cds_variable': 'netcdf_variable',
    # ...
}
```

---

## 📚 Related Resources

- [ERA5-Land Dataset](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land)
- [CDS API Documentation](https://cds.climate.copernicus.eu/api-how-to)
- [xarray Documentation](https://docs.xarray.dev/)

---

**Version**: v2.1  
**Last Updated**: 2025-12-23

