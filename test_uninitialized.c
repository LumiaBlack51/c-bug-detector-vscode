#include <stdio.h>
#include <stdlib.h>

int main() {
    // 测试未初始化变量的各种使用情况
    int x;           // 未初始化
    int y;           // 未初始化
    int z = 10;      // 已初始化
    
    // 应该检测到的问题：未初始化变量被使用
    printf("x = %d\n", x);        // BUG: 打印未初始化变量
    y = x + 5;                    // BUG: 使用未初始化变量进行计算
    if (x > 0) {                  // BUG: 比较未初始化变量
        printf("x is positive\n");
    }
    
    // 正确的使用：未初始化变量被赋值
    x = 20;                       // 正确：给未初始化变量赋值
    scanf("%d", &y);              // 正确：未初始化变量作为scanf参数
    
    // 正确的使用：已初始化变量
    printf("z = %d\n", z);       // 正确：使用已初始化变量
    y = z + 5;                   // 正确：使用已初始化变量
    
    return 0;
}
