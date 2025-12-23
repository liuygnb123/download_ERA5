"""
CDS API 配置助手

这个脚本帮助您快速配置 CDS API，用于下载 ERA5-Land 数据。

使用方法:
    python setup_cdsapi.py
"""

import os
import sys
from pathlib import Path
import platform


def get_cdsapirc_path():
    """获取 .cdsapirc 文件的路径"""
    if platform.system() == 'Windows':
        # Windows 系统
        home = os.environ.get('USERPROFILE')
        if not home:
            home = os.path.expanduser('~')
        return Path(home) / '.cdsapirc'
    else:
        # Linux/Mac 系统
        return Path.home() / '.cdsapirc'


def check_existing_config():
    """检查是否已存在配置文件"""
    config_path = get_cdsapirc_path()
    
    if config_path.exists():
        print(f"发现已存在的配置文件: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                print("\n当前配置内容:")
                print("-" * 50)
                print(content)
                print("-" * 50)
                
                # 检查配置是否有效
                has_url = 'url:' in content.lower()
                has_key = 'key:' in content.lower()
                
                if has_url and has_key:
                    print("\n✓ 配置文件格式看起来正确")
                    return True, config_path
                else:
                    print("\n✗ 配置文件格式可能不正确")
                    print("  缺少必需的字段: url 或 key")
                    return False, config_path
        except Exception as e:
            print(f"\n✗ 读取配置文件失败: {e}")
            return False, config_path
    else:
        print(f"未找到配置文件: {config_path}")
        return False, config_path


def create_config(config_path, uid, api_key):
    """创建配置文件"""
    config_content = f"""url: https://cds.climate.copernicus.eu/api/v2
key: {uid}:{api_key}
"""
    
    try:
        # 确保父目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Linux/Mac 系统设置权限
        if platform.system() != 'Windows':
            os.chmod(config_path, 0o600)
        
        print(f"\n✓ 配置文件已创建: {config_path}")
        return True
    
    except Exception as e:
        print(f"\n✗ 创建配置文件失败: {e}")
        return False


def test_config():
    """测试配置是否有效"""
    print("\n正在测试 CDS API 连接...")
    
    try:
        import cdsapi
        
        try:
            # 尝试创建客户端
            c = cdsapi.Client()
            print("✓ CDS API 客户端创建成功")
            print("✓ 配置有效，可以开始下载数据")
            return True
        
        except Exception as e:
            print(f"✗ CDS API 连接失败: {e}")
            print("\n可能的原因:")
            print("  1. UID 或 API Key 不正确")
            print("  2. 网络连接问题")
            print("  3. CDS 服务器暂时不可用")
            return False
    
    except ImportError:
        print("✗ 未安装 cdsapi 包")
        print("请运行: pip install cdsapi")
        return False


def show_instructions():
    """显示获取 API Key 的说明"""
    print("\n" + "="*60)
    print("如何获取 CDS API Key")
    print("="*60)
    print("""
1. 访问 CDS 网站并注册账号:
   https://cds.climate.copernicus.eu/

2. 登录后，访问 API Key 页面:
   https://cds.climate.copernicus.eu/api-how-to

3. 在页面中找到您的 UID 和 API Key
   格式如下:
   
   url: https://cds.climate.copernicus.eu/api/v2
   key: 12345:abcdef12-3456-7890-abcd-ef1234567890
        ^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        UID           API Key

4. 复制您的 UID 和 API Key，然后在下面输入
""")
    print("="*60)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("CDS API 配置助手")
    print("="*60)
    print("\n这个工具将帮助您配置 CDS API，用于下载 ERA5-Land 数据。\n")
    
    # 检查现有配置
    has_valid_config, config_path = check_existing_config()
    
    if has_valid_config:
        response = input("\n是否要重新配置? (y/n): ").strip().lower()
        if response != 'y':
            print("\n保持现有配置")
            
            # 测试配置
            response = input("是否测试连接? (y/n): ").strip().lower()
            if response == 'y':
                test_config()
            
            return
    
    # 显示说明
    show_instructions()
    
    # 获取用户输入
    print("\n请输入您的 CDS API 信息:")
    print("(如果还没有账号，请先访问上述网站注册)\n")
    
    uid = input("UID: ").strip()
    api_key = input("API Key: ").strip()
    
    if not uid or not api_key:
        print("\n✗ UID 和 API Key 不能为空")
        return
    
    # 确认
    print("\n" + "-"*60)
    print("您输入的信息:")
    print(f"UID: {uid}")
    print(f"API Key: {api_key}")
    print(f"配置文件路径: {config_path}")
    print("-"*60)
    
    response = input("\n确认创建配置文件? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n已取消")
        return
    
    # 创建配置文件
    if create_config(config_path, uid, api_key):
        # 测试配置
        response = input("\n是否测试连接? (y/n): ").strip().lower()
        if response == 'y':
            if test_config():
                print("\n" + "="*60)
                print("✓ 配置完成！您现在可以使用下载脚本了")
                print("="*60)
                print("\n接下来可以:")
                print("  1. 运行快速开始示例:")
                print("     python quick_start_example.py")
                print("\n  2. 使用配置文件下载:")
                print("     python download_ERA5_Land_with_config.py")
                print("\n  3. 编写自己的脚本:")
                print("     from download_ERA5_Land import ERA5LandDownloader")
            else:
                print("\n配置文件已创建，但连接测试失败")
                print("请检查您的 UID 和 API Key 是否正确")
    else:
        print("\n配置失败，请手动创建配置文件")
        print(f"配置文件路径: {config_path}")
        print("\n文件内容应为:")
        print("-"*50)
        print(f"url: https://cds.climate.copernicus.eu/api/v2")
        print(f"key: {uid}:{api_key}")
        print("-"*50)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出程序")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

