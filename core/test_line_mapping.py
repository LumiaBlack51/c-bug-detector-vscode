#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试行号映射系统
"""
from utils.c_preprocessor import preprocessor
from utils.enhanced_lexer import EnhancedLexer

def test_line_mapping():
    """测试行号映射系统"""
    try:
        print("=== 测试行号映射系统 ===")
        
        # 测试预处理器
        print("1. 测试预处理器...")
        preprocessed_file, original_file = preprocessor.preprocess_file('../test_simple_malloc.c')
        print(f"   预处理成功: {preprocessed_file}")
        print(f"   原始文件: {original_file}")
        
        # 读取预处理后的代码
        with open(preprocessed_file, 'r', encoding='utf-8') as f:
            preprocessed_code = f.read()
        
        print("\n预处理后的代码:")
        print("-" * 50)
        print(preprocessed_code)
        print("-" * 50)
        
        # 测试词法分析器
        print("\n2. 测试词法分析器...")
        lexer = EnhancedLexer(preprocessed_code)
        tokens = lexer.tokenize()
        
        print(f"   找到 {len(tokens)} 个词法单元")
        print("\n前15个词法单元:")
        for i, token in enumerate(tokens[:15]):
            print(f"   {i+1:2d}. {token.type:12s}: \"{token.value}\" (文件: {token.logical_file}, 行: {token.logical_line})")
        
        # 验证行号映射
        print("\n3. 验证行号映射...")
        malloc_tokens = [t for t in tokens if t.value == 'malloc']
        if malloc_tokens:
            malloc_token = malloc_tokens[0]
            print(f"   malloc 词法单元:")
            print(f"     逻辑文件: {malloc_token.logical_file}")
            print(f"     逻辑行号: {malloc_token.logical_line}")
            print(f"     物理行号: {malloc_token.physical_line}")
            print(f"     列号: {malloc_token.column}")
        
        print("\n[SUCCESS] 行号映射系统测试完成!")
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        preprocessor.cleanup()

if __name__ == "__main__":
    test_line_mapping()
