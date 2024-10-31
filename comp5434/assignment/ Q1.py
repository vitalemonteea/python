#Comp5434 assignment1 Q1
# Name: Qian Jincheng
#Pagerank algorithm

import numpy as np

#构建邻接矩阵
adjacency_matrix =  [
    [0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [0, 0, 0, 0, 1],
    [1, 1, 0, 1, 0]
]

#转移概率矩阵
# 5x5矩阵，行和列的顺序为 A,B,C,D,E
transition_matrix = [
    [0,   1/2,   0,   0,   0  ],  
    [0,   0  ,   1,   1/2, 0  ],  
    [1/2, 0  ,   0,   0,   1/2],  
    [0,   0  ,   0,   0,   1/2],  
    [1/2,1/2 ,   0,   1/2, 0  ]   
]

#pagerank算法
def pagerank(transition_matrix, d=0.85, max_iter=100):
    n = len(transition_matrix)
    #初始化pagerank值
    pagerank_values = np.ones(n) / n
    for _ in range(max_iter):
        #更新pagerank值
        new_pagerank_values = np.ones(n) * (1 - d) / n + d * transition_matrix.T.dot(pagerank_values)
        #判断是否收敛
        if np.allclose(new_pagerank_values, pagerank_values, atol=1e-6):
            break
        pagerank_values = new_pagerank_values
    return pagerank_values
 

#计算pagerank值
pagerank_values = pagerank(transition_matrix)
print("Pagerank Values:" ,pagerank_values)