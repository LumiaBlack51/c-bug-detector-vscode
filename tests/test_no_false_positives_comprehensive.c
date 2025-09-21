#include <stdio.h>
#include <stdlib.h>

// 测试误报检测 - 这些代码应该不报错

// 函数1: 正确的指针使用
void test_correct_usage() {
    // 1. 指针初始化为NULL，但不解引用
    int* ptr1 = NULL;
    printf("ptr1 is NULL\n");
    
    // 2. 指针分配内存后正常使用
    int* ptr2 = malloc(sizeof(int));
    if (ptr2 != NULL) {
        *ptr2 = 42;
        printf("value = %d\n", *ptr2);
        free(ptr2);
    }
    
    // 3. 指针指向局部变量
    int x = 100;
    int* ptr3 = &x;
    printf("value = %d\n", *ptr3);
    
    // 4. 指针指向数组
    int arr[5] = {1, 2, 3, 4, 5};
    int* ptr4 = arr;
    printf("arr[0] = %d\n", ptr4[0]);
}

// 函数2: 正确的结构体指针使用
struct Point {
    int x, y;
};

void test_correct_struct_usage() {
    // 1. 结构体指针分配内存
    struct Point* p1 = malloc(sizeof(struct Point));
    if (p1 != NULL) {
        p1->x = 10;
        p1->y = 20;
        printf("Point: (%d, %d)\n", p1->x, p1->y);
        free(p1);
    }
    
    // 2. 结构体指针指向局部结构体
    struct Point p2 = {30, 40};
    struct Point* p3 = &p2;
    printf("Point: (%d, %d)\n", p3->x, p3->y);
}

// 函数3: 正确的指针赋值
void test_correct_pointer_assignment() {
    // 1. 有效指针赋值
    int* ptr1 = malloc(sizeof(int));
    if (ptr1 != NULL) {
        *ptr1 = 50;
        int* ptr2 = ptr1;  // 有效指针赋值
        printf("value = %d\n", *ptr2);
        free(ptr1);
    }
    
    // 2. NULL指针赋值
    int* ptr3 = NULL;
    int* ptr4 = ptr3;  // NULL指针赋值
    printf("ptr4 is NULL\n");
}

// 函数4: 正确的函数参数传递
void test_correct_function_params() {
    int* ptr1 = malloc(sizeof(int));
    if (ptr1 != NULL) {
        *ptr1 = 60;
        printf("Passing valid pointer to function\n");
        free(ptr1);
    }
    
    int* ptr2 = NULL;
    printf("Passing NULL pointer to function\n");
}

// 函数5: 正确的条件检查
void test_correct_condition_check() {
    int* ptr1 = malloc(sizeof(int));
    if (ptr1 != NULL) {
        *ptr1 = 70;
        printf("value = %d\n", *ptr1);
        free(ptr1);
    } else {
        printf("Memory allocation failed\n");
    }
}

int main() {
    printf("Testing correct pointer usage (should not report errors)...\n");
    
    test_correct_usage();
    test_correct_struct_usage();
    test_correct_pointer_assignment();
    test_correct_function_params();
    test_correct_condition_check();
    
    return 0;
}
