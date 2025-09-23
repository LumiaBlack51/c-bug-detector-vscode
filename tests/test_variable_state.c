#include <stdio.h>
#include <stdbool.h>

// 测试函数参数不会误报
void test_function_params(int param1, int *param2, char param3) {
    // 这些参数在函数体内使用不应该报错
    printf("param1 = %d\n", param1);        // 应该不报错
    *param2 = 42;                           // 应该不报错
    printf("param3 = %c\n", param3);        // 应该不报错
    
    // 测试局部变量
    int local_var;                          // 未初始化的局部变量
    printf("local_var = %d\n", local_var);  // BUG: uninitialized variable
}

// 测试 static 变量
void test_static_vars() {
    static int static_counter = 0;          // 已初始化的 static 变量
    static bool static_flag;                // 未初始化的 static 变量
    
    static_counter++;                       // 应该不报错
    if (static_flag) {                      // BUG: uninitialized variable
        printf("flag is true\n");
    }
}

// 测试 const 变量
void test_const_vars() {
    const int const_val = 100;              // 已初始化的 const 变量
    const char *const_str = "hello";        // 已初始化的 const 指针
    
    printf("const_val = %d\n", const_val);  // 应该不报错
    printf("const_str = %s\n", const_str);  // 应该不报错
}

int main() {
    int x = 10;
    int *ptr = &x;
    char ch = 'A';
    
    test_function_params(x, ptr, ch);
    test_static_vars();
    test_const_vars();
    
    return 0;
}