import os
import math
import networkx as nx
import multiprocessing
import numpy as np
import pandas as pd
from itertools import repeat
from sklearn.metrics import pairwise_distances_argmin
from sklearn.cluster import KMeans
from collections import defaultdict
from scipy.spatial.distance import euclidean
from scipy.stats import pearsonr
from util import *

ratings_df_pickle = 'pickled/movie_ratings_df.pickle'
reviewer_sim_pickle = 'pickled/movie_reviewer_sim.pickle'
rating_cluster_pickle = 'pickled/movie_rating_cluster%d.pickle'
movies_df_pickle = 'pickled/movie_movies_df.pickle'


def get_movies_df():
    if not os.path.exists(movies_df_pickle):
        names = ['movie_id', 'movie_title', 'release_date', 'video_release_date', 'IMDb_URL', 'unknown', 'Action',
                 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                 ' Film_Noir ','Horror', 'Musical', 'Mystery', 'Romance', ' Sci_Fi ', 'Thriller', 'War', 'Western']
        mov_df = pd.read_csv('data/ml-100k/u.item', sep='|', names=names, encoding='ISO-8859-1')
        dump_pickle(mov_df, movies_df_pickle)
    else:
        mov_df = read_pickle(movies_df_pickle)
    return mov_df


def get_review_df():
    if not os.path.exists(ratings_df_pickle):
        names = ['user_id', 'item_id', 'rating', 'timestamp']
        rev_df = pd.read_csv('data/ml-100k/u.data', sep='\t', names=names)
        dump_pickle(rev_df, ratings_df_pickle)
    else:
        rev_df = read_pickle(ratings_df_pickle)
    return rev_df


def make_new_combined(u1, u2):
    d = {'user_id_x': u1.user_id, 'item_id': u1.item_id, 'rating_x': u1.rating, 'timestamp_x': u1.timestamp,
         'user_id_y': list(repeat(u2.user_id.index[0], u1.user_id.size)), 'rating_y': list(repeat(0, u1.rating.size)),
         'timestamp_y': u1.timestamp}
    return pd.DataFrame(d)


def pearson(rating_u1, rating_u2):
    length = rating_u1.size
    mean_u1 = np.mean(rating_u1)
    mean_u2 = np.mean(rating_u2)
    numerator = sum([(rating_u1.iat[i] - mean_u1) * (rating_u2.iat[i] - mean_u2) for i in range(length)])
    denominator_u1 = math.sqrt(sum([(rating_u1.iat[i] - mean_u1) ** 2 for i in range(length)]))
    denominator_u2 = math.sqrt(sum([(rating_u2.iat[i] - mean_u2) ** 2 for i in range(length)]))
    if (denominator_u1 * denominator_u2) == 0:
        return 0
    correlation = numerator / (denominator_u1 * denominator_u2)
    return correlation


def sim_for_chunk(d):
    print('processing chunk %d' % d['chunk'])
    rdf = d['rdf']
    urs = d['urs']
    u_sims = {'user': [], 'other_user': [], 'sim_method': [], 'sim': []}
    for c_user in urs:
        cu_reviewed = rdf[rdf.user_id == c_user]
        o_uids = rdf[rdf.user_id != c_user].user_id.sort_values().unique()
        for o_uid in o_uids:
            o_u = rdf[rdf.user_id == o_uid]
            c = pd.merge(cu_reviewed, o_u, how='inner', on=['item_id'])
            if len(c.rating_y) == 0:
                c = make_new_combined(cu_reviewed, o_u)

            u_sims['user'].append(c_user)
            u_sims['other_user'].append(o_uid)
            u_sims['sim_method'].append('pearson_seq')
            u_sims['sim'].append(c.rating_x.corr(c.rating_y, method='pearson'))

            u_sims['user'].append(c_user)
            u_sims['other_user'].append(o_uid)
            u_sims['sim_method'].append('pearson_sci')
            p, _ = pearsonr(c.rating_x, c.rating_y)
            u_sims['sim'].append(p)

            u_sims['user'].append(c_user)
            u_sims['other_user'].append(o_uid)
            u_sims['sim_method'].append('pearson_mine')
            u_sims['sim'].append(pearson(c.rating_x, c.rating_y))

            u_sims['user'].append(c_user)
            u_sims['other_user'].append(o_uid)
            u_sims['sim_method'].append('euclid')
            u_sims['sim'].append(euclidean(c.rating_x, c.rating_y))
    print('finished processing chunk %d' % d['chunk'])
    return u_sims


def get_reviewer_sim(rdf):
    if not os.path.exists(reviewer_sim_pickle):
        users = rdf.user_id.sort_values().unique()
        chunks = []
        temp = []
        chunk_c = 1
        for cur_user in users:
            temp.append(cur_user)
            if len(temp) == 41:
                chunks.append({'chunk': chunk_c, 'rdf': rdf.copy(deep=True), 'urs': list(temp)})
                chunk_c += 1
                temp.clear()

        p = multiprocessing.Pool(4)
        ret = p.map(sim_for_chunk, chunks)
        all_sims = {'user': [], 'other_user': [], 'sim_method': [], 'sim': []}
        for it in ret:
            for k, v in it.items():
                all_sims[k].extend(v)
        all_sims = pd.DataFrame(all_sims)
        dump_pickle(all_sims, reviewer_sim_pickle)
    else:
        all_sims = read_pickle(reviewer_sim_pickle)

    return all_sims


def cluster_reviews(n_clusters=20):
    rev_df = get_review_df()
    if not os.path.exists(rating_cluster_pickle % n_clusters):
        users = rev_df.user_id.unique()
        n_users = users.shape[0]
        items = rev_df.item_id.unique()
        n_items = items.shape[0]
        ratings = np.zeros((n_users, n_items))
        for row in rev_df.itertuples():
            ratings[row[1] - 1, row[2] - 1] = row[3]
        k_means = KMeans(n_clusters=n_clusters, n_init=50, max_iter=3000)
        k_means.fit(ratings)
        k_means_cluster_centers = np.sort(k_means.cluster_centers_, axis=0)
        k_means_labels = pairwise_distances_argmin(ratings, k_means_cluster_centers)
        user_in_cluster = defaultdict(list)
        for cluster in range(n_clusters):
            my_members = k_means_labels == cluster
            if np.count_nonzero(my_members) > 0:
                my_members_idxs = my_members.nonzero()
                for user_idx in np.nditer(my_members_idxs):
                    print('user %d is in cluster %d' % (users[user_idx], cluster + 1))
                    user_in_cluster['user'].append(users[user_idx])
                    user_in_cluster['cluster'].append(cluster + 1)
                print('----------------------------------------')
        user_in_cluster = pd.DataFrame(user_in_cluster)
        dump_pickle(user_in_cluster, rating_cluster_pickle % n_clusters)
    else:
        user_in_cluster = read_pickle(rating_cluster_pickle % n_clusters)
    return rev_df, user_in_cluster
