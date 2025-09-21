/*
 * 变量状态监察官模块测试用例
 * 包含各种变量状态问题的示例和正确用法
 */

#include <stdio.h>

// 错误示例1: 未初始化变量使用
void uninitialized_variable_example() {
    int x;
    int y;
    // 错误: 使用未初始化的变量
    printf("Sum: %d\n", x + y);
}

// 正确示例1: 初始化变量
void initialized_variable_example() {
    int x = 10;
    int y = 20;
    printf("Sum: %d\n", x + y);
}

// 错误示例2: 未初始化数组使用
void uninitialized_array_example() {
    int arr[5];
    // 错误: 使用未初始化的数组
    printf("First element: %d\n", arr[0]);
}

// 正确示例2: 初始化数组
void initialized_array_example() {
    int arr[5] = {1, 2, 3, 4, 5};
    printf("First element: %d\n", arr[0]);
}

// 错误示例3: 未初始化指针使用
void uninitialized_pointer_example() {
    int *ptr;
    // 错误: 使用未初始化的指针
    printf("Value: %d\n", *ptr);
}

// 正确示例3: 初始化指针
void initialized_pointer_example() {
    int *ptr = NULL;
    if (ptr != NULL) {
        printf("Value: %d\n", *ptr);
    }
}

// 错误示例4: 未初始化变量参与运算
void uninitialized_arithmetic_example() {
    int a, b, c;
    // 错误: 未初始化变量参与运算
    c = a + b;
    printf("Result: %d\n", c);
}

// 正确示例4: 初始化变量参与运算
void initialized_arithmetic_example() {
    int a = 10, b = 20, c;
    c = a + b;
    printf("Result: %d\n", c);
}

// 错误示例5: 未初始化变量进行比较
void uninitialized_comparison_example() {
    int x, y;
    // 错误: 未初始化变量进行比较
    if (x > y) {
        printf("x is greater\n");
    }
}

// 正确示例5: 初始化变量进行比较
void initialized_comparison_example() {
    int x = 15, y = 10;
    if (x > y) {
        printf("x is greater\n");
    }
}

// 错误示例6: 未初始化变量作为函数参数
void function_with_uninitialized_param(int param) {
    printf("Parameter: %d\n", param);
}

void uninitialized_function_param_example() {
    int x;
    // 错误: 未初始化变量作为函数参数
    function_with_uninitialized_param(x);
}

// 正确示例6: 初始化变量作为函数参数
void initialized_function_param_example() {
    int x = 42;
    function_with_uninitialized_param(x);
}

// 错误示例7: 未初始化变量参与指针运算
void uninitialized_pointer_arithmetic_example() {
    int *ptr;
    int arr[5] = {1, 2, 3, 4, 5};
    // 错误: 未初始化指针进行运算
    printf("Value: %d\n", *(ptr + 1));
}

// 正确示例7: 初始化指针参与运算
void initialized_pointer_arithmetic_example() {
    int *ptr;
    int arr[5] = {1, 2, 3, 4, 5};
    ptr = arr;  // 初始化指针
    printf("Value: %d\n", *(ptr + 1));
}

// 错误示例8: 未初始化变量参与数组访问
void uninitialized_array_access_example() {
    int index;
    int arr[5] = {1, 2, 3, 4, 5};
    // 错误: 未初始化变量作为数组索引
    printf("Value: %d\n", arr[index]);
}

// 正确示例8: 初始化变量参与数组访问
void initialized_array_access_example() {
    int index = 2;
    int arr[5] = {1, 2, 3, 4, 5};
    printf("Value: %d\n", arr[index]);
}

int main() {
    printf("变量状态测试开始\n");
    
    // 运行各种测试
    uninitialized_variable_example();
    initialized_variable_example();
    uninitialized_array_example();
    initialized_array_example();
    uninitialized_pointer_example();
    initialized_pointer_example();
    uninitialized_arithmetic_example();
    initialized_arithmetic_example();
    uninitialized_comparison_example();
    initialized_comparison_example();
    uninitialized_function_param_example();
    initialized_function_param_example();
    uninitialized_pointer_arithmetic_example();
    initialized_pointer_arithmetic_example();
    uninitialized_array_access_example();
    initialized_array_access_example();
    
    printf("变量状态测试结束\n");
    return 0;
}

/*
 * 标准答案:
 * 1. 第12行: 未初始化变量使用 - x和y未初始化就被使用
 * 2. 第22行: 未初始化数组使用 - arr[0]未初始化就被访问
 * 3. 第32行: 未初始化指针使用 - ptr未初始化就被解引用
 * 4. 第42行: 未初始化变量参与运算 - a和b未初始化就参与运算
 * 5. 第52行: 未初始化变量进行比较 - x和y未初始化就比较
 * 6. 第62行: 未初始化变量作为函数参数 - x未初始化就作为参数
 * 7. 第72行: 未初始化指针参与运算 - ptr未初始化就进行指针运算
 * 8. 第82行: 未初始化变量参与数组访问 - index未初始化就作为数组索引
 */
