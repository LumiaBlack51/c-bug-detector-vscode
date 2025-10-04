"""
C代码预处理器 - 为pycparser准备代码
pycparser需要预处理后的C代码，因为它不支持预处理指令
"""
import re
import os
import subprocess
import tempfile
from typing import Dict, List, Tuple, Optional


class CPreprocessor:
    """C代码预处理器 - 为pycparser准备代码"""
    
    def __init__(self):
        self.fake_libc_path = self._get_fake_libc_path()
        self.line_mapping: Dict[int, int] = {}  # 预处理后行号 -> 原始行号
    
    def _get_fake_libc_path(self) -> Optional[str]:
        """获取pycparser的fake_libc_include路径"""
        try:
            import pycparser
            pycparser_dir = os.path.dirname(pycparser.__file__)
            fake_libc_path = os.path.join(pycparser_dir, 'utils', 'fake_libc_include')
            if os.path.exists(fake_libc_path):
                return fake_libc_path
        except Exception:
            pass
        return None
    
    def preprocess_file(self, file_path: str, use_gcc: bool = True) -> Tuple[str, Dict[int, int]]:
        """
        预处理C文件，返回预处理后的代码和行号映射
        
        Args:
            file_path: C源文件路径
            use_gcc: 是否尝试使用GCC预处理器（如果失败则使用简单预处理）
        
        Returns:
            (预处理后的代码, 行号映射字典)
        """
        # 尝试使用GCC预处理
        if use_gcc:
            preprocessed_code, line_mapping = self._preprocess_with_gcc(file_path)
            if preprocessed_code:
                return preprocessed_code, line_mapping
        
        # 回退到简单预处理
        return self._simple_preprocess(file_path)
    
    def _preprocess_with_gcc(self, file_path: str) -> Tuple[Optional[str], Dict[int, int]]:
        """使用GCC预处理器处理文件"""
        try:
            # 构建GCC命令
            cmd = ['gcc', '-E', '-P']  # -E 只预处理, -P 不生成#line指令
            
            # 如果有fake_libc_include，添加到include路径
            if self.fake_libc_path:
                cmd.extend(['-I', self.fake_libc_path])
            
            cmd.append(file_path)
            
            # 执行预处理
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if result.returncode == 0:
                # 创建行号映射（简化版本，假设预处理后的代码行号基本对应）
                preprocessed_code = result.stdout
                lines = preprocessed_code.split('\n')
                line_mapping = {i+1: i+1 for i in range(len(lines))}
                return preprocessed_code, line_mapping
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"GCC预处理失败: {e}")
        
        return None, {}
    
    def _simple_preprocess(self, file_path: str) -> Tuple[str, Dict[int, int]]:
        """
        简单预处理 - 移除注释和预处理指令
        这是pycparser能够处理的最小化预处理
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_code = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return "", {}
        
        # 1. 移除所有注释
        code_without_comments = self._remove_comments(original_code)
        
        # 2. 移除或简化预处理指令
        code_processed, line_mapping = self._process_directives(code_without_comments)
        
        # 3. 展开简单的宏（可选）
        # code_processed = self._expand_simple_macros(code_processed)
        
        return code_processed, line_mapping
    
    def _remove_comments(self, code: str) -> str:
        """移除C代码中的注释"""
        # 移除单行注释 //
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # 移除多行注释 /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        return code
    
    def _process_directives(self, code: str) -> Tuple[str, Dict[int, int]]:
        """
        处理预处理指令
        - 移除#include, #define等（pycparser不需要）
        - 保留#pragma等可能影响语义的指令
        - 建立行号映射
        """
        lines = code.split('\n')
        processed_lines = []
        line_mapping = {}
        processed_line_num = 1
        
        for original_line_num, line in enumerate(lines, 1):
            # 检查是否是预处理指令
            if line.strip().startswith('#'):
                # 移除#include, #define, #ifndef, #ifdef等
                if any(directive in line for directive in ['#include', '#define', '#ifndef', '#ifdef', '#endif', '#undef', '#if', '#else', '#elif']):
                    # 用空行替代，保持行号大致对应
                    processed_lines.append('')
                    line_mapping[processed_line_num] = original_line_num
                    processed_line_num += 1
                    continue
            
            # 保留普通代码行
            processed_lines.append(line)
            line_mapping[processed_line_num] = original_line_num
            processed_line_num += 1
        
        processed_code = '\n'.join(processed_lines)
        return processed_code, line_mapping
    
    def preprocess_for_pycparser(self, file_path: str) -> Tuple[str, Dict[int, int]]:
        """
        为pycparser预处理C文件
        返回处理后的代码和行号映射
        
        注意：pycparser不需要展开系统头文件，只需要移除注释和预处理指令
        """
        # 直接使用简单预处理（更适合pycparser）
        # pycparser的fake_libc_include会在解析时自动处理标准库类型
        return self._simple_preprocess(file_path)
    
    def create_temp_preprocessed_file(self, file_path: str) -> Tuple[str, Dict[int, int]]:
        """
        创建预处理后的临时文件
        返回临时文件路径和行号映射
        """
        preprocessed_code, line_mapping = self.preprocess_for_pycparser(file_path)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write(preprocessed_code)
            temp_file_path = f.name
        
        return temp_file_path, line_mapping
    
    def cleanup(self):
        """清理资源（为了兼容性保留）"""
        pass


# 全局预处理器实例
_preprocessor = None

def get_preprocessor() -> CPreprocessor:
    """获取预处理器单例"""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = CPreprocessor()
    return _preprocessor

# 创建全局单例（为了兼容性）
preprocessor = get_preprocessor()

def preprocess_for_pycparser(file_path: str) -> Tuple[str, Dict[int, int]]:
    """
    便捷函数：为pycparser预处理C文件
    
    Args:
        file_path: C源文件路径
    
    Returns:
        (预处理后的代码, 行号映射字典)
    """
    return preprocessor.preprocess_for_pycparser(file_path)
