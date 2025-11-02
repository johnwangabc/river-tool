# -*- coding: utf-8 -*-
"""
EXE打包辅助脚本
自动将config_exe.py重命名为config.py，然后打包
"""

import os
import shutil
import subprocess
import sys

def build_exe():
    """打包EXE"""
    print("=" * 60)
    print("河流数据统计工具 - EXE打包工具")
    print("=" * 60)

    # 1. 备份原config.py
    if os.path.exists('config.py'):
        print("\n[1/5] 备份原config.py...")
        shutil.copy('config.py', 'config.py.backup')
        print("✓ 已备份为 config.py.backup")

    # 2. 使用config_exe.py
    print("\n[2/5] 使用EXE版配置...")
    shutil.copy('config_exe.py', 'config.py')
    print("✓ 已将config_exe.py复制为config.py")

    # 3. 检查依赖
    print("\n[3/5] 检查PyInstaller...")
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ 未安装PyInstaller")
        print("  正在安装PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✓ PyInstaller安装完成")

    # 4. 打包
    print("\n[4/5] 开始打包EXE...")
    print("  这可能需要几分钟时间，请耐心等待...")

    try:
        result = subprocess.run(
            ['pyinstaller', '巡河宝统计工具.spec'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print("✓ 打包成功！")
        else:
            print("✗ 打包失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ 打包出错: {e}")
        return False

    # 5. 恢复config.py
    print("\n[5/5] 恢复原配置...")
    if os.path.exists('config.py.backup'):
        shutil.move('config.py.backup', 'config.py')
        print("✓ 已恢复config.py")

    # 6. 复制user_config.ini到dist目录
    if os.path.exists('dist/巡河宝统计工具.exe'):
        print("\n[额外] 复制配置文件到dist目录...")
        shutil.copy('user_config.ini', 'dist/user_config.ini')
        print("✓ 已复制user_config.ini到dist目录")

    print("\n" + "=" * 60)
    print("✓ 打包完成！")
    print("=" * 60)
    print("\n生成的文件位置:")
    print(f"  EXE文件: dist\\巡河宝统计工具.exe")
    print(f"  配置文件: dist\\user_config.ini")
    print("\n使用说明:")
    print("  1. 将 dist 文件夹中的所有文件复制到目标位置")
    print("  2. 编辑 user_config.ini 填入正确的token")
    print("  3. 双击运行 巡河宝统计工具.exe")
    print()

    return True

if __name__ == '__main__':
    try:
        success = build_exe()
        if success:
            print("按回车键退出...")
            input()
    except Exception as e:
        print(f"\n发生错误: {e}")
        print("\n按回车键退出...")
        input()
        sys.exit(1)
