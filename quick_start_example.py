"""
ERA5-Land 数据下载快速开始示例

这个脚本提供了几个常用的下载场景示例，可以直接运行或根据需要修改。

使用前请确保：
1. 已安装依赖: pip install cdsapi xarray netCDF4 pandas tqdm
2. 已配置 CDS API Key (参见 ERA5_Land_下载说明.md)
"""

from download_ERA5_Land import ERA5LandDownloader


def example_1_china_temperature_2014():
    """
    示例1: 下载中国区域2014年的温度和太阳辐射数据
    - 区域: 中国
    - 时间: 2014年1月
    - 变量: 2米温度, 地表太阳辐射
    - 所有24小时数据
    """
    print("\n" + "="*60)
    print("示例1: 下载中国区域2014年1月的温度和太阳辐射数据")
    print("="*60)
    
    downloader = ERA5LandDownloader(
        output_dir='./data/example1_china_2014',
        max_workers=3,
        retry_times=3
    )
    
    files = downloader.download(
        variables=[
            '2m_temperature',
            'surface_solar_radiation_downwards'
        ],
        start_date='2014-01-01',
        end_date='2014-01-31',
        area=[60, 70, 10, 140],  # 中国区域: [北, 西, 南, 东]
        time_hours=None,          # 所有24小时
        split_by='month'
    )
    
    print(f"\n✓ 下载完成! 共 {len(files)} 个文件")
    return files


def example_2_specific_hours():
    """
    示例2: 下载特定小时的数据
    - 区域: 华北地区
    - 时间: 2020年1月
    - 变量: 2米温度
    - 仅选择 00:00, 06:00, 12:00, 18:00 四个时刻
    """
    print("\n" + "="*60)
    print("示例2: 下载华北地区特定小时的温度数据")
    print("="*60)
    
    downloader = ERA5LandDownloader(
        output_dir='./data/example2_specific_hours',
        max_workers=2
    )
    
    files = downloader.download(
        variables=['2m_temperature'],
        start_date='2020-01-01',
        end_date='2020-01-31',
        area=[42, 110, 35, 122],  # 华北地区
        time_hours=['00:00', '06:00', '12:00', '18:00'],  # 仅4个时刻
        split_by='month'
    )
    
    print(f"\n✓ 下载完成! 共 {len(files)} 个文件")
    return files


def example_3_multiple_variables():
    """
    示例3: 下载多个变量
    - 区域: 华东地区
    - 时间: 2015年1-3月
    - 变量: 温度, 风速(U和V分量), 降水
    - 按月分割
    """
    print("\n" + "="*60)
    print("示例3: 下载华东地区多个气象变量")
    print("="*60)
    
    downloader = ERA5LandDownloader(
        output_dir='./data/example3_multiple_vars',
        max_workers=4
    )
    
    files = downloader.download(
        variables=[
            '2m_temperature',
            '10m_u_component_of_wind',
            '10m_v_component_of_wind',
            'total_precipitation'
        ],
        start_date='2015-01-01',
        end_date='2015-03-31',
        area=[35, 116, 25, 125],  # 华东地区
        split_by='month'
    )
    
    print(f"\n✓ 下载完成! 共 {len(files)} 个文件")
    return files


def example_4_merge_files():
    """
    示例4: 下载并合并文件
    - 区域: 小范围区域
    - 时间: 2019年1-2月
    - 变量: 2米温度
    - 合并为单个文件
    """
    print("\n" + "="*60)
    print("示例4: 下载数据并合并为单个文件")
    print("="*60)
    
    downloader = ERA5LandDownloader(
        output_dir='./data/example4_merged',
        max_workers=2
    )
    
    files = downloader.download(
        variables=['2m_temperature'],
        start_date='2019-01-01',
        end_date='2019-02-28',
        area=[40, 100, 30, 120],
        split_by='month',
        merge_files=True,  # 合并文件
        final_output_name='ERA5_Land_temperature_2019Q1_merged.nc'
    )
    
    print(f"\n✓ 下载完成! 合并后文件: {files[0] if files else 'None'}")
    return files


def example_5_long_time_series():
    """
    示例5: 下载长时间序列数据
    - 区域: 中国
    - 时间: 2010-2014年 (5年)
    - 变量: 地表太阳辐射
    - 按年分割
    """
    print("\n" + "="*60)
    print("示例5: 下载长时间序列数据(5年)")
    print("="*60)
    print("警告: 这个任务将下载大量数据，可能需要较长时间!")
    
    # 询问用户确认
    response = input("是否继续? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return []
    
    downloader = ERA5LandDownloader(
        output_dir='./data/example5_long_series',
        max_workers=3,
        retry_times=5
    )
    
    files = downloader.download(
        variables=['surface_solar_radiation_downwards'],
        start_date='2010-01-01',
        end_date='2014-12-31',
        area=[60, 70, 10, 140],  # 中国区域
        split_by='year',  # 按年分割
        time_hours=['06:00', '12:00', '18:00']  # 仅白天时刻
    )
    
    print(f"\n✓ 下载完成! 共 {len(files)} 个文件")
    return files


def example_6_read_downloaded_data():
    """
    示例6: 读取下载的数据
    演示如何使用 xarray 读取和处理下载的 NetCDF 文件
    """
    print("\n" + "="*60)
    print("示例6: 读取和处理下载的数据")
    print("="*60)
    
    try:
        import xarray as xr
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 假设已经有下载好的文件
        # 这里只是演示代码，实际需要替换为真实的文件路径
        print("\n这是一个示例代码，展示如何读取ERA5-Land数据:")
        print("""
import xarray as xr
import matplotlib.pyplot as plt

# 1. 打开数据文件
ds = xr.open_dataset('ERA5_Land_2m_temperature_201401.nc')

# 2. 查看数据结构
print(ds)
print(ds.data_vars)

# 3. 读取温度变量
temperature = ds['t2m']  # 2米温度
print(temperature)

# 4. 选择特定时间和位置
# 选择2014年1月15日12:00的数据
temp_time = temperature.sel(time='2014-01-15 12:00')

# 选择北京附近的数据 (纬度40°N, 经度116°E)
temp_point = temperature.sel(
    time='2014-01-15 12:00',
    latitude=40.0,
    longitude=116.0,
    method='nearest'
)
print(f"北京温度: {temp_point.values} K")
print(f"北京温度: {temp_point.values - 273.15:.2f} °C")

# 5. 计算统计量
temp_mean = temperature.mean(dim='time')  # 时间平均
temp_max = temperature.max(dim='time')    # 最大值
temp_min = temperature.min(dim='time')    # 最小值

# 6. 绘制地图
fig, ax = plt.subplots(figsize=(10, 8))
temp_time.plot(ax=ax, cmap='coolwarm')
plt.title('2014-01-15 12:00 Temperature')
plt.savefig('temperature_map.png')
plt.close()

# 7. 绘制时间序列
# 提取某个点的时间序列
temp_series = temperature.sel(
    latitude=40.0,
    longitude=116.0,
    method='nearest'
)
fig, ax = plt.subplots(figsize=(12, 5))
temp_series.plot(ax=ax)
plt.title('Temperature Time Series at Beijing')
plt.savefig('temperature_timeseries.png')
plt.close()

# 8. 关闭数据集
ds.close()
        """)
        
    except ImportError:
        print("需要安装 xarray 和 matplotlib 来运行数据读取示例")
        print("安装命令: pip install xarray matplotlib")


def main():
    """主菜单"""
    
    print("\n" + "="*60)
    print("ERA5-Land 数据下载快速开始示例")
    print("="*60)
    print("\n请选择要运行的示例:")
    print("1. 下载中国区域2014年1月的温度和太阳辐射数据")
    print("2. 下载华北地区特定小时的温度数据")
    print("3. 下载华东地区多个气象变量")
    print("4. 下载数据并合并为单个文件")
    print("5. 下载长时间序列数据(5年，需要较长时间)")
    print("6. 查看如何读取和处理下载的数据")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选项 (0-6): ").strip()
            
            if choice == '0':
                print("退出程序")
                break
            elif choice == '1':
                example_1_china_temperature_2014()
            elif choice == '2':
                example_2_specific_hours()
            elif choice == '3':
                example_3_multiple_variables()
            elif choice == '4':
                example_4_merge_files()
            elif choice == '5':
                example_5_long_time_series()
            elif choice == '6':
                example_6_read_downloaded_data()
            else:
                print("无效选项，请重新输入")
            
            # 询问是否继续
            cont = input("\n是否运行其他示例? (y/n): ").strip().lower()
            if cont != 'y':
                print("退出程序")
                break
                
        except KeyboardInterrupt:
            print("\n\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()

