#include <stdio.h>

int main() {
    int d, i;
    float f;
    char str[100];
    char c;
    int *ptr = &d;
    
    // 正确的用法 - 不应该报错
    scanf("%d %d", &d, &i);  // 正确：普通变量有&符号
    scanf("%s", str);        // 正确：数组名不需要&符号
    scanf("%d", ptr);        // 正确：指针不需要&符号
    
    // 错误的用法 - 应该报错
    scanf("%d %d", d, i);    // 错误：普通变量缺少&符号
    scanf("%f %d", f, i);    // 错误：缺少&符号，类型不匹配
    scanf("%c", c);          // 错误：缺少&符号
    scanf("%s", &str);       // 错误：数组名不应该有&符号
    
    return 0;
}

