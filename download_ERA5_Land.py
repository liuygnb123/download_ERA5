"""
ERA5-Land 小时数据自动下载脚本
功能：
    1. 自动下载ERA5-Land hourly数据并保存为nc文件
    2. 支持自定义变量名、时间范围、经纬度范围和保存位置
    3. 支持并行下载加速
    4. 自动检查下载完整性，失败时重新下载
    5. 完善的异常处理机制

使用前请先安装依赖：
    pip install cdsapi xarray netCDF4 pandas tqdm

使用前需要配置CDS API：
    1. 注册账号：https://cds.climate.copernicus.eu/
    2. 获取API Key：https://cds.climate.copernicus.eu/api-how-to
    3. 创建配置文件 ~/.cdsapirc (Linux/Mac) 或 %USERPROFILE%\.cdsapirc (Windows)
    文件内容：
        url: https://cds.climate.copernicus.eu/api/v2
        key: <your-uid>:<your-api-key>
"""

import cdsapi
import os
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import traceback
import shutil


class ERA5LandDownloader:
    """ERA5-Land数据下载器"""
    
    # 默认的变量名映射表（CDS API名称 -> NetCDF文件中的实际名称）
    DEFAULT_VARIABLE_MAPPING = {
        '2m_temperature': 't2m',
        '2m_dewpoint_temperature': 'd2m',
        'skin_temperature': 'skt',
        'soil_temperature_level_1': 'stl1',
        'soil_temperature_level_2': 'stl2',
        'soil_temperature_level_3': 'stl3',
        'soil_temperature_level_4': 'stl4',
        'surface_solar_radiation_downwards': 'ssrd',
        'surface_thermal_radiation_downwards': 'strd',
        'surface_net_solar_radiation': 'ssr',
        'surface_net_thermal_radiation': 'str',
        'surface_solar_radiation_downward_clear_sky': 'ssrdc',
        'surface_thermal_radiation_downward_clear_sky': 'strdc',
        '10m_u_component_of_wind': 'u10',
        '10m_v_component_of_wind': 'v10',
        'total_precipitation': 'tp',
        'snowfall': 'sf',
        'surface_pressure': 'sp',
        'surface_runoff': 'sro',
        'sub_surface_runoff': 'ssro',
        'volumetric_soil_water_layer_1': 'swvl1',
        'volumetric_soil_water_layer_2': 'swvl2',
        'volumetric_soil_water_layer_3': 'swvl3',
        'volumetric_soil_water_layer_4': 'swvl4',
        'leaf_area_index_high_vegetation': 'lai_hv',
        'leaf_area_index_low_vegetation': 'lai_lv',
        'snow_depth': 'sd',
        'snow_cover': 'snowc',
        'evaporation': 'e',
        'potential_evaporation': 'pev',
        'runoff': 'ro',
        'total_evaporation': 'e',
    }
    
    def __init__(self, output_dir='./ERA5_Land_data', max_workers=4, 
                 retry_times=3, retry_delay=10, variable_mapping=None):
        """
        初始化下载器
        
        参数:
            output_dir: 数据保存目录
            max_workers: 并行下载的最大线程数
            retry_times: 失败后重试次数
            retry_delay: 重试延迟时间(秒)
            variable_mapping: 自定义变量名映射字典，格式为 {CDS_API_name: NetCDF_variable_name}
                            如果为None，使用默认映射表
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        
        # 设置变量名映射表
        if variable_mapping is None:
            self.variable_mapping = self.DEFAULT_VARIABLE_MAPPING.copy()
        else:
            # 合并用户自定义映射和默认映射
            self.variable_mapping = self.DEFAULT_VARIABLE_MAPPING.copy()
            self.variable_mapping.update(variable_mapping)
        
        # 日志目录
        self.log_dir = self.output_dir / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 临时文件目录
        self.temp_dir = self.output_dir / 'temp'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载状态文件
        self.status_file = self.log_dir / 'download_status.json'
        self.load_status()
        
        # 验证日志文件
        self.verification_log_file = self.log_dir / 'verification_log.txt'
        self._init_verification_log()
    
    def load_status(self):
        """加载下载状态"""
        if self.status_file.exists():
            with open(self.status_file, 'r', encoding='utf-8') as f:
                self.download_status = json.load(f)
        else:
            self.download_status = {}
    
    def save_status(self):
        """保存下载状态"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_status, f, indent=2, ensure_ascii=False)
    
    def _init_verification_log(self):
        """初始化验证日志文件"""
        if not self.verification_log_file.exists():
            with open(self.verification_log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("ERA5-Land 数据验证日志\n")
                f.write("="*80 + "\n\n")
    
    def _log_verification(self, message, level='INFO'):
        """
        写入验证日志
        
        参数:
            message: 日志消息
            level: 日志级别 (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_symbols = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅'
        }
        symbol = level_symbols.get(level, 'ℹ️')
        
        log_line = f"[{timestamp}] {symbol} [{level}] {message}\n"
        
        with open(self.verification_log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        # 同时输出到控制台（ERROR和WARNING级别）
        if level in ['ERROR', 'WARNING']:
            print(log_line.strip())
    
    def generate_download_tasks(self, variables, start_date, end_date, 
                                area=None, time_hours=None, split_by='month'):
        """
        生成下载任务列表
        
        参数:
            variables: 变量名列表，例如 ['2m_temperature', '10m_u_component_of_wind']
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            area: 区域范围 [N, W, S, E]，例如 [60, 70, 10, 140] (中国区域)
                  如果为None，则下载全球数据
            time_hours: 小时列表，例如 ['00:00', '01:00', ..., '23:00']
                       如果为None，则下载所有24小时
            split_by: 数据分割方式 'month'(按月) 或 'year'(按年)
        
        返回:
            任务列表，每个任务是一个字典
        """
        if time_hours is None:
            time_hours = [f'{h:02d}:00' for h in range(24)]
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        tasks = []
        
        if split_by == 'month':
            # 按月分割
            current = start
            while current <= end:
                year = current.year
                month = current.month
                
                # 计算该月的开始和结束日期
                month_start = current
                if current.month == 12:
                    month_end = datetime(current.year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(current.year, current.month + 1, 1) - timedelta(days=1)
                
                # 确保不超过结束日期
                month_end = min(month_end, end)
                
                # 生成该月的所有日期
                days = pd.date_range(month_start, month_end, freq='D')
                day_list = [d.strftime('%d') for d in days]
                
                task = {
                    'variables': variables,
                    'year': str(year),
                    'month': f'{month:02d}',
                    'days': day_list,
                    'time_hours': time_hours,
                    'area': area,
                    'task_id': f'{year}{month:02d}'
                }
                tasks.append(task)
                
                # 移动到下个月
                if current.month == 12:
                    current = datetime(current.year + 1, 1, 1)
                else:
                    current = datetime(current.year, current.month + 1, 1)
        
        elif split_by == 'year':
            # 按年分割
            for year in range(start.year, end.year + 1):
                year_start = max(start, datetime(year, 1, 1))
                year_end = min(end, datetime(year, 12, 31))
                
                # 生成该年的所有月份
                months = pd.date_range(year_start, year_end, freq='MS')
                month_list = [m.strftime('%m') for m in months]
                
                # 生成该年的所有日期
                days = pd.date_range(year_start, year_end, freq='D')
                day_list = [d.strftime('%d') for d in days]
                
                task = {
                    'variables': variables,
                    'year': str(year),
                    'months': month_list,
                    'days': list(set(day_list)),  # 去重
                    'time_hours': time_hours,
                    'area': area,
                    'task_id': str(year)
                }
                tasks.append(task)
        
        return tasks
    
    def download_single_task(self, task):
        """
        下载单个任务
        
        参数:
            task: 任务字典
        
        返回:
            (success, task_id, output_file, error_msg)
        """
        task_id = task['task_id']
        variables = task['variables']
        
        # 生成输出文件名
        var_str = '_'.join(variables)
        output_filename = f"ERA5_Land_{var_str}_{task_id}.nc"
        output_file = self.output_dir / output_filename
        temp_file = self.temp_dir / f"{output_filename}.tmp"
        
        # 检查是否已经成功下载
        if task_id in self.download_status and self.download_status[task_id].get('status') == 'completed':
            if output_file.exists() and self._verify_file(output_file, variables, task):
                return True, task_id, str(output_file), "已存在且验证通过"
        
        # 构建请求参数
        request_params = {
            'variable': variables,
            'year': task['year'],
            'time': task['time_hours'],
            'format': 'netcdf',
        }
        
        # 添加月份参数
        if 'month' in task:
            request_params['month'] = task['month']
        elif 'months' in task:
            request_params['month'] = task['months']
        
        # 添加日期参数
        request_params['day'] = task['days']
        
        # 添加区域参数
        if task.get('area'):
            request_params['area'] = task['area']
        
        # 尝试下载
        for attempt in range(self.retry_times):
            try:
                # 初始化CDS API客户端
                c = cdsapi.Client()
                
                # 下载到临时文件
                c.retrieve(
                    'reanalysis-era5-land',
                    request_params,
                    str(temp_file)
                )
                
                # 验证下载的文件
                if not temp_file.exists():
                    raise Exception("下载的文件不存在")
                
                # #region agent log
                log_data = {"location": "download_ERA5_Land.py:download_single_task:after_download", "message": "文件下载完成", "data": {"temp_file": str(temp_file), "file_size": temp_file.stat().st_size, "exists": temp_file.exists()}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                try:
                    with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                
                # 检查是否是ZIP文件并解压
                import zipfile
                
                actual_nc_file = temp_file
                extract_dir = None
                
                # #region agent log
                is_zip = zipfile.is_zipfile(temp_file)
                log_data = {"location": "download_ERA5_Land.py:download_single_task:check_zip", "message": "检查文件类型", "data": {"is_zipfile": is_zip, "file_path": str(temp_file)}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                try:
                    with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                
                if zipfile.is_zipfile(temp_file):
                    print(f"检测到ZIP文件，正在解压...")
                    
                    # 创建解压目录
                    extract_dir = temp_file.parent / f"{temp_file.stem}_extracted"
                    extract_dir.mkdir(exist_ok=True)
                    
                    # 解压ZIP文件
                    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # 查找解压后的NC文件
                    nc_files = list(extract_dir.glob('*.nc'))
                    
                    # #region agent log
                    log_data = {"location": "download_ERA5_Land.py:download_single_task:after_extract", "message": "ZIP解压完成", "data": {"nc_files_count": len(nc_files), "nc_files": [str(f.name) for f in nc_files]}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                    try:
                        with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                    except: pass
                    # #endregion
                    
                    if not nc_files:
                        raise Exception("ZIP文件中没有找到NC文件")
                    
                    actual_nc_file = nc_files[0]  # 使用第一个NC文件
                    print(f"解压完成: {actual_nc_file.name}")
                
                # 验证文件（使用解压后的文件或原始文件）
                # 传入完整的任务信息进行全面验证
                if not self._verify_file(actual_nc_file, variables, task):
                    raise Exception("文件验证失败")
                
                # 移动到最终位置
                if actual_nc_file != temp_file:
                    # 如果是解压的文件，移动NC文件
                    shutil.move(str(actual_nc_file), str(output_file))
                    # 清理临时ZIP文件和解压目录
                    if temp_file.exists():
                        temp_file.unlink()
                    if extract_dir and extract_dir.exists():
                        shutil.rmtree(extract_dir)
                    
                    # #region agent log
                    log_data = {"location": "download_ERA5_Land.py:download_single_task:move_extracted", "message": "移动解压后的文件", "data": {"from": str(actual_nc_file), "to": str(output_file)}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                    try:
                        with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                    except: pass
                    # #endregion
                else:
                    # 如果不是ZIP文件，直接移动
                    shutil.move(str(temp_file), str(output_file))
                    
                    # #region agent log
                    log_data = {"location": "download_ERA5_Land.py:download_single_task:move_direct", "message": "直接移动文件", "data": {"from": str(temp_file), "to": str(output_file)}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                    try:
                        with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                    except: pass
                    # #endregion
                
                # 更新状态
                self.download_status[task_id] = {
                    'status': 'completed',
                    'file': str(output_file),
                    'timestamp': datetime.now().isoformat(),
                    'variables': variables,
                    'task': task
                }
                self.save_status()
                
                # #region agent log
                log_data = {"location": "download_ERA5_Land.py:download_single_task:success", "message": "任务完成", "data": {"task_id": task_id, "output_file": str(output_file)}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                try:
                    with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                
                return True, task_id, str(output_file), None
            
            except Exception as e:
                error_msg = f"尝试 {attempt + 1}/{self.retry_times} 失败: {str(e)}"
                
                # #region agent log
                log_data = {"location": "download_ERA5_Land.py:download_single_task:error", "message": "下载失败", "data": {"attempt": attempt + 1, "error": str(e), "traceback": traceback.format_exc()}, "timestamp": int(time.time() * 1000), "sessionId": "debug-session", "hypothesisId": "F"}
                try:
                    with open(r"g:\光伏废物回收\实验分析\base\5-气候变量\degradation\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                
                # 清理临时文件
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                
                # 清理解压目录
                if 'extract_dir' in locals() and extract_dir and extract_dir.exists():
                    try:
                        shutil.rmtree(extract_dir)
                    except:
                        pass
                
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    # 最后一次尝试也失败了
                    self.download_status[task_id] = {
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'traceback': traceback.format_exc(),
                        'task': task  # 保存任务信息以便重试
                    }
                    self.save_status()
                    return False, task_id, None, error_msg
        
        return False, task_id, None, "未知错误"
    
    def _verify_file(self, file_path, expected_variables, task=None):
        """
        验证下载的文件是否完整
        
        参数:
            file_path: 文件路径
            expected_variables: 期望的变量列表
            task: 任务信息字典（包含时间、空间范围等）
        
        返回:
            True表示验证通过，False表示验证失败
        """
        # 记录验证开始
        self._log_verification("="*80)
        self._log_verification(f"开始验证文件: {Path(file_path).name}", 'INFO')
        self._log_verification(f"文件路径: {file_path}", 'INFO')
        
        try:
            # 尝试打开文件
            ds = xr.open_dataset(file_path)
            self._log_verification("文件打开成功", 'SUCCESS')
            
            # 记录文件基本信息
            file_size_mb = Path(file_path).stat().st_size / (1024*1024)
            self._log_verification(f"文件大小: {file_size_mb:.2f} MB", 'INFO')
            self._log_verification(f"文件中的变量: {list(ds.data_vars.keys())}", 'INFO')
            
            # 1. 验证变量
            self._log_verification("\n【1/4】变量验证", 'INFO')
            missing_vars = []
            for var in expected_variables:
                # 获取映射后的变量名
                mapped_var = self.variable_mapping.get(var, var)
                
                # 检查原始名称或映射后的名称
                if var not in ds.variables and var not in ds.data_vars and \
                   mapped_var not in ds.variables and mapped_var not in ds.data_vars:
                    missing_vars.append(f"{var} (映射为 {mapped_var})")
                    self._log_verification(f"  ❌ 变量缺失: {var} (映射为 {mapped_var})", 'ERROR')
                else:
                    self._log_verification(f"  ✅ 变量存在: {var} (映射为 {mapped_var})", 'SUCCESS')
            
            if missing_vars:
                self._log_verification(f"验证失败: 缺少 {len(missing_vars)} 个变量", 'ERROR')
                self._log_verification(f"文件中实际变量: {list(ds.data_vars.keys())}", 'INFO')
                ds.close()
                return False
            
            # 2. 验证数据完整性
            self._log_verification("\n【2/4】数据完整性验证", 'INFO')
            for var in expected_variables:
                mapped_var = self.variable_mapping.get(var, var)
                
                # 尝试使用映射后的名称
                if mapped_var in ds.variables or mapped_var in ds.data_vars:
                    data = ds[mapped_var]
                    actual_var = mapped_var
                elif var in ds.variables or var in ds.data_vars:
                    data = ds[var]
                    actual_var = var
                else:
                    continue
                
                if data.size == 0:
                    self._log_verification(f"  ❌ 变量 {var} 数据为空", 'ERROR')
                    ds.close()
                    return False
                else:
                    # 计算有效数据比例
                    valid_count = (~data.isnull()).sum().values
                    total_count = data.size
                    valid_percent = (valid_count / total_count * 100) if total_count > 0 else 0
                    self._log_verification(
                        f"  ✅ {var}: {total_count:,} 数据点, {valid_count:,} 有效 ({valid_percent:.1f}%)", 
                        'SUCCESS'
                    )
            
            # 3. 验证时间范围
            self._log_verification("\n【3/4】时间范围验证", 'INFO')
            if task and 'year' in task:
                try:
                    # 获取时间维度
                    time_var = None
                    for t in ['time', 'valid_time', 'forecast_reference_time']:
                        if t in ds.variables or t in ds.coords:
                            time_var = t
                            break
                    
                    if time_var:
                        times = pd.to_datetime(ds[time_var].values)
                        file_year = times[0].year
                        expected_year = int(task['year'])
                        
                        self._log_verification(f"  时间维度: {time_var}", 'INFO')
                        self._log_verification(f"  起始时间: {times[0]}", 'INFO')
                        self._log_verification(f"  结束时间: {times[-1]}", 'INFO')
                        self._log_verification(f"  时间步数: {len(times)}", 'INFO')
                        
                        # 验证年份
                        if file_year != expected_year:
                            self._log_verification(f"  ❌ 年份不匹配: 期望 {expected_year}, 实际 {file_year}", 'ERROR')
                            ds.close()
                            return False
                        else:
                            self._log_verification(f"  ✅ 年份匹配: {file_year}", 'SUCCESS')
                        
                        # 验证月份（如果指定）
                        if 'month' in task:
                            file_month = times[0].month
                            expected_month = int(task['month'])
                            if file_month != expected_month:
                                self._log_verification(f"  ❌ 月份不匹配: 期望 {expected_month}, 实际 {file_month}", 'ERROR')
                                ds.close()
                                return False
                            else:
                                self._log_verification(f"  ✅ 月份匹配: {file_month}", 'SUCCESS')
                        
                        # 验证时间步数（粗略检查）
                        expected_hours = len(task.get('time_hours', []))
                        expected_days = len(task.get('days', []))
                        if expected_hours > 0 and expected_days > 0:
                            expected_timesteps = expected_hours * expected_days
                            actual_timesteps = len(times)
                            diff_percent = abs(actual_timesteps - expected_timesteps) / expected_timesteps * 100
                            
                            # 允许一定的误差（±10%）
                            if abs(actual_timesteps - expected_timesteps) > expected_timesteps * 0.1:
                                self._log_verification(
                                    f"  ⚠️ 时间步数偏差: 期望 {expected_timesteps}, 实际 {actual_timesteps} (偏差 {diff_percent:.1f}%)", 
                                    'WARNING'
                                )
                            else:
                                self._log_verification(f"  ✅ 时间步数合理: {actual_timesteps} (期望 {expected_timesteps})", 'SUCCESS')
                    else:
                        self._log_verification("  ⚠️ 未找到时间维度", 'WARNING')
                except Exception as e:
                    self._log_verification(f"  ⚠️ 时间验证异常: {e}", 'WARNING')
            else:
                self._log_verification("  ℹ️ 跳过时间验证（未提供任务信息）", 'INFO')
                
            # 4. 验证空间范围
            self._log_verification("\n【4/4】空间范围验证", 'INFO')
            if task and 'area' in task and task['area']:
                try:
                    area = task['area']  # [N, W, S, E]
                    
                    # 获取纬度和经度
                    lat_var = 'latitude' if 'latitude' in ds.coords else 'lat'
                    lon_var = 'longitude' if 'longitude' in ds.coords else 'lon'
                    
                    if lat_var in ds.coords and lon_var in ds.coords:
                        lats = ds[lat_var].values
                        lons = ds[lon_var].values
                        
                        lat_min, lat_max = lats.min(), lats.max()
                        lon_min, lon_max = lons.min(), lons.max()
                        
                        self._log_verification(f"  纬度范围: {lat_min:.2f}° 到 {lat_max:.2f}°", 'INFO')
                        self._log_verification(f"  经度范围: {lon_min:.2f}° 到 {lon_max:.2f}°", 'INFO')
                        self._log_verification(f"  网格点数: {len(lats)} × {len(lons)}", 'INFO')
                        
                        # 检查纬度范围（允许一定误差）
                        expected_lat_min, expected_lat_max = min(area[0], area[2]), max(area[0], area[2])
                        lat_diff = max(abs(lat_min - expected_lat_min), abs(lat_max - expected_lat_max))
                        
                        # 允许0.5度的误差
                        if lat_diff > 0.5:
                            self._log_verification(
                                f"  ⚠️ 纬度偏差: 期望 {expected_lat_min:.2f}°~{expected_lat_max:.2f}°, 实际 {lat_min:.2f}°~{lat_max:.2f}° (偏差 {lat_diff:.2f}°)", 
                                'WARNING'
                            )
                        else:
                            self._log_verification(f"  ✅ 纬度范围匹配 (误差 {lat_diff:.2f}°)", 'SUCCESS')
                        
                        # 检查经度范围（允许一定误差）
                        expected_lon_min, expected_lon_max = min(area[1], area[3]), max(area[1], area[3])
                        lon_diff = max(abs(lon_min - expected_lon_min), abs(lon_max - expected_lon_max))
                        
                        # 允许0.5度的误差
                        if lon_diff > 0.5:
                            self._log_verification(
                                f"  ⚠️ 经度偏差: 期望 {expected_lon_min:.2f}°~{expected_lon_max:.2f}°, 实际 {lon_min:.2f}°~{lon_max:.2f}° (偏差 {lon_diff:.2f}°)", 
                                'WARNING'
                            )
                        else:
                            self._log_verification(f"  ✅ 经度范围匹配 (误差 {lon_diff:.2f}°)", 'SUCCESS')
                    else:
                        self._log_verification("  ⚠️ 未找到空间维度", 'WARNING')
                except Exception as e:
                    self._log_verification(f"  ⚠️ 空间验证异常: {e}", 'WARNING')
            else:
                self._log_verification("  ℹ️ 跳过空间验证（未提供区域信息）", 'INFO')
            
            ds.close()
            
            # 验证成功
            self._log_verification("\n" + "="*80, 'SUCCESS')
            self._log_verification("✅ 文件验证通过！所有检查项均符合要求", 'SUCCESS')
            self._log_verification("="*80 + "\n", 'SUCCESS')
            return True
        
        except Exception as e:
            error_msg = f"文件验证异常: {e}"
            self._log_verification(f"\n❌ {error_msg}", 'ERROR')
            self._log_verification(f"详细错误:\n{traceback.format_exc()}", 'ERROR')
            self._log_verification("="*80 + "\n", 'ERROR')
            print(error_msg)
            print(f"详细错误: {traceback.format_exc()}")
            return False
    
    def download(self, variables, start_date, end_date, area=None, 
                 time_hours=None, split_by='month', merge_files=False,
                 final_output_name=None):
        """
        执行批量下载
        
        参数:
            variables: 变量名列表
            start_date: 开始日期
            end_date: 结束日期
            area: 区域范围
            time_hours: 小时列表
            split_by: 分割方式
            merge_files: 是否合并所有文件
            final_output_name: 合并后的文件名
        
        返回:
            下载成功的文件列表
        """
        # 生成下载任务
        tasks = self.generate_download_tasks(
            variables, start_date, end_date, area, time_hours, split_by
        )
        
        print(f"\n总共生成 {len(tasks)} 个下载任务")
        print(f"并行下载线程数: {self.max_workers}")
        print(f"开始下载...\n")
        
        successful_files = []
        failed_tasks = []
        
        # 使用线程池并行下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.download_single_task, task): task 
                for task in tasks
            }
            
            # 使用tqdm显示进度
            with tqdm(total=len(tasks), desc="下载进度") as pbar:
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        success, task_id, output_file, error_msg = future.result()
                        
                        if success:
                            successful_files.append(output_file)
                            pbar.set_postfix_str(f"✓ {task_id}")
                        else:
                            failed_tasks.append((task_id, error_msg))
                            pbar.set_postfix_str(f"✗ {task_id}")
                        
                    except Exception as e:
                        task_id = task['task_id']
                        failed_tasks.append((task_id, str(e)))
                        pbar.set_postfix_str(f"✗ {task_id}")
                    
                    pbar.update(1)
        
        # 输出结果统计
        print(f"\n{'='*60}")
        print(f"下载完成!")
        print(f"成功: {len(successful_files)}/{len(tasks)}")
        print(f"失败: {len(failed_tasks)}/{len(tasks)}")
        print(f"{'='*60}\n")
        
        # 写入下载汇总日志
        self._log_verification("\n" + "="*80)
        self._log_verification("下载任务汇总", 'INFO')
        self._log_verification("="*80)
        self._log_verification(f"总任务数: {len(tasks)}", 'INFO')
        self._log_verification(f"成功: {len(successful_files)}", 'SUCCESS')
        self._log_verification(f"失败: {len(failed_tasks)}", 'ERROR' if failed_tasks else 'INFO')
        
        if successful_files:
            self._log_verification("\n成功下载的文件:", 'SUCCESS')
            for f in successful_files:
                self._log_verification(f"  ✅ {Path(f).name}", 'SUCCESS')
        
        if failed_tasks:
            print("失败的任务:")
            self._log_verification("\n失败的任务:", 'ERROR')
            for task_id, error in failed_tasks:
                print(f"  - {task_id}: {error}")
                self._log_verification(f"  ❌ {task_id}: {error}", 'ERROR')
            print()
        
        self._log_verification(f"\n验证日志已保存到: {self.verification_log_file}", 'INFO')
        self._log_verification("="*80 + "\n", 'INFO')
        
        # 合并文件(可选)
        if merge_files and len(successful_files) > 1:
            print("正在合并文件...")
            merged_file = self.merge_netcdf_files(
                successful_files, 
                final_output_name or f"ERA5_Land_merged_{start_date}_{end_date}.nc"
            )
            if merged_file:
                print(f"文件已合并到: {merged_file}\n")
                return [merged_file]
        
        return successful_files
    
    def merge_netcdf_files(self, file_list, output_name):
        """
        合并多个NetCDF文件
        
        参数:
            file_list: 文件路径列表
            output_name: 输出文件名
        
        返回:
            合并后的文件路径
        """
        try:
            output_file = self.output_dir / output_name
            
            # 使用xarray打开并合并文件
            datasets = []
            for file in sorted(file_list):
                ds = xr.open_dataset(file)
                datasets.append(ds)
            
            # 沿时间维度合并
            merged = xr.concat(datasets, dim='time')
            
            # 排序时间维度
            merged = merged.sortby('time')
            
            # 保存合并后的文件
            merged.to_netcdf(output_file)
            
            # 关闭数据集
            for ds in datasets:
                ds.close()
            merged.close()
            
            return str(output_file)
        
        except Exception as e:
            print(f"合并文件失败: {e}")
            traceback.print_exc()
            return None
    
    def retry_failed_downloads(self):
        """重试所有失败的下载"""
        failed_tasks = []
        for task_id, status in self.download_status.items():
            if status.get('status') == 'failed':
                if 'task' in status:
                    failed_tasks.append(status['task'])
        
        if not failed_tasks:
            print("没有失败的下载任务")
            return []
        
        print(f"发现 {len(failed_tasks)} 个失败的任务，开始重试...")
        
        successful_files = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_single_task, task) 
                      for task in failed_tasks]
            
            with tqdm(total=len(failed_tasks), desc="重试进度") as pbar:
                for future in as_completed(futures):
                    success, task_id, output_file, _ = future.result()
                    if success:
                        successful_files.append(output_file)
                    pbar.update(1)
        
        print(f"重试完成，成功: {len(successful_files)}/{len(failed_tasks)}")
        return successful_files
    
    def clean_temp_files(self):
        """清理临时文件"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
                print("临时文件已清理")
        except Exception as e:
            print(f"清理临时文件失败: {e}")


def main():
    """示例使用"""
    
    # 自定义变量名映射（可选）
    # 如果下载的文件中变量名与预期不同，可以在这里添加映射
    custom_mapping = {
        # 'your_cds_variable_name': 'actual_netcdf_variable_name',
        # 例如: 'my_custom_temp': 't2m',
    }
    
    # 创建下载器实例
    downloader = ERA5LandDownloader(
        output_dir='./ERA5_Land_data',  # 数据保存目录
        max_workers=4,                   # 并行下载数量(建议2-4个)
        retry_times=3,                   # 失败重试次数
        retry_delay=10,                  # 重试延迟(秒)
        variable_mapping=custom_mapping  # 自定义变量映射（None使用默认映射）
    )
    
    # 定义下载参数
    variables = [
        '2m_temperature',                # 2米温度
        'surface_solar_radiation_downwards',  # 地表太阳辐射
        # '10m_u_component_of_wind',     # 10米U风速
        # '10m_v_component_of_wind',     # 10米V风速
        # 'total_precipitation',          # 总降水量
        # 更多变量请参考: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land
    ]
    
    # 时间范围
    start_date = '2014-01-01'
    end_date = '2014-01-31'
    
    # 区域范围 [N, W, S, E] - 中国区域示例
    area = [60, 70, 10, 140]  # 北纬60°, 东经70° 到 北纬10°, 东经140°
    # 如果要下载全球数据，设置 area = None
    
    # 小时列表（可选择特定小时，或全部24小时）
    time_hours = [f'{h:02d}:00' for h in range(24)]  # 所有小时
    # time_hours = ['00:00', '06:00', '12:00', '18:00']  # 仅选择特定小时
    
    # 开始下载
    downloaded_files = downloader.download(
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        area=area,
        time_hours=time_hours,
        split_by='month',        # 'month' 或 'year'
        merge_files=False,       # 是否合并所有文件
        final_output_name=None   # 合并后的文件名（如果merge_files=True）
    )
    
    # 输出下载的文件
    print("\n下载的文件:")
    for file in downloaded_files:
        print(f"  - {file}")
    
    # 如果有失败的任务，可以重试
    # downloader.retry_failed_downloads()
    
    # 清理临时文件
    downloader.clean_temp_files()


if __name__ == '__main__':
    main()

