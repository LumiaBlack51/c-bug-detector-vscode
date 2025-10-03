#include <stdio.h>
#include <stdlib.h>

// BUG: 变量未初始化测试
int main() {
    // 测试1: 基本变量未初始化
    int x; // BUG: uninitialized variable
    printf("x = %d\n", x);
    
    // 测试2: 字符变量未初始化
    char c; // BUG: uninitialized variable
    printf("c = %c\n", c);
    
    // 测试3: 浮点变量未初始化
    float f; // BUG: uninitialized variable
    printf("f = %f\n", f);
    
    // 测试4: 数组未初始化
    int arr[5]; // BUG: uninitialized variable
    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }
    
    // 测试5: 结构体未初始化
    struct Data {
        int id;
        char name[20];
        float score;
    };
    struct Data data; // BUG: uninitialized variable
    printf("data.id = %d\n", data.id);
    printf("data.name = %s\n", data.name);
    printf("data.score = %f\n", data.score);
    
    // 测试6: 局部变量未初始化
    void test_local() {
        int local_var; // BUG: uninitialized variable
        printf("local_var = %d\n", local_var);
    }
    test_local();
    
    // 测试7: 条件语句中的未初始化变量
    int cond_var; // BUG: uninitialized variable
    if (1) {
        printf("cond_var = %d\n", cond_var);
    }
    
    // 测试8: 循环中的未初始化变量
    int loop_var; // BUG: uninitialized variable
    for (int i = 0; i < 3; i++) {
        printf("loop_var = %d\n", loop_var);
    }
    
    // 测试9: 函数参数计算中的未初始化变量
    int calc_var; // BUG: uninitialized variable
    int result = calc_var + 10; // BUG: uninitialized variable
    printf("result = %d\n", result);
    
    // 测试10: 数组索引中的未初始化变量
    int index_var; // BUG: uninitialized variable
    int test_arr[10] = {0};
    printf("test_arr[index_var] = %d\n", test_arr[index_var]); // BUG: uninitialized variable
    
    // 测试11: 指针算术中的未初始化变量
    int *ptr = malloc(sizeof(int));
    int offset_var; // BUG: uninitialized variable
    printf("*(ptr + offset_var) = %d\n", *(ptr + offset_var)); // BUG: uninitialized variable
    free(ptr);
    
    // 测试12: 结构体成员访问中的未初始化变量
    struct Test {
        int values[5];
    };
    struct Test test_struct; // BUG: uninitialized variable
    int member_index; // BUG: uninitialized variable
    printf("test_struct.values[member_index] = %d\n", test_struct.values[member_index]); // BUG: uninitialized variable
    
    return 0;
}
