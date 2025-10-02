#include <stdio.h>
#include <stdlib.h>

int main() {
    int *ptr = malloc(sizeof(int) * 10);
    ptr[0] = 42;
    printf("Value: %d\n", ptr[0]);
    // 内存泄漏：忘记释放 ptr
    return 0;
}
