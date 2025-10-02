#include <stdio.h>

int main() {
    int d;
    int i;
    float f;
    char c;
    
    // 这里应该检测到参数缺少&符号的问题
    scanf("%d %d", d, i);  // 缺少&符号
    scanf("%f %d", f, i);  // 缺少&符号
    
    scanf("%c", c);  // 缺少&符号
    
    return 0;
}

