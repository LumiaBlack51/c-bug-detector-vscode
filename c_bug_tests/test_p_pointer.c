#include <stdio.h>

int main() {
    int *ptr = NULL;
    int value;
    
    // 指针相关问题
    *ptr = 10;  // 空指针解引用
    
    scanf("%d", ptr);    // 指针不需要&符号
    scanf("%d", value);  // 非指针需要&符号
    
    return 0;
}

