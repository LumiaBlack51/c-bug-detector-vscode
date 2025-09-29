#!/usr/bin/env python3
"""
C语言Bug检测器 - Nuitka打包脚本
使用Nuitka将检测器打包为独立的exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """主打包函数"""
    print("🚀 开始使用Nuitka打包C语言Bug检测器...")
    
    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 检查main.py是否存在
    main_py = script_dir / "core" / "main.py"
    if not main_py.exists():
        print("❌ 错误: 找不到 core/main.py 文件")
        return 1
    
    # 清理之前的构建
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    if build_dir.exists():
        print("🧹 清理之前的构建文件...")
        try:
            shutil.rmtree(build_dir)
        except PermissionError:
            print("⚠️  无法删除build目录，可能被其他程序占用，继续执行...")
    
    if dist_dir.exists():
        print("🧹 清理之前的输出文件...")
        try:
            shutil.rmtree(dist_dir)
        except PermissionError:
            print("⚠️  无法删除dist目录，可能被其他程序占用，继续执行...")
    
    # 构建Nuitka命令
    nuitka_cmd = [
        "python", "-m", "nuitka",
        "--standalone",  # 独立模式
        "--onefile",     # 单文件模式
        "--output-filename=c-bug-detector.exe",  # 输出文件名
        "--output-dir=dist",  # 输出目录
        "--remove-output",  # 构建后清理临时文件
        "--assume-yes-for-downloads",  # 自动下载依赖
        "--windows-console-mode=force",  # 强制控制台模式
        "--include-package=colorama",  # 包含colorama包
        "--include-package=pycparser",  # 包含pycparser包（如果使用）
        "--windows-icon-from-ico=icon.ico" if (script_dir / "icon.ico").exists() else None,
        str(main_py)
    ]
    
    # 移除None值
    nuitka_cmd = [cmd for cmd in nuitka_cmd if cmd is not None]
    
    print("📦 执行Nuitka打包命令...")
    print(f"命令: {' '.join(nuitka_cmd)}")
    
    try:
        # 执行打包
        result = subprocess.run(nuitka_cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功!")
        
        # 检查输出文件
        exe_file = dist_dir / "c-bug-detector.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print(f"📁 输出文件: {exe_file}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            
            # 创建使用说明
            create_usage_guide(dist_dir)
            
            print("\n🎉 打包完成! 可以发送给同行进行测试了。")
            return 0
        else:
            print("❌ 错误: 找不到生成的exe文件")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return 1
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return 1

def create_usage_guide(dist_dir):
    """创建使用说明文档"""
    usage_content = """# C语言Bug检测器 - 使用说明

## 简介
这是一个C语言Bug检测器，能够检测常见的C语言编程错误，包括：
- printf/scanf格式字符串问题
- 变量未初始化使用
- 内存安全问题
- 数值控制流问题

## 使用方法

### 1. 检测单个C文件
```
c-bug-detector.exe path/to/your/file.c
```

### 2. 检测目录下所有C文件
```
c-bug-detector.exe --batch path/to/directory
```

### 3. 生成报告文件
```
c-bug-detector.exe path/to/file.c -o report.txt
```

### 4. 生成JSON格式报告
```
c-bug-detector.exe path/to/file.c -f json -o report.json
```

### 5. 禁用特定检测模块
```
c-bug-detector.exe path/to/file.c --disable memory_safety variable_state
```

### 6. 查看所有可用模块
```
c-bug-detector.exe --list-modules
```

## 检测模块说明

- **标准库使用助手**: 检测printf/scanf格式字符串问题
- **变量状态监察官**: 检测变量未初始化使用
- **内存安全卫士**: 检测内存泄漏、野指针等问题
- **数值与控制流分析器**: 检测数值和控制流问题

## 示例

检测一个C文件：
```
c-bug-detector.exe test.c
```

检测结果会显示在控制台中，包括：
- 问题位置（行号）
- 问题类型
- 详细描述
- 修复建议

## 注意事项

1. 确保输入的C文件语法正确
2. 检测器会分析代码的静态结构，不会执行代码
3. 某些复杂的动态分析可能无法完全覆盖
4. 建议结合编译器警告一起使用

## 技术支持

如有问题，请联系开发团队。
"""
    
    usage_file = dist_dir / "使用说明.txt"
    with open(usage_file, 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print(f"📖 已创建使用说明: {usage_file}")

if __name__ == "__main__":
    sys.exit(main())
