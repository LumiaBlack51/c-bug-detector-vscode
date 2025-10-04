#include <stdio.h>
#include <stdlib.h>

int main() {
    // 第5行
    int *p1 = malloc(sizeof(int));  // 这应该是第6行
    // 第7行
    int *p2 = malloc(sizeof(int));  // 这应该是第8行
    // 第9行
    return 0;
}
