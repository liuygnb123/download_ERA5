"""
ERA5-Land 下载管理工具

功能：
    1. 查看下载状态
    2. 重试失败的下载
    3. 清理临时文件
    4. 验证已下载的文件
    5. 查看存储空间使用情况
"""

import json
import os
from pathlib import Path
from datetime import datetime
import xarray as xr
from download_ERA5_Land import ERA5LandDownloader


class DownloadManager:
    """下载管理器"""
    
    def __init__(self, output_dir='./ERA5_Land_data'):
        """初始化管理器"""
        self.output_dir = Path(output_dir)
        self.downloader = ERA5LandDownloader(output_dir=str(self.output_dir))
    
    def show_status(self):
        """显示下载状态"""
        print("\n" + "="*60)
        print("下载状态统计")
        print("="*60)
        
        status = self.downloader.download_status
        
        if not status:
            print("还没有下载记录")
            return
        
        completed = sum(1 for s in status.values() if s.get('status') == 'completed')
        failed = sum(1 for s in status.values() if s.get('status') == 'failed')
        total = len(status)
        
        print(f"\n总任务数: {total}")
        print(f"已完成: {completed} ({completed/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        
        # 显示详细信息
        if completed > 0:
            print("\n✓ 已完成的任务:")
            for task_id, info in status.items():
                if info.get('status') == 'completed':
                    file = info.get('file', 'Unknown')
                    timestamp = info.get('timestamp', 'Unknown')
                    variables = info.get('variables', [])
                    print(f"  [{task_id}] {', '.join(variables)}")
                    print(f"    文件: {file}")
                    print(f"    时间: {timestamp}")
        
        if failed > 0:
            print("\n✗ 失败的任务:")
            for task_id, info in status.items():
                if info.get('status') == 'failed':
                    error = info.get('error', 'Unknown error')
                    timestamp = info.get('timestamp', 'Unknown')
                    print(f"  [{task_id}]")
                    print(f"    错误: {error}")
                    print(f"    时间: {timestamp}")
        
        print()
    
    def retry_failed(self):
        """重试失败的下载"""
        print("\n" + "="*60)
        print("重试失败的下载")
        print("="*60)
        
        failed_count = sum(1 for s in self.downloader.download_status.values() 
                          if s.get('status') == 'failed')
        
        if failed_count == 0:
            print("\n没有失败的下载任务")
            return
        
        print(f"\n发现 {failed_count} 个失败的任务")
        response = input("是否重试? (y/n): ")
        
        if response.lower() == 'y':
            print("\n开始重试...")
            files = self.downloader.retry_failed_downloads()
            print(f"\n重试完成，成功 {len(files)} 个任务")
        else:
            print("已取消")
    
    def verify_files(self):
        """验证已下载的文件"""
        print("\n" + "="*60)
        print("验证已下载的文件")
        print("="*60)
        
        completed_tasks = {
            task_id: info 
            for task_id, info in self.downloader.download_status.items()
            if info.get('status') == 'completed'
        }
        
        if not completed_tasks:
            print("\n没有已完成的下载任务")
            return
        
        print(f"\n正在验证 {len(completed_tasks)} 个文件...\n")
        
        valid_count = 0
        invalid_files = []
        
        for task_id, info in completed_tasks.items():
            file_path = info.get('file')
            variables = info.get('variables', [])
            
            if not file_path or not os.path.exists(file_path):
                print(f"✗ [{task_id}] 文件不存在: {file_path}")
                invalid_files.append((task_id, file_path, "文件不存在"))
                continue
            
            try:
                # 尝试打开文件
                ds = xr.open_dataset(file_path)
                
                # 检查变量
                missing_vars = []
                for var in variables:
                    if var not in ds.variables and var not in ds.data_vars:
                        missing_vars.append(var)
                
                if missing_vars:
                    print(f"✗ [{task_id}] 缺少变量: {', '.join(missing_vars)}")
                    invalid_files.append((task_id, file_path, f"缺少变量: {missing_vars}"))
                else:
                    print(f"✓ [{task_id}] 验证通过")
                    valid_count += 1
                
                ds.close()
                
            except Exception as e:
                print(f"✗ [{task_id}] 验证失败: {str(e)}")
                invalid_files.append((task_id, file_path, str(e)))
        
        # 输出统计
        print("\n" + "-"*60)
        print(f"验证完成: {valid_count}/{len(completed_tasks)} 个文件有效")
        
        if invalid_files:
            print(f"\n发现 {len(invalid_files)} 个无效文件")
            response = input("是否将这些任务标记为失败并重新下载? (y/n): ")
            
            if response.lower() == 'y':
                for task_id, file_path, error in invalid_files:
                    # 标记为失败
                    self.downloader.download_status[task_id]['status'] = 'failed'
                    self.downloader.download_status[task_id]['error'] = error
                    # 删除文件
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"已删除: {file_path}")
                        except:
                            print(f"删除失败: {file_path}")
                
                self.downloader.save_status()
                print("\n已标记为失败，可以使用 '重试失败的下载' 功能重新下载")
        
        print()
    
    def show_disk_usage(self):
        """显示磁盘空间使用情况"""
        print("\n" + "="*60)
        print("存储空间使用情况")
        print("="*60)
        
        if not self.output_dir.exists():
            print("\n数据目录不存在")
            return
        
        # 统计文件大小
        total_size = 0
        file_count = 0
        
        for file in self.output_dir.rglob('*.nc'):
            try:
                size = file.stat().st_size
                total_size += size
                file_count += 1
            except:
                pass
        
        # 格式化大小
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        
        print(f"\n数据目录: {self.output_dir}")
        print(f"文件数量: {file_count}")
        print(f"总大小: {format_size(total_size)}")
        
        if file_count > 0:
            print(f"平均文件大小: {format_size(total_size / file_count)}")
        
        # 列出最大的文件
        print("\n最大的10个文件:")
        files_with_size = []
        for file in self.output_dir.rglob('*.nc'):
            try:
                size = file.stat().st_size
                files_with_size.append((file, size))
            except:
                pass
        
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        
        for i, (file, size) in enumerate(files_with_size[:10], 1):
            rel_path = file.relative_to(self.output_dir)
            print(f"  {i}. {format_size(size):>12} - {rel_path}")
        
        print()
    
    def clean_temp_files(self):
        """清理临时文件"""
        print("\n" + "="*60)
        print("清理临时文件")
        print("="*60)
        
        temp_dir = self.output_dir / 'temp'
        
        if not temp_dir.exists():
            print("\n临时目录不存在")
            return
        
        # 统计临时文件
        temp_files = list(temp_dir.rglob('*'))
        temp_files = [f for f in temp_files if f.is_file()]
        
        if not temp_files:
            print("\n没有临时文件")
            return
        
        total_size = sum(f.stat().st_size for f in temp_files)
        
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} TB"
        
        print(f"\n发现 {len(temp_files)} 个临时文件")
        print(f"总大小: {format_size(total_size)}")
        
        response = input("是否删除? (y/n): ")
        
        if response.lower() == 'y':
            self.downloader.clean_temp_files()
            print("清理完成")
        else:
            print("已取消")
    
    def export_file_list(self, output_file='downloaded_files.txt'):
        """导出已下载的文件列表"""
        print("\n" + "="*60)
        print("导出文件列表")
        print("="*60)
        
        completed_tasks = {
            task_id: info 
            for task_id, info in self.downloader.download_status.items()
            if info.get('status') == 'completed'
        }
        
        if not completed_tasks:
            print("\n没有已完成的下载任务")
            return
        
        output_path = self.output_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ERA5-Land 已下载文件列表\n")
            f.write(f"生成时间: {datetime.now().isoformat()}\n")
            f.write("="*60 + "\n\n")
            
            for task_id, info in completed_tasks.items():
                file_path = info.get('file', 'Unknown')
                timestamp = info.get('timestamp', 'Unknown')
                variables = info.get('variables', [])
                task = info.get('task', {})
                
                f.write(f"任务ID: {task_id}\n")
                f.write(f"变量: {', '.join(variables)}\n")
                f.write(f"文件: {file_path}\n")
                f.write(f"时间: {timestamp}\n")
                
                if task:
                    f.write(f"时间范围: {task.get('year')}-{task.get('month', 'all')}\n")
                    if task.get('area'):
                        f.write(f"区域: {task.get('area')}\n")
                
                f.write("-"*60 + "\n\n")
        
        print(f"\n文件列表已导出到: {output_path}")
        print()


def main():
    """主菜单"""
    print("\n" + "="*60)
    print("ERA5-Land 下载管理工具")
    print("="*60)
    
    # 获取数据目录
    default_dir = './ERA5_Land_data'
    data_dir = input(f"\n数据目录 (默认: {default_dir}): ").strip()
    if not data_dir:
        data_dir = default_dir
    
    manager = DownloadManager(output_dir=data_dir)
    
    while True:
        print("\n" + "="*60)
        print("请选择功能:")
        print("1. 查看下载状态")
        print("2. 重试失败的下载")
        print("3. 验证已下载的文件")
        print("4. 查看存储空间使用情况")
        print("5. 清理临时文件")
        print("6. 导出文件列表")
        print("0. 退出")
        print("="*60)
        
        try:
            choice = input("\n请输入选项 (0-6): ").strip()
            
            if choice == '0':
                print("\n退出程序")
                break
            elif choice == '1':
                manager.show_status()
            elif choice == '2':
                manager.retry_failed()
            elif choice == '3':
                manager.verify_files()
            elif choice == '4':
                manager.show_disk_usage()
            elif choice == '5':
                manager.clean_temp_files()
            elif choice == '6':
                manager.export_file_list()
            else:
                print("\n无效选项，请重新输入")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            input("\n按回车键继续...")


if __name__ == '__main__':
    main()

