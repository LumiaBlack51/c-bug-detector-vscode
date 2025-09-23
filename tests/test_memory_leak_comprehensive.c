#include <stdio.h>
#include <stdlib.h>

// BUG: 内存泄漏和忘记释放测试
int main() {
    // 测试1: 基本内存泄漏
    int *ptr1 = malloc(sizeof(int) * 10); // BUG: memory leak - 忘记释放
    ptr1[0] = 42;
    printf("ptr1[0] = %d\n", ptr1[0]);
    
    // 测试2: 多个内存泄漏
    char *str1 = malloc(100); // BUG: memory leak - 忘记释放
    double *arr1 = malloc(sizeof(double) * 20); // BUG: memory leak - 忘记释放
    str1[0] = 'A';
    arr1[0] = 3.14;
    
    // 测试3: 条件分配但未释放
    int *ptr2 = malloc(sizeof(int) * 5);
    if (ptr2) {
        ptr2[0] = 100;
        printf("ptr2[0] = %d\n", ptr2[0]);
        // BUG: memory leak - 忘记释放ptr2
    }
    
    // 测试4: 循环中的内存泄漏
    for (int i = 0; i < 5; i++) {
        int *temp = malloc(sizeof(int)); // BUG: memory leak - 忘记释放temp
        *temp = i;
        printf("temp[%d] = %d\n", i, *temp);
    }
    
    // 测试5: 函数中的内存泄漏
    void leaky_function() {
        char *local_ptr = malloc(50); // BUG: memory leak - 忘记释放local_ptr
        strcpy(local_ptr, "Hello");
        printf("local_ptr = %s\n", local_ptr);
    }
    leaky_function();
    
    // 测试6: 部分释放内存泄漏
    int *ptr3 = malloc(sizeof(int) * 3);
    char *str3 = malloc(30);
    float *arr3 = malloc(sizeof(float) * 5);
    
    if (ptr3) {
        ptr3[0] = 200;
        free(ptr3); // 正确释放
    }
    
    if (str3) {
        strcpy(str3, "Partial");
        // BUG: memory leak - 忘记释放str3
    }
    
    if (arr3) {
        arr3[0] = 2.5;
        free(arr3); // 正确释放
    }
    
    // 测试7: realloc后的内存泄漏
    int *ptr4 = malloc(sizeof(int) * 10);
    if (ptr4) {
        ptr4[0] = 300;
        
        // 重新分配内存
        ptr4 = realloc(ptr4, sizeof(int) * 20);
        if (ptr4) {
            ptr4[10] = 400;
            // BUG: memory leak - 忘记释放realloc后的内存
        }
    }
    
    // 测试8: 嵌套函数调用中的内存泄漏
    void helper_function() {
        char *temp = malloc(20); // BUG: memory leak - 忘记释放temp
        strcpy(temp, "Helper");
        printf("temp = %s\n", temp);
    }
    
    void test_nested_leak() {
        int *ptr5 = malloc(sizeof(int) * 2);
        if (ptr5) {
            ptr5[0] = 500;
            helper_function(); // 调用有内存泄漏的函数
            free(ptr5); // 正确释放
        }
    }
    test_nested_leak();
    
    // 测试9: 条件释放导致的内存泄漏
    int *ptr6 = malloc(sizeof(int) * 2);
    char *str6 = malloc(20);
    
    if (ptr6) {
        ptr6[0] = 600;
        
        // 只在某些条件下释放
        if (ptr6[0] > 500) {
            free(ptr6); // 正确释放
        }
        // BUG: memory leak - str6在某些条件下未释放
    }
    
    // 测试10: 结构体中的内存泄漏
    struct Data {
        int *values;
        char *name;
        int count;
    };
    
    struct Data *data = malloc(sizeof(struct Data));
    if (data) {
        data->values = malloc(sizeof(int) * 10); // BUG: memory leak - 忘记释放values
        data->name = malloc(50); // BUG: memory leak - 忘记释放name
        data->count = 10;
        
        data->values[0] = 700;
        strcpy(data->name, "Test");
        
        free(data); // 只释放了结构体本身，忘记释放成员指针
    }
    
    // 测试11: 链表中的内存泄漏
    struct ListNode {
        int data;
        struct ListNode* next;
    };
    
    struct ListNode* head = malloc(sizeof(struct ListNode));
    if (head) {
        head->data = 800;
        head->next = malloc(sizeof(struct ListNode)); // BUG: memory leak - 忘记释放next
        if (head->next) {
            head->next->data = 900;
            head->next->next = NULL;
        }
        
        free(head); // 只释放了头节点，忘记释放其他节点
    }
    
    // 测试12: 数组中的内存泄漏
    int **matrix = malloc(sizeof(int*) * 5);
    if (matrix) {
        for (int i = 0; i < 5; i++) {
            matrix[i] = malloc(sizeof(int) * 5); // BUG: memory leak - 忘记释放每行
            for (int j = 0; j < 5; j++) {
                matrix[i][j] = i * 5 + j;
            }
        }
        
        // 使用矩阵
        printf("matrix[0][0] = %d\n", matrix[0][0]);
        
        free(matrix); // 只释放了行指针数组，忘记释放每行
    }
    
    // 测试13: 字符串数组中的内存泄漏
    char **strings = malloc(sizeof(char*) * 3);
    if (strings) {
        strings[0] = malloc(20); // BUG: memory leak - 忘记释放
        strings[1] = malloc(20); // BUG: memory leak - 忘记释放
        strings[2] = malloc(20); // BUG: memory leak - 忘记释放
        
        strcpy(strings[0], "First");
        strcpy(strings[1], "Second");
        strcpy(strings[2], "Third");
        
        free(strings); // 只释放了字符串指针数组，忘记释放每个字符串
    }
    
    // 测试14: 函数返回的内存泄漏
    int* get_memory() {
        int *ptr = malloc(sizeof(int) * 5); // BUG: memory leak - 返回的内存可能被忘记释放
        ptr[0] = 1000;
        return ptr;
    }
    
    int *returned_ptr = get_memory();
    printf("returned_ptr[0] = %d\n", returned_ptr[0]);
    // BUG: memory leak - 忘记释放返回的内存
    
    // 测试15: 异常路径中的内存泄漏
    int *ptr7 = malloc(sizeof(int) * 10);
    if (ptr7) {
        ptr7[0] = 1100;
        
        // 模拟错误条件
        if (ptr7[0] < 0) {
            free(ptr7); // 只在错误条件下释放
        }
        // BUG: memory leak - 正常路径下忘记释放
    }
    
    printf("内存泄漏测试完成\n");
    return 0;
}
