#include <stdio.h>

int main() {
    int i;
    float f;
    
    // 类型不匹配的问题
    scanf("%f", &i);  // 错误：整数变量用浮点格式符
    scanf("%d", &f);  // 错误：浮点变量用整数格式符
    
    return 0;
}

