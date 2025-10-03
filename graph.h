#ifndef GRAPH_H
#define GRAPH_H

typedef struct Edge {
    int to;
    int w;
    struct Edge* next;
} Edge;

typedef struct Graph {
    int n;
    Edge** head;
} Graph;

Graph* graph_create(int n);
void graph_free(Graph* g);
void graph_add_edge(Graph* g, int u, int v, int w);
void graph_remove_edge(Graph* g, int u, int v);
void bfs(const Graph* g, int s, int* order, int* count);
void dfs(const Graph* g, int s, int* order, int* count);
int* topo_sort(const Graph* g, int* outCount);
void dijkstra(const Graph* g, int s, int* dist);
void prim_mst(const Graph* g, int* parent);
void floyd(const Graph* g, int** dist);

#endif
