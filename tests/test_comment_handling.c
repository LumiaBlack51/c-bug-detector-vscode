#include <stdio.h>
#include <stdlib.h>

// 这是单行注释，测试注释处理
int main() {
    int *ptr1; // 未初始化的指针
    *ptr1 = 42; // 解引用野指针 - 应该报错
    
    /* 这是多行注释
       测试多行注释处理 */
    char *str1; /* 行内多行注释 */
    str1[0] = 'A'; // 解引用野指针
    
    /*
     * 这是跨行多行注释
     * 应该被完全忽略
     */
    double *arr1; // 未初始化的指针
    arr1[0] = 3.14; // 解引用野指针
    
    // 测试包含&字符的注释
    int *ptr2 = NULL; // 注释中包含&字符
    *ptr2 = 100; // 解引用空指针
    
    // 测试scanf注释
    char str2[100];
    scanf("%s", str2); // 正确：字符串不需要&
    
    int x;
    scanf("%d", x); // 错误：整数需要&
    
    return 0;
}
