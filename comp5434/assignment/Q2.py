#Comp5434 assignment1 Q2
# Name: Qian Jincheng
#Decision Tree
import numpy as np

#initialize the dataset
def initializeDataset():
    #一共八组数据，利用前6组数据集作为训练集，后2组数据集作为测试集
    #{sunny, cloudy}-1{rainy}-0
    #temperature hot-1 mild-0 
    #humidity high-1 normal-0
    #play yes-1 no-0
    dataSet = np.array([[1, 1, 1, 0], 
                        [1, 1, 1, 1], 
                        [1, 0, 0, 1], 
                        [0, 0, 1, 1], 
                        [1, 0, 0, 1], 
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [1, 1, 1, 0]])
    labels = ['weather','temperature','humidity']
    testSet = np.array([[0,0,1],[1,1,0]])
    return dataSet,labels,testSet

#calculate the gini index of the dataset
# input: dataSet
# output: giniMatrix
def calculateGini(dataSet, labels):  # 添加 labels 参数
    nFeatures = len(labels)  # 使用当前剩余的特征数量
    giniMatrix = []
    
    for i in range(nFeatures):
        print(f"\n{'='*50}")
        print(f"Feature {i} ({labels[i]}):")
        print(f"{'='*50}")
        
        # 为0的子集计算
        subSet0 = dataSet[dataSet[:,i]==0]
        weight0 = len(subSet0)/len(dataSet)
        
        print(f"\n[Subset where {labels[i]} = 0]")
        print(f"Samples: {len(subSet0)}/{len(dataSet)} (Weight = {weight0:.3f})")
        
        if len(subSet0)>0:
            class_dist0 = {}
            sumPSquared = 0
            for label in [0, 1]:  # 假设类别是0和1
                count = len(subSet0[subSet0[:,-1]==label])
                p = count/len(subSet0) if len(subSet0) > 0 else 0
                class_dist0[label] = (count, p)
                sumPSquared += p*p
            gini0 = 1-sumPSquared
            
            print("Class Distribution:")
            print(f"  Class 0: {class_dist0[0][0]} samples (P = {class_dist0[0][1]:.3f})")
            print(f"  Class 1: {class_dist0[1][0]} samples (P = {class_dist0[1][1]:.3f})")
            print(f"Gini = {gini0:.3f}")
        else:
            gini0 = 0
            print("Empty subset, Gini = 0")

        # 为1的子集计算
        print(f"\n[Subset where {labels[i]} = 1]")
        subSet1 = dataSet[dataSet[:,i]==1]
        weight1 = len(subSet1)/len(dataSet)
        print(f"Samples: {len(subSet1)}/{len(dataSet)} (Weight = {weight1:.3f})")
        
        if len(subSet1)>0:
            class_dist1 = {}
            sumPSquared = 0
            for label in [0, 1]:
                count = len(subSet1[subSet1[:,-1]==label])
                p = count/len(subSet1) if len(subSet1) > 0 else 0
                class_dist1[label] = (count, p)
                sumPSquared += p*p
            gini1 = 1-sumPSquared
            
            print("Class Distribution:")
            print(f"  Class 0: {class_dist1[0][0]} samples (P = {class_dist1[0][1]:.3f})")
            print(f"  Class 1: {class_dist1[1][0]} samples (P = {class_dist1[1][1]:.3f})")
            print(f"Gini = {gini1:.3f}")
        else:
            gini1 = 0
            print("Empty subset, Gini = 0")
            
        weighted_gini = weight0*gini0 + weight1*gini1
        print(f"\n>> Weighted Gini for {labels[i]} = {weighted_gini:.3f}")
        giniMatrix.append(weighted_gini)

    print(f"\n{'='*50}")
    print("Final Gini Values:")
    for i, gini in enumerate(giniMatrix):
        print(f"{labels[i]}: {gini:.3f}")
    print(f"{'='*50}")
    
    return giniMatrix

#构建决策树
def buildDecisionTree(dataSet, labels):
    mostCommonLabel = np.argmax(np.bincount(dataSet[:,-1].astype(int)))
    
    # 1.终止条件
    if len(np.unique(dataSet[:,-1])) == 1:
        return {'class': int(dataSet[0,-1])}
    
    if len(labels) == 0 or dataSet.shape[1] == 1:
        return {'class': int(mostCommonLabel)}

    # 计算每个特征的Gini值 - 修正：传入labels参数
    gini = calculateGini(dataSet, labels)
    minGiniIndex = np.argmin(gini)
    bestFeature = labels[minGiniIndex]
    
    print(f"\nSelected feature with minimum Gini: {bestFeature} (Gini = {gini[minGiniIndex]:.3f})")
    
    # 创建树节点
    tree = {'feature': bestFeature}
    remainingLabels = labels.copy()
    remainingLabels.pop(minGiniIndex)  # 移除已使用的特征标签
    
    # 处理数据集
    for value in [0, 1]:
        subset = dataSet[dataSet[:, minGiniIndex] == value]
        if len(subset) == 0:
            tree[value] = {'class': int(mostCommonLabel)}
        else:
            # 删除已使用的特征列
            subset = np.delete(subset, minGiniIndex, axis=1)
            # 递归构建子树
            tree[value] = buildDecisionTree(subset, remainingLabels)

    return tree

#测试决策树
def testDecisionTree(tree, testSet, labels):
    prediction = []
    for i, test in enumerate(testSet):
        print(f"\nTesting sample {i}: {test}")  # 打印测试样本
        current_tree = tree
        while isinstance(current_tree, dict):
            if 'class' in current_tree:
                print(f"Reached leaf node with class: {current_tree['class']}")
                prediction.append(current_tree['class'])
                break
            
            feature_name = current_tree['feature']
            feature_index = labels.index(feature_name)
            feature_value = int(test[feature_index])
            print(f"Feature: {feature_name}, Value: {feature_value}")  # 打印决策过程
            current_tree = current_tree[feature_value]
            
    return prediction

if __name__ == "__main__":
    dataSet, labels, testSet = initializeDataset()
    tree = buildDecisionTree(dataSet, labels)
    print("\nDecision Tree Structure:")
    print(tree)
    print("\nTesting Process:")
    predictions = testDecisionTree(tree, testSet, labels)
    print("\nFinal Predictions:", predictions)
       
