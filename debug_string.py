# 测试字符串内容
test_string = '"Point %d: (%d, %d)\\n", i, points[i].x, points[i].y'
print('测试字符串:', repr(test_string))
print('字符串长度:', len(test_string))

# 查找引号位置
quote_start = test_string.find('"')
print('引号开始位置:', quote_start)

if quote_start != -1:
    quote_end = quote_start + 1
    while quote_end < len(test_string):
        if test_string[quote_end] == '"':
            print(f'找到引号在位置 {quote_end}')
            break
        quote_end += 1
    
    if quote_end < len(test_string):
        format_string = test_string[quote_start + 1:quote_end]
        print('提取的格式字符串:', repr(format_string))
        print('格式字符串长度:', len(format_string))
