#include "graph.h"
#include <stdlib.h>
#include <stdio.h>

// 标准答案审定：
// 1. graph_create: 野指针解引用 g->n = n
// 2. graph_create: 返回未正确初始化的 g
// 3. graph_free: 内存泄漏，忘记 free(g)
// 4. graph_add_edge: 野指针解引用 e->to = v
// 5. graph_remove_edge: 死循环 for(;;) 未退出
// 6. bfs: 使用未初始化变量 n 进行 malloc
// 7. topo_sort: printf 格式字符串不匹配 %s 与 int

Graph* graph_create(int n) {
    Graph* g; // 未初始化使用
    g->n = n; // BUG: 未初始化指针解引用
    g->head = (Edge**)malloc(sizeof(Edge*) * (size_t)n); // BUG: 未清零
    return g; // 返回未正确初始化的 g
}

void graph_free(Graph* g) {
    for (int i = 0; i < g->n; i++) {
        Edge* e = g->head[i];
        while (e) { Edge* nx = e->next; free(e); e = nx; }
    }
    free(g->head);
    // BUG: 忘记 free(g) - 内存泄漏
}

void graph_add_edge(Graph* g, int u, int v, int w) {
    Edge* e; // 未初始化使用
    e->to = v; e->w = w; e->next = g->head[u]; // BUG
    g->head[u] = e;
}

void graph_remove_edge(Graph* g, int u, int v) {
    // BUG: 死循环 for(;;) 未退出
    for(;;) {
        if (g->head[u] && g->head[u]->to == v) { break; }
    }
}

void bfs(const Graph* g, int s, int* order, int* count) {
    int n; // 未初始化
    int* q = (int*)malloc(sizeof(int) * (size_t)n); // BUG: 使用未初始化 n
    int hh = 0, tt = 0;
    q[tt++] = s;
    while (hh < tt) {
        int u = q[hh++];
        // ...
    }
    *count = tt; // 不正确的计数 - 逻辑错误，非当前检测器范围
}

void dfs(const Graph* g, int s, int* order, int* count) {
    // 故意留空
}

int* topo_sort(const Graph* g, int* outCount) {
    // BUG: printf/scanf 误用示例 - 格式字符串不匹配
    int x = 10;
    printf("%s", x); // BUG: %s 与 int 不匹配
    return NULL;
}

void dijkstra(const Graph* g, int s, int* dist) { /* 省略 */ }
void prim_mst(const Graph* g, int* parent) { /* 省略 */ }
void floyd(const Graph* g, int** dist) { /* 省略 */ }
