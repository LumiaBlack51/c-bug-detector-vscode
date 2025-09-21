/*
 * 标准库使用助手模块测试用例
 * 包含各种标准库使用问题的示例和正确用法
 */

// 错误示例1: 缺少必要的头文件
void missing_header_example() {
    // 错误: 使用printf但未包含stdio.h
    printf("Hello World\n");
}

// 正确示例1: 包含必要的头文件
#include <stdio.h>
void correct_header_example() {
    printf("Hello World\n");
}

// 错误示例2: 头文件拼写错误
#include <studio.h>  // 错误: 应该是stdio.h
void misspelled_header_example() {
    printf("This will cause compilation error\n");
}

// 正确示例2: 正确的头文件拼写
#include <stdio.h>
void correct_spelling_example() {
    printf("This will compile correctly\n");
}

// 错误示例3: scanf参数缺少&符号
void scanf_missing_ampersand_example() {
    int x;
    // 错误: scanf参数缺少&符号
    scanf("%d", x);
}

// 正确示例3: scanf参数包含&符号
void scanf_correct_ampersand_example() {
    int x;
    scanf("%d", &x);
    printf("You entered: %d\n", x);
}

// 错误示例4: printf格式字符串与参数不匹配
void printf_format_mismatch_example() {
    int x = 42;
    // 错误: 格式字符串数量与参数数量不匹配
    printf("Value: %d %d\n", x);
}

// 正确示例4: printf格式字符串与参数匹配
void printf_format_match_example() {
    int x = 42;
    printf("Value: %d\n", x);
}

// 错误示例5: 使用malloc但未包含stdlib.h
void malloc_without_header_example() {
    // 错误: 使用malloc但未包含stdlib.h
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        free(ptr);
    }
}

// 正确示例5: 使用malloc并包含stdlib.h
#include <stdlib.h>
void malloc_with_header_example() {
    int *ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        free(ptr);
    }
}

// 错误示例6: 使用字符串函数但未包含string.h
void string_function_without_header_example() {
    char str1[] = "Hello";
    char str2[20];
    // 错误: 使用strcpy但未包含string.h
    strcpy(str2, str1);
    printf("Copied string: %s\n", str2);
}

// 正确示例6: 使用字符串函数并包含string.h
#include <string.h>
void string_function_with_header_example() {
    char str1[] = "Hello";
    char str2[20];
    strcpy(str2, str1);
    printf("Copied string: %s\n", str2);
}

// 错误示例7: 使用数学函数但未包含math.h
void math_function_without_header_example() {
    double x = 3.14;
    // 错误: 使用sin但未包含math.h
    double result = sin(x);
    printf("sin(%f) = %f\n", x, result);
}

// 正确示例7: 使用数学函数并包含math.h
#include <math.h>
void math_function_with_header_example() {
    double x = 3.14;
    double result = sin(x);
    printf("sin(%f) = %f\n", x, result);
}

// 错误示例8: 使用字符函数但未包含ctype.h
void ctype_function_without_header_example() {
    char c = 'A';
    // 错误: 使用isalpha但未包含ctype.h
    if (isalpha(c)) {
        printf("Character is alphabetic\n");
    }
}

// 正确示例8: 使用字符函数并包含ctype.h
#include <ctype.h>
void ctype_function_with_header_example() {
    char c = 'A';
    if (isalpha(c)) {
        printf("Character is alphabetic\n");
    }
}

// 错误示例9: 使用时间函数但未包含time.h
void time_function_without_header_example() {
    // 错误: 使用time但未包含time.h
    time_t current_time = time(NULL);
    printf("Current time: %ld\n", current_time);
}

// 正确示例9: 使用时间函数并包含time.h
#include <time.h>
void time_function_with_header_example() {
    time_t current_time = time(NULL);
    printf("Current time: %ld\n", current_time);
}

// 错误示例10: scanf格式字符串与参数类型不匹配
void scanf_format_mismatch_example() {
    int x;
    // 错误: 格式字符串%d但参数是float类型
    scanf("%d", &x);
    printf("You entered: %d\n", x);
}

// 正确示例10: scanf格式字符串与参数类型匹配
void scanf_format_match_example() {
    int x;
    scanf("%d", &x);
    printf("You entered: %d\n", x);
}

int main() {
    printf("标准库使用测试开始\n");
    
    // 运行各种测试
    correct_header_example();
    correct_spelling_example();
    scanf_correct_ampersand_example();
    printf_format_match_example();
    malloc_with_header_example();
    string_function_with_header_example();
    math_function_with_header_example();
    ctype_function_with_header_example();
    time_function_with_header_example();
    scanf_format_match_example();
    
    printf("标准库使用测试结束\n");
    return 0;
}

/*
 * 标准答案:
 * 1. 第8行: 缺少stdio.h头文件 - 使用printf但未包含stdio.h
 * 2. 第15行: 头文件拼写错误 - studio.h应该是stdio.h
 * 3. 第23行: scanf参数缺少&符号 - x前缺少&符号
 * 4. 第31行: printf格式字符串与参数不匹配 - 格式字符串数量与参数数量不匹配
 * 5. 第39行: 缺少stdlib.h头文件 - 使用malloc但未包含stdlib.h
 * 6. 第49行: 缺少string.h头文件 - 使用strcpy但未包含string.h
 * 7. 第59行: 缺少math.h头文件 - 使用sin但未包含math.h
 * 8. 第69行: 缺少ctype.h头文件 - 使用isalpha但未包含ctype.h
 * 9. 第79行: 缺少time.h头文件 - 使用time但未包含time.h
 * 10. 第89行: scanf格式字符串与参数类型不匹配 - 格式字符串与参数类型不匹配
 */
