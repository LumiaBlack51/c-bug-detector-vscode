#!/usr/bin/env python3
"""
C语言Bug检测器安装脚本
自动安装依赖包并配置环境
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                     check=True, capture_output=True)
        
        # 安装依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                     check=True, capture_output=True)
        
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        print("请手动运行: pip install -r requirements.txt")
        return False


def create_executable_script():
    """创建可执行脚本"""
    print("📝 创建可执行脚本...")
    
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    
    # 创建启动脚本
    if platform.system() == "Windows":
        # Windows批处理文件
        script_content = f"""@echo off
python "{current_dir}\\main.py" %*
"""
        script_path = current_dir / "cbug-detector.bat"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Windows批处理脚本已创建: {script_path}")
        
    else:
        # Unix shell脚本
        script_content = f"""#!/bin/bash
python3 "{current_dir}/main.py" "$@"
"""
        script_path = current_dir / "cbug-detector.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        print(f"✅ Unix shell脚本已创建: {script_path}")
    
    return script_path


def test_installation():
    """测试安装"""
    print("🧪 测试安装...")
    
    try:
        # 测试导入模块
        from modules.memory_safety import MemorySafetyModule
        from modules.variable_state import VariableStateModule
        from modules.standard_library import StandardLibraryModule
        from modules.numeric_control_flow import NumericControlFlowModule
        from utils.error_reporter import ErrorReporter
        from utils.code_parser import CCodeParser
        
        print("✅ 模块导入测试通过")
        
        # 测试基本功能
        detector = MemorySafetyModule()
        print(f"✅ 模块功能测试通过: {detector.get_module_name()}")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入测试失败: {e}")
        return False


def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎉 C语言Bug检测器安装完成！")
    print("="*60)
    print("\n📖 使用方法:")
    print("1. 分析单个文件:")
    print("   python main.py <文件路径>")
    print("   python main.py tests/test_memory_safety.c")
    print("\n2. 批量分析目录:")
    print("   python main.py --batch <目录路径>")
    print("   python main.py --batch tests/")
    print("\n3. 指定输出格式:")
    print("   python main.py <文件路径> -f json -o report.json")
    print("\n4. 启用/禁用特定模块:")
    print("   python main.py <文件路径> --enable memory_safety")
    print("   python main.py <文件路径> --disable standard_library")
    print("\n5. 查看所有可用模块:")
    print("   python main.py --list-modules")
    print("\n📋 可用模块:")
    print("   - memory_safety: 内存安全卫士")
    print("   - variable_state: 变量状态监察官")
    print("   - standard_library: 标准库使用助手")
    print("   - numeric_control_flow: 数值与控制流分析器")
    print("\n💡 提示:")
    print("   - 所有错误报告都包含具体的行号和修复建议")
    print("   - 支持JSON格式输出，便于集成到其他工具")
    print("   - 可以单独启用或禁用任何模块")
    print("\n🔗 项目地址: https://github.com/your-username/c-bug-detector")
    print("="*60)


def main():
    """主安装函数"""
    print("🚀 C语言Bug检测器安装程序")
    print("="*40)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 创建可执行脚本
    script_path = create_executable_script()
    
    # 测试安装
    if not test_installation():
        print("⚠️  安装可能有问题，但基本功能应该可用")
    
    # 显示使用说明
    show_usage()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 安装完成！")
            sys.exit(0)
        else:
            print("\n❌ 安装失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        sys.exit(1)
