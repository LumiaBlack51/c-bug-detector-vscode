#include <stdio.h>
#include <stdlib.h>

// 测试函数定义识别 - 不应该报未初始化
int testFunction(int param1, char param2) {
    int localVar = 10;  // 已初始化
    char uninitVar;     // 未初始化，但这是函数定义内，不应该报错
    return localVar;
}

// 测试malloc内存管理 - return的情况
int* createArray(int size) {
    int* arr = malloc(size * sizeof(int));
    if (arr == NULL) {
        return NULL;  // 这里return了malloc的内存，不应该报内存泄漏
    }
    return arr;  // 这里也return了，不应该报内存泄漏
}

// 测试malloc内存管理 - free的情况
void processData(int* data) {
    int* temp = malloc(100 * sizeof(int));
    if (temp != NULL) {
        // 使用temp...
        free(temp);  // 这里free了，不应该报内存泄漏
    }
}

// 测试变量状态检测
void testVariableState() {
    int uninitVar;      // 未初始化
    int initVar = 5;    // 已初始化
    
    printf("initVar = %d\n", initVar);  // 使用已初始化变量，正常
    printf("uninitVar = %d\n", uninitVar);  // 使用未初始化变量，应该报错
}

// 测试结构体定义
struct Point {
    int x;  // 结构体成员，不需要初始化检测
    int y;  // 结构体成员，不需要初始化检测
};

// 测试函数调用中的变量使用
void testFunctionCall() {
    int value = 42;
    printf("Value: %d\n", value);  // 函数调用中的变量使用，正常
}

int main() {
    int* ptr = createArray(10);
    if (ptr != NULL) {
        free(ptr);  // 释放从函数返回的内存
    }
    
    testVariableState();
    testFunctionCall();
    
    return 0;
}
