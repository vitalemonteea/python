import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# Define the dataset
X = np.array([(1, 2), (2, 2), (2, 3), (8, 7), (8, 8), (9, 8), (10, 10), (0, 0), (10, 1)])

# Set DBSCAN parameters
eps = 1.5
min_samples = 3

# Apply DBSCAN
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
labels = dbscan.fit_predict(X)

# Identify core points, border points, and noise points
core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
core_samples_mask[dbscan.core_sample_indices_] = True

# Print results
print("Results:")
for i, point in enumerate(X):
    if core_samples_mask[i]:
        point_type = "Core point"
    elif labels[i] != -1:
        point_type = "Border point"
    else:
        point_type = "Noise point"
    print(f"Point {point}: {point_type}")

# List clusters
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print(f"\nNumber of clusters: {n_clusters}")

for cluster in range(n_clusters):
    cluster_points = X[labels == cluster]
    print(f"Cluster {cluster + 1}: {cluster_points.tolist()}")

print("\nNoise points:", X[labels == -1].tolist())

# Visualize the results
plt.figure(figsize=(10, 8))
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

for label, color in zip(unique_labels, colors):
    if label == -1:
        color = 'k'  # Black for noise points
    
    class_member_mask = (labels == label)
    
    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=color, markeredgecolor='k', markersize=14, label=f'Core (Cluster {label})' if label != -1 else 'Core (Noise)')
    
    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=color, markeredgecolor='k', markersize=6, label=f'Border (Cluster {label})' if label != -1 else 'Border (Noise)')

plt.title('DBSCAN Clustering')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()
