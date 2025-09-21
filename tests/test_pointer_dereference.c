#include <stdio.h>
#include <stdlib.h>

int main() {
    // 测试1：指针初始化为NULL，但不解引用 - 不应该报错
    int* ptr1 = NULL;
    printf("ptr1 is NULL\n");  // 不解引用，应该正常
    
    // 测试2：指针初始化为NULL，然后解引用 - 应该报错
    int* ptr2 = NULL;
    printf("value = %d\n", *ptr2);  // 解引用NULL指针，应该报错
    
    // 测试3：指针分配内存后解引用 - 应该正常
    int* ptr3 = malloc(sizeof(int));
    if (ptr3 != NULL) {
        *ptr3 = 42;  // 解引用有效指针，应该正常
        printf("value = %d\n", *ptr3);
        free(ptr3);
    }
    
    // 测试4：指针赋值为NULL后解引用 - 应该报错
    int* ptr4 = malloc(sizeof(int));
    ptr4 = NULL;  // 重新赋值为NULL
    printf("value = %d\n", *ptr4);  // 解引用NULL指针，应该报错
    
    // 测试5：未初始化指针解引用 - 应该报错
    int* ptr5;
    printf("value = %d\n", *ptr5);  // 解引用未初始化指针，应该报错
    
    // 测试6：指针数组访问 - 应该正常
    int* ptr6 = malloc(10 * sizeof(int));
    if (ptr6 != NULL) {
        ptr6[0] = 100;  // 数组访问，应该正常
        printf("array[0] = %d\n", ptr6[0]);
        free(ptr6);
    }
    
    return 0;
}
