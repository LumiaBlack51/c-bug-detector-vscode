import sys
sys.path.append('.')
from modules.standard_library import StandardLibraryModule
import re

module = StandardLibraryModule()

# 测试printf参数解析
test_line = 'printf("Point %d: (%d, %d)\\n", i, points[i].x, points[i].y);'
print('测试行:', test_line)

# 提取printf参数
printf_match = re.search(r'printf\s*\(([^)]+)\)', test_line)
if printf_match:
    params_content = printf_match.group(1).strip()
    print('参数内容:', params_content)
    
    # 解析参数
    format_string, actual_params = module._parse_printf_arguments(params_content)
    print('格式字符串:', format_string)
    print('实际参数:', actual_params)
    print('参数数量:', len(actual_params))
    
    # 计算格式说明符
    if format_string:
        format_specifiers = re.findall(r'%[+-]?[0-9]*\.?[0-9]*[hlL]?[diouxXeEfFgGaAcspn]', format_string)
        format_specifiers = [spec for spec in format_specifiers if spec != '%%']
        print('格式说明符:', format_specifiers)
        print('格式说明符数量:', len(format_specifiers))
    else:
        print('格式字符串解析失败')
