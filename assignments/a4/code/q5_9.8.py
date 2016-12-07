import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.cluster import KMeans
from spherecluster import SphericalKMeans

if __name__ == '__main__':
    f, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=True)
    colors = ['#4EACC5', '#FF9C34', '#4E9A06']
    X = np.array([[-4, -2], [-3, -2], [-2, -2], [-1, -2], [1, -1], [1, 1], [2, 3], [3, 2], [3, 4], [4, 3]])
    print('data to cluster =', X, '\n')
    print('executing Kmeans with 3 clusters')
    km = KMeans(n_clusters=3, init='k-means++', n_init=20, max_iter=3000)
    km.fit(X)
    print('executing SphericalKMeans with 3 clusters')
    skm = SphericalKMeans(n_clusters=3, init='k-means++', n_init=20, max_iter=3000)
    skm.fit(X)

    print('plotting the results')
    k_means_cluster_centers = np.sort(km.cluster_centers_, axis=0)
    skm_means_cluster_centers = np.sort(skm.cluster_centers_, axis=0)
    k_means_labels = pairwise_distances_argmin(X, k_means_cluster_centers)
    skm_means_labels = pairwise_distances_argmin(X, skm_means_cluster_centers)

    # KMeans
    for k, col in zip(range(3), colors):
        my_members = k_means_labels == k
        cluster_center = k_means_cluster_centers[k]
        ax1.scatter(X[my_members, 0], X[my_members, 1], marker='+', c=col, s=60)
        ax1.plot(cluster_center[0], cluster_center[1], marker='o', markerfacecolor=col,
                 markeredgecolor='k', markersize=6)
    ax1.set_title('KMeans k=3')
    ax1.set_xticks(())
    ax1.set_yticks(())

    # SphericalKMeans
    for k, col in zip(range(3), colors):
        my_members = skm_means_labels == k
        cluster_center = skm_means_cluster_centers[k]
        ax2.scatter(X[my_members, 0], X[my_members, 1], marker='+', c=col, s=60)
        ax2.plot(cluster_center[0], cluster_center[1], marker='o', markerfacecolor=col,
                 markeredgecolor='k', markersize=6)
    ax2.set_title('SphericalKMeans k=3')
    ax2.set_xticks(())
    ax2.set_yticks(())
    f.savefig('images/kmeans_vs_sphericalkmean.png')
    plt.close(f)
    print('the plot of the results is located at images/kmeans_vs_sphericalkmean.png')
