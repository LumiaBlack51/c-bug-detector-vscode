#include <stdio.h>
#include <stdlib.h>

// 这个文件应该检测到一些问题

int main() {
    int uninitVar;      // 未初始化变量
    int* ptr = malloc(sizeof(int));  // malloc但未free
    
    printf("uninitVar = %d\n", uninitVar);  // 使用未初始化变量
    
    // ptr没有被free，应该报内存泄漏
    
    return 0;
}
