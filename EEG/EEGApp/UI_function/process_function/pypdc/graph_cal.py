import numpy as np
import networkx as nx
from itertools import chain
import statistics

def calculate_graph_metrics(weighted_matrix, is_binary=False):
    """
    计算图论参数，支持加权矩阵和二值矩阵。

    参数:
        weighted_matrix (numpy.ndarray): 加权邻接矩阵。
        is_binary (bool): 是否为二值矩阵，默认为 False。

    返回:
        dict: 包含节点强度、节点度、聚类系数、特征路径长度、局部效率和全局效率的字典。
    """
    # 创建有向图
    G = nx.from_numpy_array(weighted_matrix, create_using=nx.DiGraph)
    
    # 1. Node Strength（节点强度）
    if is_binary:
        # 如果是二值矩阵，节点强度等于节点度
        node_strength = dict(G.degree())
    else:
        # 计算加权节点强度
        node_strength = dict(G.degree(weight='weight'))
    
    # 2. Node Degree（节点度）
    node_degree = dict(G.degree())
    
    # 3. Clustering Coefficient（聚类系数）
    clustering_coefficient = nx.clustering(G.to_undirected())  # 转换为无向图
    
    # 4. Characteristic Path Length（特征路径长度）
    if nx.is_strongly_connected(G):
        characteristic_path_length = nx.average_shortest_path_length(G)
    else:
        # 如果图不连通，计算平均最短路径长度
        path_lengths = (x[1].values() for x in nx.shortest_path_length(G))
        characteristic_path_length = sum(chain.from_iterable(path_lengths)) / sum(len(x[1]) for x in nx.shortest_path_length(G))
    
    # 5. Local Efficiency（局部效率）
    G_undirected = G.to_undirected()
    local_efficiency_list = {}
    for node in G_undirected.nodes():
        neighbors = list(nx.neighbors(G_undirected, node))
        if len(neighbors) > 1:
            subgraph = G_undirected.subgraph(neighbors)
            local_efficiency_list[node] = nx.global_efficiency(subgraph)
        else:
            local_efficiency_list[node] = 0  # 如果节点没有邻居，则局部效率为 0
    
    # 6. Global Efficiency（全局效率）
    global_efficiency = nx.global_efficiency(G_undirected)
    
    # 7. Local Efficiency（局部效率）
    local_efficiency = nx.local_efficiency(G_undirected)
    
    # 返回结果
    return {
        'node_strength': node_strength,
        'node_degree': node_degree,
        'clustering_coefficient': clustering_coefficient,
        'characteristic_path_length': characteristic_path_length,
        'local_efficiency_list': local_efficiency_list,
        'global_efficiency': global_efficiency,
        'local_efficiency': local_efficiency
    }