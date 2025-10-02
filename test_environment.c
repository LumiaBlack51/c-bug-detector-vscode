#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // 测试printf格式问题
    int num = 42;
    char str[] = "hello";
    printf("%s\n", num);        // 错误：%s期望char*，但num是int
    printf("%d\n", str);        // 错误：%d期望int，但str是char*
    printf("%f\n", num);        // 错误：%f期望double，但num是int
    
    // 测试scanf问题
    int x, y;
    scanf("%d", x);             // 错误：缺少&符号
    scanf("%d %d", &x, y);      // 错误：第二个参数缺少&符号
    
    // 测试未初始化变量
    int uninitialized_var;
    printf("未初始化变量: %d\n", uninitialized_var);  // 错误：使用未初始化变量
    
    // 测试内存安全问题
    int *ptr = malloc(sizeof(int));
    *ptr = 100;
    printf("分配的内存值: %d\n", *ptr);
    // 错误：忘记释放内存
    
    // 测试野指针
    int *wild_ptr;
    *wild_ptr = 50;             // 错误：使用未初始化的指针
    
    // 测试数组越界
    int arr[5] = {1, 2, 3, 4, 5};
    printf("数组元素: %d\n", arr[10]);  // 错误：数组越界访问
    
    // 测试死循环
    int i = 0;
    while (i < 10) {
        printf("i = %d\n", i);
        // 错误：忘记递增i，可能导致死循环
    }
    
    return 0;
}

