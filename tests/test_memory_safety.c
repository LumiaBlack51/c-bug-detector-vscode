/*
 * 内存安全卫士模块测试用例
 * 包含各种内存安全问题的示例和正确用法
 */

#include <stdio.h>
#include <stdlib.h>

// 错误示例1: 内存泄漏
void memory_leak_example() {
    int *ptr = malloc(sizeof(int));
    *ptr = 42;
    printf("Value: %d\n", *ptr);
    // 错误: 忘记释放内存
    // 应该添加: free(ptr);
}

// 正确示例1: 正确释放内存
void correct_memory_usage() {
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        printf("Value: %d\n", *ptr);
        free(ptr);
        ptr = NULL;  // 防止野指针
    }
}

// 错误示例2: 野指针使用
void wild_pointer_example() {
    int *ptr = malloc(sizeof(int));
    *ptr = 100;
    free(ptr);
    // 错误: 释放后继续使用指针
    printf("Value: %d\n", *ptr);
}

// 正确示例2: 避免野指针
void avoid_wild_pointer() {
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 100;
        free(ptr);
        ptr = NULL;  // 设置为NULL防止野指针
    }
}

// 错误示例3: 空指针解引用
void null_pointer_dereference() {
    int *ptr = NULL;
    // 错误: 未检查NULL就解引用
    printf("Value: %d\n", *ptr);
}

// 正确示例3: NULL检查
void null_pointer_check() {
    int *ptr = NULL;
    if (ptr != NULL) {
        printf("Value: %d\n", *ptr);
    } else {
        printf("Pointer is NULL\n");
    }
}

// 错误示例4: 返回局部指针
int* return_local_pointer() {
    int local_var = 42;
    // 错误: 返回局部变量的地址
    return &local_var;
}

// 正确示例4: 返回动态分配的内存
int* return_dynamic_memory() {
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
    }
    return ptr;
}

// 错误示例5: 未检查malloc返回值
void unchecked_malloc() {
    int *ptr = malloc(sizeof(int));
    // 错误: 未检查malloc是否成功
    *ptr = 42;
    free(ptr);
}

// 正确示例5: 检查malloc返回值
void checked_malloc() {
    int *ptr = malloc(sizeof(int));
    if (ptr == NULL) {
        printf("Memory allocation failed\n");
        return;
    }
    *ptr = 42;
    free(ptr);
}

// 错误示例6: 重复释放
void double_free_example() {
    int *ptr = malloc(sizeof(int));
    *ptr = 42;
    free(ptr);
    // 错误: 重复释放同一块内存
    free(ptr);
}

// 正确示例6: 避免重复释放
void avoid_double_free() {
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        free(ptr);
        ptr = NULL;  // 设置为NULL防止重复释放
    }
}

int main() {
    printf("内存安全测试开始\n");
    
    // 运行各种测试
    memory_leak_example();
    correct_memory_usage();
    wild_pointer_example();
    avoid_wild_pointer();
    null_pointer_dereference();
    null_pointer_check();
    
    int *ptr1 = return_local_pointer();
    int *ptr2 = return_dynamic_memory();
    
    unchecked_malloc();
    checked_malloc();
    double_free_example();
    avoid_double_free();
    
    printf("内存安全测试结束\n");
    return 0;
}

/*
 * 标准答案:
 * 1. 第15行: 内存泄漏 - malloc后未释放
 * 2. 第35行: 野指针使用 - free后继续使用指针
 * 3. 第45行: 空指针解引用 - 未检查NULL就解引用
 * 4. 第55行: 返回局部指针 - 返回局部变量地址
 * 5. 第65行: 未检查malloc返回值 - malloc后未检查NULL
 * 6. 第75行: 重复释放 - 对同一指针调用两次free
 */
