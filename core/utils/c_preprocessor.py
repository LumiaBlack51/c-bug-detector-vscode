#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C预处理器包装器 - 生成带有#line指令的预处理代码
解决行号映射问题的核心组件
"""
import os
import subprocess
import tempfile
from typing import Tuple, Optional

class CPreprocessor:
    """C预处理器包装器"""
    
    def __init__(self):
        self.temp_files = []  # 跟踪临时文件，用于清理
    
    def preprocess_file(self, source_file: str) -> Tuple[str, str]:
        """
        预处理C文件，生成带有#line指令的预处理代码
        
        Args:
            source_file: 源文件路径
            
        Returns:
            Tuple[preprocessed_file, original_file]: 预处理后的文件路径和原始文件路径
        """
        try:
            # 创建临时文件
            temp_fd, temp_file = tempfile.mkstemp(suffix='.i', prefix='preprocessed_')
            os.close(temp_fd)
            self.temp_files.append(temp_file)
            
            # 调用gcc预处理器
            # 关键：不使用-P选项，保留#line指令
            cmd = [
                'gcc', '-E',  # 只预处理，不编译
                '-C',         # 保留注释
                source_file,  # 源文件
                '-o', temp_file  # 输出到临时文件
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"预处理器错误: {result.stderr}")
                # 如果gcc不可用，尝试clang
                cmd[0] = 'clang'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    raise RuntimeError(f"预处理器失败: {result.stderr}")
            
            return temp_file, source_file
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("预处理器超时")
        except FileNotFoundError:
            raise RuntimeError("未找到gcc或clang预处理器")
        except Exception as e:
            raise RuntimeError(f"预处理失败: {e}")
    
    def cleanup(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        self.temp_files.clear()
    
    def __del__(self):
        """析构函数，确保临时文件被清理"""
        self.cleanup()

# 全局预处理器实例
preprocessor = CPreprocessor()
