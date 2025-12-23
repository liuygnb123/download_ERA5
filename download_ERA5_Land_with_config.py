"""
使用配置文件下载 ERA5-Land 数据的脚本

使用方法:
    1. 编辑 download_config.json 文件，设置下载参数
    2. 运行: python download_ERA5_Land_with_config.py
"""

import json
from pathlib import Path
from download_ERA5_Land import ERA5LandDownloader


def load_config(config_file='download_config.json'):
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def main():
    """主函数"""
    
    # 加载配置
    config_file = 'download_config.json'
    
    if not Path(config_file).exists():
        print(f"错误: 配置文件 {config_file} 不存在!")
        print("请先创建配置文件，可以参考 download_config.json 示例")
        return
    
    print("正在加载配置文件...")
    config = load_config(config_file)
    
    # 创建下载器
    settings = config.get('downloader_settings', {})
    downloader = ERA5LandDownloader(
        output_dir=settings.get('output_dir', './ERA5_Land_data'),
        max_workers=settings.get('max_workers', 4),
        retry_times=settings.get('retry_times', 3),
        retry_delay=settings.get('retry_delay', 10)
    )
    
    # 获取下载任务
    tasks = config.get('download_tasks', [])
    enabled_tasks = [task for task in tasks if task.get('enabled', True)]
    
    if not enabled_tasks:
        print("警告: 没有启用的下载任务!")
        print("请在配置文件中将任务的 'enabled' 设置为 true")
        return
    
    print(f"\n找到 {len(enabled_tasks)} 个启用的下载任务")
    print("="*60)
    
    # 执行每个任务
    all_downloaded_files = []
    
    for idx, task in enumerate(enabled_tasks, 1):
        task_name = task.get('task_name', f'任务{idx}')
        
        print(f"\n[{idx}/{len(enabled_tasks)}] 开始执行任务: {task_name}")
        print("-"*60)
        
        # 提取任务参数
        variables = task.get('variables', [])
        start_date = task.get('start_date')
        end_date = task.get('end_date')
        area = task.get('area')
        time_hours = task.get('time_hours')
        split_by = task.get('split_by', 'month')
        merge_files = task.get('merge_files', False)
        final_output_name = task.get('final_output_name')
        
        # 验证必需参数
        if not variables:
            print(f"跳过任务 '{task_name}': 缺少变量列表")
            continue
        if not start_date or not end_date:
            print(f"跳过任务 '{task_name}': 缺少日期范围")
            continue
        
        # 显示任务信息
        print(f"变量: {', '.join(variables)}")
        print(f"时间范围: {start_date} 至 {end_date}")
        if area:
            print(f"区域: {area}")
        else:
            print("区域: 全球")
        if time_hours:
            print(f"小时: {', '.join(time_hours)}")
        else:
            print("小时: 所有24小时")
        print(f"分割方式: {split_by}")
        print(f"合并文件: {merge_files}")
        
        try:
            # 执行下载
            downloaded_files = downloader.download(
                variables=variables,
                start_date=start_date,
                end_date=end_date,
                area=area,
                time_hours=time_hours,
                split_by=split_by,
                merge_files=merge_files,
                final_output_name=final_output_name
            )
            
            all_downloaded_files.extend(downloaded_files)
            print(f"✓ 任务 '{task_name}' 完成")
            
        except Exception as e:
            print(f"✗ 任务 '{task_name}' 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 清理临时文件
    downloader.clean_temp_files()
    
    # 输出总结
    print("\n" + "="*60)
    print("所有任务执行完毕!")
    print(f"共下载 {len(all_downloaded_files)} 个文件")
    print("="*60)
    
    if all_downloaded_files:
        print("\n下载的文件列表:")
        for file in all_downloaded_files:
            print(f"  - {file}")


if __name__ == '__main__':
    main()

