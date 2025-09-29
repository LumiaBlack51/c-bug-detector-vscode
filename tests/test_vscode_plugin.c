#include <stdio.h>
#include <stdlib.h>

// 测试VSCode插件检测功能
int main() {
    // 测试死循环检测
    while(1) {
        printf("This is an infinite loop\n");
    }
    
    // 测试内存泄漏检测
    int *ptr = malloc(sizeof(int));
    // 忘记释放内存
    
    // 测试变量未初始化
    int uninitialized_var;
    printf("%d\n", uninitialized_var);
    
    return 0;
}
