#include <stdio.h>

int main() {
    int d;
    int i;
    float f;
    char str[100];
    char c;
    
    // 这里应该检测到参数缺少&符号的问题，但不应该把格式符%d中的d当作变量
    scanf("%d %d", d, i);  // 缺少&符号，但%d中的d不是变量
    scanf("%f %d", f, i);  // 缺少&符号，类型不匹配：整数传给浮点
    scanf("%s", str);      // str是数组名，不需要&符号
    scanf("%c", c);        // 缺少&符号
    
    return 0;
}

