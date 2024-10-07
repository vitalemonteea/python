
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_unique_words(documents):
    # Step 1: Get all unique words across all documents
    unique_words = set()
    for doc in documents:
        unique_words.update(doc.split())
    return sorted(list(unique_words))

def create_characteristic_matrix(documents, unique_words):
    # Step 2: Create the characteristic matrix
    char_matrix = np.zeros((len(documents), len(unique_words)))
    for i, doc in enumerate(documents):
        for word in doc.split():
            j = unique_words.index(word)
            char_matrix[i, j] = 1
    return char_matrix

def calculate_similarities(char_matrix):
    return cosine_similarity(char_matrix)

def print_results(unique_words, char_matrix, similarities):
    print("Unique words:", unique_words)
    print("\nCharacteristic Matrix:")
    print(char_matrix)
    print("\nPairwise Similarities:")
    print(similarities)
    print("\nPairwise Similarities (readable format):")
    for i in range(len(similarities)):
        for j in range(i+1, len(similarities)):
            print(f"Similarity between D{i+1} and D{j+1}: {similarities[i][j]:.4f}")

def main():
    documents = [
        "big data computing technology useful",
        "data mining technology",
        "data science study of extract insights",
        "big data large amount unstructured structured sources"
    ]

    unique_words = get_unique_words(documents)   #get unique words 
    char_matrix = create_characteristic_matrix(documents, unique_words)#get characteristic matrix
    similarities = calculate_similarities(char_matrix) #get similarities
    print_results(unique_words, char_matrix, similarities)

if __name__ == "__main__":
    main()
