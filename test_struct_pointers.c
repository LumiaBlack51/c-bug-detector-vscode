#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 测试结构体指针和变量声明的识别能力

// 定义测试结构体
struct Point {
    int x;
    int y;
};

struct Node {
    int data;
    struct Node* next;
};

struct Graph {
    int vertices;
    struct Node** adjList;
};

// 测试各种结构体指针声明方式
void test_struct_pointer_declarations() {
    // 测试不同的结构体指针声明语法
    struct Point* p1;           // 标准语法
    struct Point *p2;           // 星号靠近变量名
    struct Point * p3;          // 星号两边都有空格
    struct Point*p4;            // 星号紧贴类型名
    
    // 测试结构体变量声明
    struct Point point1;        // 标准结构体变量
    struct Point point2 = {0};  // 初始化的结构体变量
    
    // 测试数组声明
    struct Point points[10];    // 结构体数组
    struct Point* ptr_array[5]; // 结构体指针数组
    
    // 测试嵌套结构体
    struct Node node1;
    struct Node* node_ptr;
    
    // 测试复杂结构体
    struct Graph graph1;
    struct Graph* graph_ptr;
    
    // 测试typedef结构体（如果支持）
    typedef struct {
        int id;
        char name[50];
    } Student;
    
    Student student1;
    Student* student_ptr;
    
    // 测试未初始化使用 - 应该检测到
    p1->x = 10;        // BUG: wild pointer dereference
    p2->y = 20;        // BUG: wild pointer dereference
    p3->x = 30;        // BUG: wild pointer dereference
    p4->y = 40;        // BUG: wild pointer dereference
    
    // 测试结构体成员访问
    point1.x = 100;    // 正确：访问结构体变量成员
    point1.y = 200;    // 正确：访问结构体变量成员
    
    // 测试数组访问
    points[0].x = 1;   // 正确：访问结构体数组元素
    points[0].y = 2;   // 正确：访问结构体数组元素
    
    // 测试指针数组
    ptr_array[0] = p1; // 将未初始化的指针赋值给数组
    
    // 测试嵌套结构体访问
    node1.data = 42;   // 正确：访问嵌套结构体成员
    node_ptr->data = 43; // BUG: wild pointer dereference
    
    // 测试复杂结构体访问
    graph1.vertices = 5; // 正确：访问复杂结构体成员
    graph_ptr->vertices = 6; // BUG: wild pointer dereference
    
    // 测试typedef结构体访问
    student1.id = 1;   // 正确：访问typedef结构体成员
    student_ptr->id = 2; // BUG: wild pointer dereference
}

// 测试结构体指针的内存分配和释放
void test_struct_memory_management() {
    // 测试malloc分配结构体
    struct Point* p1 = malloc(sizeof(struct Point));
    struct Point* p2 = malloc(sizeof(struct Point));
    struct Node* node1 = malloc(sizeof(struct Node));
    struct Graph* graph1 = malloc(sizeof(struct Graph));
    
    // 测试calloc分配结构体
    struct Point* p3 = calloc(1, sizeof(struct Point));
    struct Point* p4 = calloc(5, sizeof(struct Point)); // 数组
    
    // 测试realloc
    p1 = realloc(p1, sizeof(struct Point) * 2);
    
    // 使用分配的内存
    if (p1) {
        p1->x = 10;
        p1->y = 20;
    }
    
    if (p2) {
        p2->x = 30;
        p2->y = 40;
    }
    
    if (node1) {
        node1->data = 100;
        node1->next = NULL;
    }
    
    if (graph1) {
        graph1->vertices = 5;
        graph1->adjList = NULL;
    }
    
    if (p3) {
        p3->x = 50;
        p3->y = 60;
    }
    
    if (p4) {
        p4[0].x = 70;
        p4[0].y = 80;
    }
    
    // 测试内存泄漏 - 应该检测到
    // 忘记释放 p1, p2, node1, graph1, p3, p4
    
    // 只释放部分内存
    free(p1); // 正确释放
    // 忘记释放其他分配的内存
}

// 测试结构体指针的传递和返回
struct Point* create_point(int x, int y) {
    struct Point* p = malloc(sizeof(struct Point));
    if (p) {
        p->x = x;
        p->y = y;
    }
    return p; // 返回分配的内存，调用者需要释放
}

void use_point(struct Point* p) {
    if (p) {
        printf("Point: (%d, %d)\n", p->x, p->y);
    }
}

void test_struct_pointer_passing() {
    // 测试函数返回的结构体指针
    struct Point* p1 = create_point(1, 2);
    struct Point* p2 = create_point(3, 4);
    
    // 使用返回的指针
    use_point(p1);
    use_point(p2);
    
    // 测试传递未初始化的指针
    struct Point* p3;
    use_point(p3); // BUG: 传递未初始化的指针
    
    // 测试传递NULL指针
    struct Point* p4 = NULL;
    use_point(p4); // 正确：传递NULL指针，函数内部会检查
    
    // 内存泄漏 - 应该检测到
    // 忘记释放 p1, p2
}

// 测试结构体数组和指针数组
void test_struct_arrays() {
    // 测试结构体数组
    struct Point points[5];
    struct Node nodes[3];
    
    // 初始化数组元素
    for (int i = 0; i < 5; i++) {
        points[i].x = i;
        points[i].y = i * 2;
    }
    
    for (int i = 0; i < 3; i++) {
        nodes[i].data = i;
        nodes[i].next = NULL;
    }
    
    // 测试指针数组
    struct Point* ptr_array[5];
    struct Node* node_ptr_array[3];
    
    // 分配内存给指针数组
    for (int i = 0; i < 5; i++) {
        ptr_array[i] = malloc(sizeof(struct Point));
        if (ptr_array[i]) {
            ptr_array[i]->x = i;
            ptr_array[i]->y = i * 2;
        }
    }
    
    for (int i = 0; i < 3; i++) {
        node_ptr_array[i] = malloc(sizeof(struct Node));
        if (node_ptr_array[i]) {
            node_ptr_array[i]->data = i;
            node_ptr_array[i]->next = NULL;
        }
    }
    
    // 使用数组
    printf("Points array:\n");
    for (int i = 0; i < 5; i++) {
        printf("Point %d: (%d, %d)\n", i, points[i].x, points[i].y);
    }
    
    printf("Pointer array:\n");
    for (int i = 0; i < 5; i++) {
        if (ptr_array[i]) {
            printf("Point %d: (%d, %d)\n", i, ptr_array[i]->x, ptr_array[i]->y);
        }
    }
    
    // 内存泄漏 - 应该检测到
    // 忘记释放指针数组中的内存
}

// 测试结构体嵌套和复杂结构
void test_nested_structs() {
    // 定义嵌套结构体
    struct Address {
        char street[50];
        char city[30];
        int zip;
    };
    
    struct Person {
        char name[50];
        int age;
        struct Address address;
        struct Person* spouse;
    };
    
    // 测试嵌套结构体声明
    struct Person person1;
    struct Person* person_ptr;
    struct Address addr1;
    struct Address* addr_ptr;
    
    // 测试嵌套结构体访问
    person1.name[0] = 'J';
    person1.age = 25;
    person1.address.zip = 12345;
    person1.spouse = NULL;
    
    // 测试未初始化的嵌套结构体指针
    person_ptr->age = 30; // BUG: wild pointer dereference
    addr_ptr->zip = 54321; // BUG: wild pointer dereference
    
    // 测试嵌套结构体指针
    person1.spouse = person_ptr; // 将未初始化的指针赋值给成员
    
    // 测试复杂访问
    if (person1.spouse) {
        person1.spouse->age = 28; // 可能解引用NULL指针
    }
}

int main() {
    printf("Testing struct pointer and variable declaration recognition...\n");
    
    test_struct_pointer_declarations();
    test_struct_memory_management();
    test_struct_pointer_passing();
    test_struct_arrays();
    test_nested_structs();
    
    printf("Struct pointer tests completed.\n");
    
    return 0;
}
