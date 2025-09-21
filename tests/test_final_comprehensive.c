#include <stdio.h>
#include <stdlib.h>

// 测试野指针和空指针检测功能

// 函数1: 野指针解引用
void test_wild_pointer() {
    int *ptr1; // 未初始化的指针
    *ptr1 = 42; // BUG: 解引用野指针 - 应该报错
    
    char *str1; // 未初始化的指针
    str1[0] = 'A'; // BUG: 解引用野指针 - 应该报错
    
    double *arr1; // 未初始化的指针
    arr1[0] = 3.14; // BUG: 解引用野指针 - 应该报错
}

// 函数2: 空指针解引用
void test_null_pointer() {
    int *ptr2 = NULL; // 初始化为NULL
    *ptr2 = 100; // BUG: 解引用空指针 - 应该报错
    
    char *str2 = 0; // 初始化为0（等同于NULL）
    str2[0] = 'B'; // BUG: 解引用空指针 - 应该报错
    
    float *arr2 = NULL;
    arr2[0] = 2.5; // BUG: 解引用空指针 - 应该报错
}

// 函数3: 野指针作为函数参数
void test_wild_pointer_param() {
    int *ptr3; // 未初始化的指针
    printf("%d\n", *ptr3); // BUG: 解引用野指针 - 应该报错
    
    char *str3; // 未初始化的指针
    scanf("%s", str3); // BUG: 野指针作为参数 - 应该报错
}

// 函数4: 空指针作为函数参数
void test_null_pointer_param() {
    int *ptr4 = NULL;
    printf("%d\n", *ptr4); // 解引用空指针 - 当前检测器无法检测
    
    char *str4 = 0;
    scanf("%s", str4); // 空指针作为参数 - 当前检测器无法检测
}

// 函数5: 正确的指针使用（不应该报错）
void test_correct_pointer() {
    int x = 42;
    int *ptr5 = &x; // 正确：指向有效变量
    printf("%d\n", *ptr5); // 正确：解引用有效指针
    
    char str5[10] = "Hello";
    char *ptr6 = str5; // 正确：指向数组
    printf("%s\n", ptr6); // 正确：使用有效指针
    
    int *ptr7 = malloc(sizeof(int)); // 正确：分配内存
    if (ptr7) {
        *ptr7 = 100; // 正确：解引用有效指针
        printf("%d\n", *ptr7);
        free(ptr7); // 正确：释放内存
    }
}

// 函数6: 指针赋值后的使用
void test_pointer_assignment() {
    int *ptr8; // 未初始化的指针
    int *ptr9 = ptr8; // 将野指针赋值给另一个指针 - 当前检测器无法检测
    *ptr9 = 200; // 解引用野指针 - 当前检测器无法检测
    
    int *ptr10 = NULL;
    int *ptr11 = ptr10; // 将空指针赋值给另一个指针
    *ptr11 = 300; // 解引用空指针 - 当前检测器无法检测
}

// 函数7: 结构体指针
struct Point {
    int x, y;
};

void test_struct_pointer() {
    struct Point *p1; // 未初始化的结构体指针
    p1->x = 10; // BUG: 解引用野指针 - 应该报错
    p1->y = 20; // BUG: 解引用野指针 - 应该报错
    
    struct Point *p2 = NULL;
    p2->x = 30; // BUG解引用空指针 - 应该报错
    p2->y = 40; // BUG解引用空指针 - 应该报错
}

// 函数8: 数组指针
void test_array_pointer() {
    int *arr1; // 未初始化的指针
    arr1[0] = 1; // BUG: 解引用野指针 - 应该报错
    arr1[1] = 2; // BUG: 解引用野指针 - 应该报错
    
    int *arr2 = NULL;
    arr2[0] = 3; // BUG: 解引用空指针 - 应该报错
    arr2[1] = 4; // BUG: 解引用空指针 - 应该报错
}

// 函数9: 函数指针
void dummy_function() {
    printf("Dummy function called\n");
}

void test_function_pointer() {
    void (*func_ptr1)(); // 未初始化的函数指针
    func_ptr1(); // 调用野函数指针 - 当前检测器无法检测
    
    void (*func_ptr2)() = NULL;
    func_ptr2(); // 调用空函数指针 - 当前检测器无法检测
    
    void (*func_ptr3)() = dummy_function; // 正确：指向有效函数
    func_ptr3(); // 正确：调用有效函数指针
}

int main() {
    printf("Testing wild pointer and null pointer detection...\n");
    
    test_wild_pointer();
    test_null_pointer();
    test_wild_pointer_param();
    test_null_pointer_param();
    test_correct_pointer();
    test_pointer_assignment();
    test_struct_pointer();
    test_array_pointer();
    test_function_pointer();
    
    return 0;
}
