import re

# 测试printf参数解析
test_line = 'printf("Point %d: (%d, %d)\\n", i, points[i].x, points[i].y);'
print('测试行:', test_line)

# 提取printf参数
printf_match = re.search(r'printf\s*\(([^)]+)\)', test_line)
if printf_match:
    params_content = printf_match.group(1).strip()
    print('参数内容:', repr(params_content))
    print('参数内容长度:', len(params_content))
    
    # 查找引号位置
    quote_start = params_content.find('"')
    print('引号开始位置:', quote_start)
    
    if quote_start != -1:
        quote_end = quote_start + 1
        while quote_end < len(params_content):
            if params_content[quote_end] == '"':
                print(f'找到引号在位置 {quote_end}')
                break
            quote_end += 1
        
        if quote_end < len(params_content):
            format_string = params_content[quote_start + 1:quote_end]
            print('提取的格式字符串:', repr(format_string))
            print('格式字符串长度:', len(format_string))
