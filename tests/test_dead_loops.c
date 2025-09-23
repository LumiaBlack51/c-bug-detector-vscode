#include <stdio.h>
#include <stdlib.h>

// 测试用例1: 明显的死循环 - for(;;)
void test_infinite_for() {
    // BUG: infinite loop - 死循环，无退出条件
    for(;;) {
        printf("infinite loop\n");
    }
}

// 测试用例2: while(1) 死循环
void test_infinite_while() {
    // BUG: infinite loop - 死循环，无退出条件
    while(1) {
        printf("infinite while\n");
    }
}

// 测试用例3: 循环变量永远不会满足退出条件 - i++ 但条件是 i >= 10
void test_never_exit_condition() {
    // BUG: infinite loop - i从10开始，条件是i>=10，但i++永远不会让i<10
    for(int i = 10; i >= 10; i++) {
        printf("i = %d\n", i);
    }
}

// 测试用例4: 循环变量递减但条件错误
void test_wrong_decrement() {
    // BUG: infinite loop - i从0开始，条件是i<10，但i--会让i越来越小，永远不会>=10
    for(int i = 0; i < 10; i--) {
        printf("i = %d\n", i);
    }
}

// 测试用例5: 循环变量步长过大，跳过退出条件
void test_step_too_large() {
    // BUG: infinite loop - i从0开始，每次+3，但条件是i==10，i会变成0,3,6,9,12...永远不等于10
    for(int i = 0; i == 10; i += 3) {
        printf("i = %d\n", i);
    }
}

// 测试用例6: 循环变量步长过小，永远达不到退出条件
void test_step_too_small() {
    // BUG: infinite loop - i从0开始，每次+0.1，但条件是i>=1，由于浮点精度问题可能永远达不到
    for(double i = 0.0; i < 1.0; i += 0.1) {
        printf("i = %f\n", i);
    }
}

// 测试用例7: 正确的循环 - 应该不报错
void test_correct_loop() {
    // 正确：i从0到9，每次+1
    for(int i = 0; i < 10; i++) {
        printf("i = %d\n", i);
    }
}

// 测试用例8: 正确的while循环 - 应该不报错
void test_correct_while() {
    int i = 0;
    while(i < 10) {
        printf("i = %d\n", i);
        i++;
    }
}

// 测试用例9: 有break的while(true) - 应该不报错
void test_while_true_with_break() {
    int count = 0;
    while(true) {
        printf("count = %d\n", count);
        count++;
        if(count >= 5) {
            break; // 有退出条件
        }
    }
}

// 测试用例10: 有return的for(;;) - 应该不报错
void test_for_infinite_with_return() {
    for(;;) {
        printf("infinite with return\n");
        return; // 有退出条件
    }
}

// 测试用例11: 复杂的循环条件 - 可能死循环
void test_complex_condition() {
    int x = 5;
    // BUG: infinite loop - x永远不会改变，条件x > 0永远为真
    while(x > 0) {
        printf("x = %d\n", x);
        // 忘记更新x
    }
}

// 测试用例12: 循环变量在循环体内被修改，但修改错误
void test_modified_in_loop() {
    int i = 0;
    while(i < 10) {
        printf("i = %d\n", i);
        i = i; // BUG: infinite loop - i被赋值为自己，没有实际变化
    }
}

// 测试用例13: 嵌套循环中的死循环
void test_nested_infinite() {
    for(int i = 0; i < 5; i++) {
        // 内层循环是死循环
        for(;;) {
            printf("nested infinite\n");
        }
    }
}

// 测试用例14: 循环条件依赖于外部变量，但外部变量不变
void test_external_dependency() {
    int flag = 1;
    // BUG: infinite loop - flag在循环中从未改变，条件永远为真
    while(flag) {
        printf("flag = %d\n", flag);
        // 忘记修改flag
    }
}

// 测试用例15: 浮点数循环的精度问题
void test_float_precision() {
    // BUG: infinite loop - 由于浮点数精度问题，可能永远达不到1.0
    for(float f = 0.0f; f != 1.0f; f += 0.1f) {
        printf("f = %f\n", f);
    }
}

int main() {
    printf("Testing dead loop detection...\n");
    
    // 只运行一个测试，避免程序真的死循环
    test_correct_loop();
    test_correct_while();
    test_while_true_with_break();
    test_for_infinite_with_return();
    
    return 0;
}
