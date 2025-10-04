import re

# 测试字符串匹配
test_string = '"Point %d: (%d, %d)\\n", i, points[i].x, points[i].y'
print('测试字符串:', test_string)

# 测试不同的正则表达式
patterns = [
    r'"([^"]*)"',  # 原始模式
    r'"([^"\\]*(\\.[^"\\]*)*)"',  # 改进模式
    r'"([^"\\\\]*(\\\\.[^"\\\\]*)*)"',  # 更严格的模式
]

for i, pattern in enumerate(patterns):
    print(f'\n模式 {i+1}: {pattern}')
    match = re.search(pattern, test_string)
    if match:
        print('匹配结果:', match.group(1))
        print('匹配结束位置:', match.end())
    else:
        print('无匹配')
