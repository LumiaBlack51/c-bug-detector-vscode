#include <stdio.h>
#include <stdlib.h>

// 测试函数声明和定义问题
void test_function(int param);

int main() {
    // 测试变量作用域问题
    {
        int local_var = 10;
    }
    printf("局部变量: %d\n", local_var);  // 错误：访问已销毁的局部变量
    
    // 测试函数调用
    test_function(5);
    
    // 测试内存泄漏
    char *buffer = malloc(100);
    strcpy(buffer, "test");
    printf("缓冲区内容: %s\n", buffer);
    // 错误：忘记释放buffer
    
    // 测试双重释放
    int *ptr1 = malloc(sizeof(int));
    free(ptr1);
    free(ptr1);  // 错误：双重释放
    
    // 测试使用已释放的内存
    int *ptr2 = malloc(sizeof(int));
    *ptr2 = 42;
    free(ptr2);
    printf("已释放内存的值: %d\n", *ptr2);  // 错误：使用已释放的内存
    
    return 0;
}

void test_function(int param) {
    // 测试参数使用
    printf("参数值: %d\n", param);
    
    // 测试局部变量未初始化
    int local_uninit;
    if (local_uninit > 0) {  // 错误：使用未初始化变量
        printf("条件成立\n");
    }
}

