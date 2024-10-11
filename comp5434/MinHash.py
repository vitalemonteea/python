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
    num_rows,num_cols=matrix.shape
    num_hash_functions=3  
    # define the hash functions
    def h1(x): return (2*x + 1) % 7
    def h2(x): return (3*x + 2) % 7
    def h3(x): return (4*x + 3) % 7

    hash_functions=[h1,h2,h3]

    minHashMatrix = np.full((num_hash_functions,num_cols),np.inf)

    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i,j]==1:
                for k,hash_func in enumerate(hash_functions):
                    minHashMatrix[k,j]=min(minHashMatrix[k,j],hash_func(i)) 
    #Make hash changes
    return minHashMatrix

#calculate the similarity
def calculate_similarity_matrix(minHashMatrix):
    num_hash,col=minHashMatrix.shape
    similarity_matrix=np.zeros((col,col))

    for i in range(col):
        for j in range(i+1,col):
            similarity_matrix[i,j]=np.sum(minHashMatrix[:,i]==minHashMatrix[:,j])/num_hash
            similarity_matrix[j,i]=similarity_matrix[i,j]

    return similarity_matrix


def main():
   import numpy as np

# ... 其他函数保持不变 ...

def main():
   matrix = get_matrix()
   minHashMatrix = get_minHashMatrix(matrix)
   similarity_matrix = calculate_similarity_matrix(minHashMatrix)
   
   print("原始矩阵:")
   print(matrix)
   
   print("\nMinHash 签名矩阵:")
   print(minHashMatrix)
   
   print("\n相似度矩阵:")
   print(similarity_matrix)

if __name__ == "__main__":
    main()



