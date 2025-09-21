#include <stdio.h>
#include <stdlib.h>

// 测试结构体定义 - 不应该检测初始化问题
struct Point {
    int x;        // 结构体成员不需要初始化
    int y;        // 结构体成员不需要初始化
    char *name;   // 结构体成员不需要初始化
};

// 测试函数参数 - 空指针传入应该被允许
void test_function(int *ptr) {
    if (ptr != NULL) {
        printf("Pointer is valid: %d\n", *ptr);
    } else {
        printf("Pointer is NULL\n");
    }
}

// 测试正常的变量初始化检测
int main() {
    // 这些应该被检测为未初始化
    int uninitialized_var;
    char uninitialized_char;
    int *uninitialized_ptr;
    
    // 使用未初始化变量 - 应该报错
    printf("Value: %d\n", uninitialized_var);
    printf("Char: %c\n", uninitialized_char);
    
    // 空指针解引用 - 应该报错
    *uninitialized_ptr = 10;
    
    // 正常的函数调用 - 空指针参数应该被允许
    test_function(NULL);
    test_function(&uninitialized_var);
    
    // 内存分配测试
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        printf("Allocated value: %d\n", *ptr);
        // 忘记释放内存 - 应该检测为内存泄漏
    }
    
    // 结构体使用测试
    struct Point p;
    p.x = 10;  // 结构体成员赋值应该正常
    p.y = 20;  // 结构体成员赋值应该正常
    p.name = "test";  // 结构体成员赋值应该正常
    
    printf("Point: (%d, %d) - %s\n", p.x, p.y, p.name);
    
    return 0;
}
