/*
 * 数值与控制流分析器模块测试用例
 * 包含各种数值溢出和死循环问题的示例和正确用法
 */

#include <stdio.h>

// 错误示例1: char类型溢出
void char_overflow_example() {
    char c;
    // 错误: 赋值超出char范围(-128到127)
    c = 300;
    printf("Value: %d\n", c);
}

// 正确示例1: 使用合适的数据类型
void correct_char_usage_example() {
    int c;
    c = 300;
    printf("Value: %d\n", c);
}

// 错误示例2: unsigned char类型溢出
void unsigned_char_overflow_example() {
    unsigned char uc;
    // 错误: 赋值超出unsigned char范围(0到255)
    uc = 300;
    printf("Value: %d\n", uc);
}

// 正确示例2: 使用合适的数据类型
void correct_unsigned_char_usage_example() {
    unsigned int uc;
    uc = 300;
    printf("Value: %d\n", uc);
}

// 错误示例3: short类型溢出
void short_overflow_example() {
    short s;
    // 错误: 赋值超出short范围(-32768到32767)
    s = 40000;
    printf("Value: %d\n", s);
}

// 正确示例3: 使用合适的数据类型
void correct_short_usage_example() {
    int s;
    s = 40000;
    printf("Value: %d\n", s);
}

// 错误示例4: int类型溢出
void int_overflow_example() {
    int i;
    // 错误: 赋值超出int范围
    i = 3000000000;
    printf("Value: %d\n", i);
}

// 正确示例4: 使用合适的数据类型
void correct_int_usage_example() {
    long long i;
    i = 3000000000;
    printf("Value: %lld\n", i);
}

// 错误示例5: 死循环 - while(1)无退出条件
void infinite_while_loop_example() {
    int count = 0;
    // 错误: 死循环，没有退出条件
    while (1) {
        printf("Count: %d\n", count);
        count++;
        // 没有break或return语句
    }
}

// 正确示例5: 有退出条件的while循环
void correct_while_loop_example() {
    int count = 0;
    while (count < 10) {
        printf("Count: %d\n", count);
        count++;
    }
}

// 错误示例6: 死循环 - while(true)无退出条件
void infinite_while_true_loop_example() {
    int count = 0;
    // 错误: 死循环，没有退出条件
    while (true) {
        printf("Count: %d\n", count);
        count++;
        // 没有break或return语句
    }
}

// 正确示例6: 有break语句的while循环
void correct_while_with_break_example() {
    int count = 0;
    while (true) {
        printf("Count: %d\n", count);
        count++;
        if (count >= 10) {
            break;  // 有退出条件
        }
    }
}

// 错误示例7: 死循环 - for循环条件恒为真
void infinite_for_loop_example() {
    // 错误: for循环条件恒为真，没有退出条件
    for (int i = 0; 1; i++) {
        printf("i: %d\n", i);
        // 没有break或return语句
    }
}

// 正确示例7: 有退出条件的for循环
void correct_for_loop_example() {
    for (int i = 0; i < 10; i++) {
        printf("i: %d\n", i);
    }
}

// 错误示例8: 死循环 - do-while循环无退出条件
void infinite_do_while_loop_example() {
    int count = 0;
    // 错误: do-while循环没有退出条件
    do {
        printf("Count: %d\n", count);
        count++;
        // 没有break或return语句
    } while (1);
}

// 正确示例8: 有退出条件的do-while循环
void correct_do_while_loop_example() {
    int count = 0;
    do {
        printf("Count: %d\n", count);
        count++;
    } while (count < 10);
}

// 错误示例9: 死循环 - while(1)有break但条件永远不满足
void infinite_while_with_unreachable_break_example() {
    int count = 0;
    // 错误: break条件永远不满足
    while (1) {
        printf("Count: %d\n", count);
        count++;
        if (count < 0) {  // 条件永远不满足
            break;
        }
    }
}

// 正确示例9: 有可达break的while循环
void correct_while_with_reachable_break_example() {
    int count = 0;
    while (1) {
        printf("Count: %d\n", count);
        count++;
        if (count >= 10) {  // 条件可以满足
            break;
        }
    }
}

// 错误示例10: 死循环 - for循环有break但条件永远不满足
void infinite_for_with_unreachable_break_example() {
    // 错误: break条件永远不满足
    for (int i = 0; 1; i++) {
        printf("i: %d\n", i);
        if (i < 0) {  // 条件永远不满足
            break;
        }
    }
}

// 正确示例10: 有可达break的for循环
void correct_for_with_reachable_break_example() {
    for (int i = 0; 1; i++) {
        printf("i: %d\n", i);
        if (i >= 10) {  // 条件可以满足
            break;
        }
    }
}

int main() {
    printf("数值与控制流测试开始\n");
    
    // 运行各种测试
    correct_char_usage_example();
    correct_unsigned_char_usage_example();
    correct_short_usage_example();
    correct_int_usage_example();
    correct_while_loop_example();
    correct_while_with_break_example();
    correct_for_loop_example();
    correct_do_while_loop_example();
    correct_while_with_reachable_break_example();
    correct_for_with_reachable_break_example();
    
    printf("数值与控制流测试结束\n");
    return 0;
}

/*
 * 标准答案:
 * 1. 第12行: char类型溢出 - 赋值300超出char范围(-128到127)
 * 2. 第22行: unsigned char类型溢出 - 赋值300超出unsigned char范围(0到255)
 * 3. 第32行: short类型溢出 - 赋值40000超出short范围(-32768到32767)
 * 4. 第42行: int类型溢出 - 赋值3000000000超出int范围
 * 5. 第52行: 死循环 - while(1)无退出条件
 * 6. 第62行: 死循环 - while(true)无退出条件
 * 7. 第72行: 死循环 - for循环条件恒为真
 * 8. 第82行: 死循环 - do-while循环无退出条件
 * 9. 第92行: 死循环 - while(1)有break但条件永远不满足
 * 10. 第102行: 死循环 - for循环有break但条件永远不满足
 */
