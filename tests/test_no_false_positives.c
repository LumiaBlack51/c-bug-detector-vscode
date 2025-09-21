#include <stdio.h>
#include <stdlib.h>

int main() {
    // 这些情况不应该报错
    
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
    
    // 3. 指针数组正常访问
    int* ptr3 = malloc(10 * sizeof(int));
    if (ptr3 != NULL) {
        ptr3[0] = 100;
        printf("array[0] = %d\n", ptr3[0]);
        free(ptr3);
    }
    
    // 4. 指针作为函数参数传递
    int* ptr4 = NULL;
    printf("Passing NULL pointer to function\n");
    
    return 0;
}
