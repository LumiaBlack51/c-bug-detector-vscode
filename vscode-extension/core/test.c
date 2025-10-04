#include <stdio.h>

int main() {
    int x;  // 未初始化变量
    printf("x = %d\n", x);  // BUG: 使用未初始化变量
    
    int *ptr;  // 未初始化指针
    *ptr = 42;  // BUG: 野指针解引用
    
    return 0;
}
