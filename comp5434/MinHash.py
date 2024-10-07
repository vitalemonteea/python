import numpy as np


def get_matrix():
    #step1  creat fundamental matrix
    matrix=np.array([[0,0,1,1],
                              [1,1,0,0],
                              [0,0,1,0],
                              [1,0,0,1],
                              [1,1,1,0],
                              [1,1,1,1],
                              [0,1,0,0]])

    return matrix

def get_minHashMatrix(matrix):
    #step2 generate the minHash signature matrix
    minHashMatrix=np.zeros((7,4))
    #Make hash changes
    return minHashMatrix

